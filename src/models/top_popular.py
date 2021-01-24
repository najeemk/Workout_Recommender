import pandas as pd
import numpy as np
from sklearn.metrics import ndcg_score
from sklearn.preprocessing import normalize, MinMaxScaler


def top_popular(df, k=None):
    """
    Takes in user_item_interactions data frame, and output the k most commented
    on workouts and their respective scores (# of comments)
    """
    workout_counts = df.groupby(
        'workout_id').size().sort_values(ascending=False)
    preds = np.array(workout_counts.index)
    scores = np.array(workout_counts.values)

    if k is None:
        return preds, scores
    else:
        return preds[:k], scores[:k]


def get_target_scores(external_indices, scores, dct):
    """
    Helper function to get input of sklearn ncdg:
    Given movie ids and their popularity score, as well as a dictionary mapping
    external ids to LightFM internal ids, return the list of popularity scores
    by LightFM internal id ordering
    """
    internal_indices = [dct[i] for i in external_indices]
    scores_by_internal = np.zeros(len(external_indices))
    scores_by_internal.put(internal_indices, scores)
    return scores_by_internal


def evaluate_top_popular(train_df, test_ui_matrix, item_map, k=None):
    """
    Takes in training/testing data and returns average NDCG
    for top popular reccomender
    """
    mms = MinMaxScaler()
    y_true = test_ui_matrix.toarray()
    external_indices, scores = top_popular(train_df)
    y_score = get_target_scores(external_indices, scores, item_map)
    y_scores = mms.fit_transform([list(y_score)]*(y_true.shape[0]))
    return ndcg_score(y_true, y_scores, k)
