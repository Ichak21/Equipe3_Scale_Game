# Bring in lightweight dependecies
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
from typing import List
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from userApiHelper import make_predictions, find_mean_rating, make_model
from app.PREPROCESSING.Utilities.handleIGDB.IGDB_handle import IGDB_handle

# import importlib
# foobar = importlib.import_module("app.PREPROCESSING.Utilities.handle_IGDB.IGDB_handle")


app = FastAPI()

df = pd.read_csv("../../../DataSet/surprise.csv")
df_unique_games = df.game_name.unique()

svd = make_model(df)

class User_2(BaseModel):
    genre : str
    nb_top_games : int

class User_3(BaseModel):
    games : List[str]
    nb_top_games : int
    

class User_4(BaseModel):
    user_id : int
    nb_top_games : int



@app.get('/')
async def test(msg:str):
    return {"message ":"test"}

@app.post('/adduserprediction')
async def add_user_prediction(user:User_3):
    global df,svd
    for game in user.games:
        if game not in df_unique_games:
           raise HTTPException(status_code = 404, detail = f'{game} n\'existe pas')
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


@app.post('/getuserprediction')
async def get_user_prediction(user:User_4):
    global df,svd
    
    if  user.user_id not in df.user_id.values:
        raise HTTPException(status_code = 404, detail = f'{user.user_id} n\'existe pas')
    
    result = make_predictions(svd,df,df_unique_games,user.user_id, user.nb_top_games)
   
    return result.to_dict()



@app.post('/getpredictionbygenre')
async def get_prediction_by_genre(user:User_2):
    global df,svd
    
    # if  user.genre not in df.user_id.values:
    #     raise HTTPException(status_code = 404, detail = f'{user.user_id} n\'existe pas')
    
    result = make_predictions(svd,df,df_unique_games,user.user_id, user.nb_top_games)
   
    return result.to_dict()