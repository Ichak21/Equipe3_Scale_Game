from igdb.wrapper import IGDBWrapper
from igdb.igdbapi_pb2 import GameResult
from igdb.igdbapi_pb2 import GenreResult
from Levenshtein import distance as lev
from tqdm import tqdm  
from time import sleep 
import numpy as np
import pandas as pd 
import requests

class IGDB_handle:
    EP_GAME = 'games.pb'
    EP_GENRE = 'genres.pb'
    GAME_OUTPUT = ["collection", "follows", "franchise", "game_engines", "genres", "keywords", "name", "rating", "rating_count", "themes"]
    GAME_OUTPUT_DATAFRAME = ["searchingName", "collection", "follows", "franchise", "game_engines", "genre1","genre2","genre3",  "keywords1","keywords2","name", "rating", "rating_count", "themes1", "themes2", "themes3"]
  

    open_wrapper:IGDBWrapper

    def __init__(self,CLIENT_ID:str, CLIENT_KEY:str):
        auth_endpoint = "https://id.twitch.tv/oauth2/token?client_id=" + str(CLIENT_ID) + "&client_secret=" + str(CLIENT_KEY) + "&grant_type=client_credentials"
        access_token = requests.post(auth_endpoint).json()["access_token"]
        self.open_wrapper = IGDBWrapper(CLIENT_ID,access_token)

    def _parseListToSelection(self, field:str, values:list):
        selections=str(field) + '=('
        for value in values:
            if value != values[len(values)-1]:
                if type(value) == str :
                    selections += '"' + str(value) + '", '
                else:
                    selections += str(value) + ', '
            else:
                if type(value) == str :
                    selections += '"' + str(value) + '")'                  
                else:
                    selections += str(value) + ')'
        return selections


    def _request_maker(self, fields:list, selections:str, offset:int, limit:int):
        request='fields '
        for field in fields:
            if field != fields[len(fields)-1]:
                request += str(field) + ', '
            else :
                request += str(field) + '; '
        request += 'offset ' + str(offset) + '; '
        request += 'limit ' + str(limit) + ';'  
        if selections != "":      
            request += ' where ' + selections + ';'
        return request

    def _requesting(self, endpoint:str, fields:list, selection:str, offset:int, limit:int):
        request = self._request_maker(fields,selection,offset,limit)
        return self.open_wrapper.api_request(endpoint, request)

    def _searchBestName(self, searchedName:str, possibility:list):
        index = 0
        min_similarity = 1000
        id_return = 0

        for possibleName in possibility:
            if lev(searchedName, possibleName) < min_similarity:
                min_similarity = lev(searchedName, possibleName)
                id_return = index
                index += 1
            else :
                index +=1
        
        return id_return

    def _dataForGame(self, game_name:str):
        request = self._requesting(
            endpoint = self.EP_GAME,
            fields = self.GAME_OUTPUT, 
            selection = 'name="' + str(game_name) + '"',
            offset = 0,
            limit = 10
        )

        response_handle = GameResult()
        response_handle.ParseFromString(request)

        response_names = []
        for game in response_handle.games:
            response_names.append([game.name,game.id])
        
        row_resultat = []
        if response_names != []:
            selected_id = response_names[self._searchBestName(game_name, response_names)][1]

            request = self._requesting(
                endpoint = self.EP_GAME,
                fields = self.GAME_OUTPUT, 
                selection = "id=" + str(selected_id),
                offset = 0,
                limit = 10
            )

            response_handle = GameResult()
            response_handle.ParseFromString(request)

            for game in response_handle.games:
                row_resultat.append(game_name)
                row_resultat.append(game.collection.id)
                row_resultat.append(game.follows)
                row_resultat.append(game.franchise)

                __temps = []
                for engine in game.game_engines:
                    __temps.append(engine.id)

                if __temps != [] : 
                    row_resultat.append(__temps[0]) 
                else: 
                    row_resultat.append(None)
                
                __temps = []
                for genre in game.genres:
                    __temps.append(genre.id)
                if __temps != [] : 
                    row_resultat.append(__temps[0])
                else:
                    row_resultat.append(None)

                if len(__temps)>1:
                    row_resultat.append(__temps[1])
                else:
                    row_resultat.append(None)

                if len(__temps)>2:
                    row_resultat.append(__temps[2])
                else:
                    row_resultat.append(None)


                __temps = []
                for keyword in game.keywords:
                    __temps.append(keyword)

                if __temps != [] : 
                    row_resultat.append(__temps[0])
                else:
                    row_resultat.append(None)

                if len(__temps)>1:
                    row_resultat.append(__temps[1])
                else:
                    row_resultat.append(None)

                row_resultat.append(game.name)
                row_resultat.append(game.rating)
                row_resultat.append(game.rating_count)

                __temps = []
                for theme in game.themes:
                    __temps.append(theme.id)

                if __temps != [] : 
                    row_resultat.append(__temps[0])
                else:
                    row_resultat.append(None)

                if len(__temps)>1:
                    row_resultat.append(__temps[1])
                else:
                    row_resultat.append(None)

                if len(__temps)>2:
                    row_resultat.append(__temps[2])
                else:
                    row_resultat.append(None)
            
        return row_resultat


    def dataForGames(self, game_list:list):
        data_game=[]
        avancement=1
        for game in game_list:
                print(str(avancement) + '/' + str(len(game_list)))
                data_game.append(self._dataForGame(game))
                avancement = avancement + 1

        outputFrame = pd.DataFrame(data_game, columns=self.GAME_OUTPUT_DATAFRAME)

        return outputFrame

    def dataForGenre(self):
        request = self._requesting(
            endpoint = self.EP_GENRE,
            fields = '*', 
            selection = "",
            offset = 0,
            limit = 500
        )

        response_handle = GenreResult()
        response_handle.ParseFromString(request)

        myresultat = []
        for genre in response_handle.genres:
            myresultat.append([genre.id,genre.name])

        genreFrame = pd.DataFrame(myresultat, columns=["Id","Name"])
        print(genreFrame)




if __name__ == "__main__":
    CLIENT_ID = "ta1dkgd2vk4qh2guo13snd55lc94qc"
    CLIENT_KEY = "6gbxtkoi7m06o8fc7ic806f4bpew71"
    handle = IGDB_handle(CLIENT_ID, CLIENT_KEY)
    handle.dataForGenre()