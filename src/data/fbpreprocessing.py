import pandas as pd
import numpy as np
import os

def clean_fbworkouts(fbworkouts_path):
    """
    Takes in fbworkouts.csv and outputs fbworkouts_clean.csv
    """
    # reads workouts_df
    workouts_df = pd.read_csv(fbworkouts_path)

    # extracts the minutes from the column
    duration = workouts_df.duration.str.split().apply(lambda x: x[0] if x[1] == 'Minutes' else x)
    workouts_df.duration = duration.astype(int)

    def strip_special_chars_and_split(df, col):
        stripped_column = df[col].str.replace('[^a-zA-Z0-9/, ]', '', regex=True)
        df[col] = stripped_column.str.split(', ')
        return df

    # strip special characters from body_focus and convert to list with {'UpperBody', 'TotalBody', 'LowerBody', 'Core'}
    strip_special_chars_and_split(workouts_df, 'body_focus')
    strip_special_chars_and_split(workouts_df, 'training_type')
    strip_special_chars_and_split(workouts_df, 'equipment')

    ## check to see that 
    #flatten = lambda t: [item for sublist in t for item in sublist]
    #assert set(flatten(workouts_df.body_focus.tolist())) == {'UpperBody', 'TotalBody', 'LowerBody', 'Core'}
    #assert set(flatten(workouts_df.training_type.tolist())) == {'Pilates', 'Plyometric', 
    #    'Toning', 'Kettlebell', 'Barre', 'Low Impact', 'Strength Training', 'Cardiovascular', 
    #    'Warm UpCool Down', 'StretchingFlexibility', 'BalanceAgility', 'HIIT'}
    #assert set(flatten(workouts_df.equipment.tolist())) == {'Bench', 'PhysioBall', 'Kettlebell', 'Mat', 
    #    'Aerobics Step', 'No Equipment', 'Exercise Band', 'Sandbag', 
    #    'Barbell', 'Dumbbell', 'Stationary Bike', 'Jump Rope', 'Medicine Ball'}

    # OHE Encoder Function
    def OHEListEncoder(df, col, drop=True):
        """
        Given a dataframe and a column, return a OHE encoding of the column
        df: pandas dataframe
        col: str, name of the column to encode
        drop: Boolean, drops column from dataframe (default = True)
        """
        expanded_col = df[col].explode()
        if drop: df = df.drop([col], axis=1)
        return df.join(pd.crosstab(expanded_col.index, expanded_col))


    workouts_df = OHEListEncoder(workouts_df, 'body_focus')
    workouts_df = OHEListEncoder(workouts_df, 'training_type')
    # there is both a workout type and equipment named kettlebell, meaning that there will be overlap
    # therefore, we dropped the kettlebell from the "training_type", since you won't be doing
    # kettlebell exercises without the kettlebell; kettlebell will be encoded in the equipment section
    workouts_df = workouts_df.drop(['Kettlebell'], axis=1) 
    workouts_df = OHEListEncoder(workouts_df, 'equipment')

    print(workouts_df.columns)
    print(workouts_df.head())
    return

def create_fbcommenters(comments_path, fbcommenters_path):
    """
    Takes in comments.csv and outputs fbcommenters.csv, which assigns id to each
    hash_id-profile combination
    """
    comments_df = pd.read_csv(comments_path, usecols=['hash_id'])
    comments_df = comments_df.drop_duplicates()
    comments_df['user_id'] = np.arange(1, comments_df.shape[0] + 1)

    dirname = os.path.dirname(comments_path)
    comments_df.to_csv(fbcommenters_path, index=False)

def fb_preprocessing(fbworkouts_path, comments_path, fbcommenters_path):
    clean_fbworkouts(fbworkouts_path)
    create_fbcommenters(comments_path, fbcommenters_path)
