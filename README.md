## Workout Recommender

A workout video recommender web application.

Authors: Amanda Shu, Peter Peng, Najeem Kanishka

### Data
The data is scraped from https://www.fitnessblender.com/. We are using the data for academic purposes only.

### Code Organization

- `run.py`: Run to get data and model results.
- `app.py`: Runs flask web application.
- `workout_db.sql`: Contains sql statements for creation of tables in database.

**Source**
- The `src/data` folder contains `scrape.py`, the web-scraping script that writes three data files into `data/raw` folder. `fbpreprocessing.py` takes these raw data files and outputs cleaned/transformed data files into `data/preprocessed` folder. `youtube.py` grabs youtube related data from the Youtube API. `model_preprocessing` reads in preprocessed data and transforms the data into what is needed for model inputs.
- `src/models` contains `run_models.py` which trains and evaluates the models. Models are implemented in `lightm_fm.py` and `top_popular.py`
- The `src/utils` folder has `clean.py` which implements the standard target `clean`.
- The `src/app` folder holds files for the web application. `forms.py` contains wtforms classes for registration/login pages. `recommendations.py` holds code for filtering user preferences and building recommendation lists. `register.py` contains a helper function to create the sql insertion statement for registering users.

**Config**: `data-params.json` has file paths outputs for data collection/preprocessing. To webscrape, this folder should also include `chromedriver.json`. To gather Youtube data, `api_key.json` specifies the api key. To run the app, `db_config.json` has the database configurations.

**Notebook**: `eda.ipynb` is a notebook with exploratory data analysis on scraped data. `models.ipynb` is a notebook reporting the recommendation models' performance across various parameters.

**Static**: Several css and javascript files for styling/theming of website.

**Templates**: Holds html files for the various endpoints.

### Set Up Project Environment
There are two ways to run this project: 1) Docker (preferred) or 2) Locally
1) To run in Docker:
  a) Pull the container with `docker pull nkanishka/workout-recommender`
  b) Run the container using:
    * General Use: `docker run -it -p 5000:5000 workout_recommender`
    * DSMLP Only: `launch-scipy-ml.sh -i nkanishka/workout_recommender_dsmlp -P Always` 

### Run the Project Stages
- To get the data, run `python run.py data`. This scrapes the data and cleans the data and saves these files into `/data/raw` and `data/preprocessed` respectively.
  - Note: for scraping, this assumes that there is a file `config/chromedriver.json` that specifies where the path to the downloaded chromedriver.exe file for your Chrome version lies in the attribute `chromedriver_path`.
  - Note: for making requests to Youtube API, this assumes that there is a file `config/api_key.json` that specifies the api key in the `api_key` attribute.
- To run model results, run `python run.py model`. This takes in the preprocessed data, trains the models, and prints out the NDCG scores for each model.
- Standard target `clean` is implemented, and it will delete the `data` folder.
- Standard target `all` is implemented, and it equivalent to running `python run.py data model`.
- Standard target `test` is implemented, and it scrapes two workouts links, and runs the rest of the data preprocessing/modeling on that data. The purpose of this target is purely to check the implementation of the code.
- Use `python app.py` to run the app locally.
  - Note: this assumes that there is a file `config/db_config.json`, which has database host, user, password, and name information.
