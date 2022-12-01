# Bring in lightweight dependecies
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
from typing import List
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from userApiHelper import make_predictions, find_mean_rating, make_model, content_based_prediction
from app.PREPROCESSING.Utilities.handleIGDB.IGDB_handle import IGDB_handle

# import importlib
# foobar = importlib.import_module("app.PREPROCESSING.Utilities.handle_IGDB.IGDB_handle")


app = FastAPI()

CLIENT_ID = "ta1dkgd2vk4qh2guo13snd55lc94qc"
CLIENT_KEY = "6gbxtkoi7m06o8fc7ic806f4bpew71"

df = pd.read_csv("./DataSet/surprise.csv")
df_unique_games = df.game_name.unique()

svd = make_model(df)

content_based_matrix = pd.read_csv('./DataSet/content-based.csv', index_col="01_game_name")

class User_2(BaseModel):
    genre : str
    nb_top_games : int

class User_3(BaseModel):
    games : List[str]
    nb_top_games : int
    

class User_4(BaseModel):
    user_id : int
    nb_top_games : int
    
class User_5(BaseModel):
    game : str
    nb_top_games : int



@app.get('/')
async def test(msg:str):
    return {"message ":"test"}

@app.post('/predictionByGameList')
async def add_user_prediction(user:User_3):
    global df,svd
    for game in user.games:
        if game not in df_unique_games:
           raise HTTPException(status_code = 404, detail = f"{game} n'existe pas")
    new_user_id = df.user_id.max() + 1
    
    df_new_user = pd.DataFrame(data=user.games, columns= ['game_name'])
    df_new_user['user_id'] = new_user_id
    
    df_new_user['raw_ratings'] = df_new_user.apply(lambda x : find_mean_rating(x.game_name,df),axis=1)
    
    print(f'before : {df.shape}')
    df = df.append(df_new_user)
    print(f'after : {df.shape}')
    
    svd = make_model(df)
    
    result = make_predictions(svd,df,df_unique_games,new_user_id, user.nb_top_games)
   
    return result.to_dict()


@app.post('/predictionByUserId')
async def get_user_prediction(user:User_4):
    global df,svd
    
    if  user.user_id not in df.user_id.values:
        raise HTTPException(status_code = 404, detail = f"{user.user_id} n'existe pas")
    
    result = make_predictions(svd,df,df_unique_games,user.user_id, user.nb_top_games)
   
    return result.to_dict()



@app.post('/predictionByGenre')
async def get_prediction_by_genre(user:User_2):
    handle = IGDB_handle(CLIENT_ID, CLIENT_KEY)
    
    return handle.searchByGenre(user.genre,user.nb_top_games)
    

@app.post('/predictionGeneral')
async def get_prediction_general():
    df2 = pd.read_csv("app/PREPROCESSING/Utilities/_output_handles/popular_api_preprocessing.csv")
    df_top = df2.loc[df2['17_review_score'] >= 75.0].sort_values(by=["15_count_playing"], ascending=False).head(10)

    return df_top[['01_game_name','17_review_score','15_count_playing']].to_dict()
    
@app.post('/predictionByGame')
async def get_prediction_by_game(user: User_5):
    if user.game not in content_based_matrix.index:
        raise HTTPException(status_code = 404, detail = f'{user.game} n\'existe pas')

    res = content_based_prediction(content_based_matrix, user.game, user.nb_top_games)
    return res.to_dict()