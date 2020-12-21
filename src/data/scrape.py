import os
import csv
import time
import pickle
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# set all_links.pickle path
fbworkout_headers = ['duration', 'calorie_burn', 'difficulty', 'equipment', 'training_type', 'body_focus', 'youtube_link']
comment_headers = ['username','profile','comment_time']

def get_workout_links(driver, all_links_pickle_path):
    """
    Goes through all free workouts and writes list of workout links to pickle file
    """
    fb_link = "https://www.fitnessblender.com/videos?exclusive%5B%5D=0"
    driver.get(fb_link)

    all_links = []
    for page in range(29):
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "contents"))
        )

        time.sleep(2)
        links = [content.get_attribute('href') for content in driver.find_elements_by_class_name('contents') if content.get_attribute('href') != None]
        all_links.append(links)

        next_btn = driver.find_element_by_class_name('iconfont-arrow-forward')
        next_btn.click()

    with open(all_links_pickle_path, 'wb') as f:
        pickle.dump([i for j in all_links for i in j if i is not None], f)


def get_fbdata(workout_link, driver):
    """
    Scrapes a workout link and returns dictionary of data, where the keys are column names and values are data values
    """
    # load the page
    driver.get(workout_link)
    time.sleep(5)

    # scroll down to load comments
    comments = driver.find_element_by_id("comments")
    driver.execute_script("arguments[0].scrollIntoView();", comments)

    # keep pressing load more button and scrolling down until button doesn't exist
    while True:
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Load More Comments')]")
                    )).click()
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        except Exception as e:
            break

    # get html
    html = driver.page_source
    soup = BeautifulSoup(html, "html5lib")

    # get workout details
    span_details = []
    for span in soup.find_all("span",{"class":"detail-value demi"}):
        if span.find('a'):
            span_details.append(span.find('a').get('href'))
        elif span.find_previous('span').text == 'Difficulty:':
            span_details.append(span.text[0])
        else:
            span_details.append(span.text)

    details_dct = dict(zip([x for x in fbworkout_headers if x!= 'body_focus'], span_details))
    details_dct['body_focus'] = soup.find("span",{"class":"focus demi"}).text

    # scrape youtube info

    # comment scraping
    comments  = soup.find_all("article", {"class":"comment"})
    usernames = []
    comment_times = []
    profiles = []
    for c in comments:
        comment_time = c.find("span", {"class":"comment__time"})
        comment_times.append(comment_time.text[2:].strip())
        usernames.append(comment_time.previous_sibling.strip())

        p = c.find("aside", {"class":"comment__profile-image"})
        if p.find('img'):
            profiles.append(p.find('img')['src'])
        else:
            profiles.append(p.find('span').text.strip())

    comments_df = pd.DataFrame({'username':usernames,
                                'profile': profiles,
                                'comment_time':comment_times,
                                })
    return details_dct, comments_df


def scrape_data(chromedriver_path, all_links_pickle_path, fbworkouts_out_path, comments_out_path):
    """
    Writes data to csv
    """

    # headers
    fbheaders = ['workout_id'] + fbworkout_headers
    cheaders = ['workout_id'] + comment_headers

    # create data folder if it doesn't yet exist
    dirname = os.path.dirname(fbworkouts_out_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # write headers if fbworkouts.csv doesn't yet exist
    if not os.path.isfile(fbworkouts_out_path):
        with open(fbworkouts_out_path, 'w', newline='') as f:
            fbwriter = csv.DictWriter(f, fbheaders)
            fbwriter.writerow({x:x for x in fbheaders})

    # write headers if comments.csv doesn't yet exist
    if not os.path.isfile(comments_out_path):
        with open(comments_out_path, 'w', newline='') as g:
            cwriter = csv.DictWriter(g, cheaders)
            cwriter.writerow({x:x for x in cheaders})

    #driver variable
    driver = webdriver.Chrome(chromedriver_path)

    # scrape all workout links to all_links.pickle if all_links.pickle doesn't yet exist
    if not os.path.isfile(all_links_pickle_path):
        get_workout_links(driver, all_links_pickle_path)

    # get workout links
    with open(all_links_pickle_path, 'rb') as file:
        links = pickle.load(file)

    links = links[:2]

    #write data
    with open(fbworkouts_out_path, 'a', newline='') as f, open(comments_out_path, 'a', newline='', encoding="utf-8") as g:
        fbwriter = csv.DictWriter(f, fbheaders)
        cwriter = csv.DictWriter(g, cheaders)

        #go through each link and write data to both csvs
        for i in range(len(links)):
            l = links[i]

            dct, df  = get_fbdata(l, driver)

            # write details
            dct['workout_id'] = i+1
            fbwriter.writerow(dct)

            # write comments
            df.insert(0, 'movie id', i+1)
            df.to_csv(g, header=False, index=False)
    driver.close()
    return
