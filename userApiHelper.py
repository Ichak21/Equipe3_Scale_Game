import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from sklearn.metrics.pairwise import cosine_similarity

def make_predictions(model, df: pd.DataFrame,df_unique_games, user_id, top_x = None):
    played_games = set(df[df["user_id"] == user_id]["game_name"].unique())
    relevant_games = set(df_unique_games).difference(played_games)
    res = []
    for game in relevant_games:
        res.append((game, model.predict(user_id, game).est))
    res = pd.DataFrame(data=res, columns = ["game_name", "ranking"]).sort_values(by="ranking", ascending=False)
    if(top_x):
        res = res.iloc[:top_x]
    return res


def find_mean_rating(game, df):
    return df[df["game_name"] == game]["raw_ratings"].mean()

def make_model(data : pd.DataFrame):
    reader = Reader(rating_scale=(0, 100))
    data = Dataset.load_from_df(data[['user_id', 'game_name', 'raw_ratings']], reader)
    
    data = data.build_full_trainset()
    
    # Model Training
    svd = SVD(random_state=42)
    svd.fit(data)
    
    return svd

def content_based_prediction(matrix: pd.DataFrame, game: str, top_x = None):
    similarities = matrix[game]
    similarities = similarities.sort_values(ascending=False)
    similarities = similarities.drop(game)
    if top_x:
        similarities = similarities.iloc[:top_x]
    return similarities