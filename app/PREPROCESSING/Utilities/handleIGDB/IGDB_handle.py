from igdb.wrapper import IGDBWrapper
from igdb.igdbapi_pb2 import GameResult
from igdb.igdbapi_pb2 import GenreResult
from igdb.igdbapi_pb2 import KeywordResult
from igdb.igdbapi_pb2 import ThemeResult
from igdb.igdbapi_pb2 import GameEngineResult
from igdb.igdbapi_pb2 import CollectionResult
from Levenshtein import distance as lev
import random
from tqdm import tqdm
import numpy as np
import pandas as pd
import requests
from pathlib import Path


class IGDB_handle:
    PATH = str(Path(__file__).parent.parent.absolute()) + str("/_output_handles/")
    EP_GAME = "games.pb"
    EP_GENRE = "genres.pb"
    EP_KEYWORD = "keywords.pb"
    EP_THEME = "themes.pb"
    EP_ENGINE = "game_engines.pb"
    EP_LOCALIZATION = "game_localizations.pb"
    EP_COLLECTION = "collections.pb"
    GAME_OUTPUT = [
        "collection",
        "follows",
        "franchise",
        "game_engines",
        "genres",
        "keywords",
        "name",
        "rating",
        "rating_count",
        "themes",
    ]
    GAME_OUTPUT_DATAFRAME = [
        "searchingName",
        "collection",
        "follows",
        "game_engines",
        "genre1",
        "genre2",
        "genre3",
        "keywords1",
        "keywords2",
        "keywords3",
        "keywords4",
        "keywords5",
        "name",
        "rating",
        "rating_count",
        "themes1",
        "themes2",
        "themes3",
        "themes4",
        "themes5",
    ]

    open_wrapper: IGDBWrapper

    def __init__(self, CLIENT_ID: str, CLIENT_KEY: str):
        auth_endpoint = (
            "https://id.twitch.tv/oauth2/token?client_id="
            + str(CLIENT_ID)
            + "&client_secret="
            + str(CLIENT_KEY)
            + "&grant_type=client_credentials"
        )
        access_token = requests.post(auth_endpoint).json()["access_token"]
        self.open_wrapper = IGDBWrapper(CLIENT_ID, access_token)

    def _request_maker(self, fields: list, selections: str, offset: int, limit: int):
        request = "fields "
        for field in fields:
            if field != fields[len(fields) - 1]:
                request += str(field) + ", "
            else:
                request += str(field) + "; "
        request += "offset " + str(offset) + "; "
        request += "limit " + str(limit) + ";"
        if selections != "":
            request += " where " + selections + ";"
        return request

    def _requesting(
        self, endpoint: str, fields: list, selection: str, offset: int, limit: int
    ):
        request = self._request_maker(fields, selection, offset, limit)
        return self.open_wrapper.api_request(endpoint, request)

    def _parseListToSelection(self, field: str, values: list):
        selections = str(field) + "=("
        for value in values:
            if value != values[len(values) - 1]:
                if type(value) == str:
                    selections += '"' + str(value) + '", '
                else:
                    selections += str(value) + ", "
            else:
                if type(value) == str:
                    selections += '"' + str(value) + '")'
                else:
                    selections += str(value) + ")"
        return selections

    def _searchBestName(self, searchedName: str, possibility: list):
        index = 0
        min_similarity = 1000
        id_return = 0

        for possibleName in possibility:
            if lev(searchedName, possibleName) < min_similarity:
                min_similarity = lev(searchedName, possibleName)
                id_return = index
                index += 1
            else:
                index += 1

        return id_return

    def _dataByIdForGenre(self, id: int):
        request = self._requesting(
            endpoint=self.EP_GENRE,
            fields="*",
            selection="id=" + str(id),
            offset=0,
            limit=1,
        )

        response_handle = GenreResult()
        response_handle.ParseFromString(request)

        for genre in response_handle.genres:
            return genre.name

    def _dataByIdForTheme(self, id: int):
        request = self._requesting(
            endpoint=self.EP_THEME,
            fields="*",
            selection="id=" + str(id),
            offset=0,
            limit=1,
        )

        response_handle = ThemeResult()
        response_handle.ParseFromString(request)

        for theme in response_handle.themes:
            return theme.name

    def _dataByIdForKeywords(self, id: int):
        request = self._requesting(
            endpoint=self.EP_KEYWORD,
            fields="*",
            selection="id=" + str(id),
            offset=0,
            limit=1,
        )

        response_handle = KeywordResult()
        response_handle.ParseFromString(request)

        for keyword in response_handle.keywords:
            return keyword.name

    def _dateByIdForEngine(self, id: int):
        request = self._requesting(
            endpoint=self.EP_ENGINE,
            fields="*",
            selection="id=" + str(id),
            offset=0,
            limit=1,
        )

        response_handle = GameEngineResult()
        response_handle.ParseFromString(request)

        for engine in response_handle.gameengines:
            return engine.name

    def _databyIdCollection(self, id: int):
        request = self._requesting(
            endpoint=self.EP_COLLECTION,
            fields="*",
            selection="id=" + str(id),
            offset=0,
            limit=1,
        )

        response_handle = CollectionResult()
        response_handle.ParseFromString(request)

        for collection in response_handle.collections:
            return collection.name

    def _dataForGame(self, game_name: str):
        request = self._requesting(
            endpoint=self.EP_GAME,
            fields=self.GAME_OUTPUT,
            selection='name="' + str(game_name) + '"',
            offset=0,
            limit=10,
        )

        response_handle = GameResult()
        response_handle.ParseFromString(request)

        response_names = []
        for game in response_handle.games:
            response_names.append([game.name, game.id])

        row_resultat = []
        if response_names != []:
            selected_id = response_names[
                self._searchBestName(game_name, response_names)
            ][1]

            request = self._requesting(
                endpoint=self.EP_GAME,
                fields=self.GAME_OUTPUT,
                selection="id=" + str(selected_id),
                offset=0,
                limit=10,
            )

            response_handle = GameResult()
            response_handle.ParseFromString(request)

            for game in response_handle.games:
                row_resultat.append(game_name)
                row_resultat.append(self._databyIdCollection(game.collection.id))
                row_resultat.append(game.follows)

                __temps = []
                for engine in game.game_engines:
                    __temps.append(self._dateByIdForEngine(engine.id))

                if __temps != []:
                    row_resultat.append(__temps[0])
                else:
                    row_resultat.append(None)

                __temps = []
                for genre in game.genres:
                    __temps.append(genre.id)
                if __temps != []:
                    row_resultat.append(self._dataByIdForGenre(__temps[0]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 1:
                    row_resultat.append(self._dataByIdForGenre(__temps[1]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 2:
                    row_resultat.append(self._dataByIdForGenre(__temps[2]))
                else:
                    row_resultat.append(None)

                __temps = []
                for keyword in game.keywords:
                    __temps.append(keyword.id)

                if __temps != []:
                    row_resultat.append(self._dataByIdForKeywords(__temps[0]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 1:
                    row_resultat.append(self._dataByIdForKeywords(__temps[1]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 2:
                    row_resultat.append(self._dataByIdForKeywords(__temps[2]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 3:
                    row_resultat.append(self._dataByIdForKeywords(__temps[3]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 4:
                    row_resultat.append(self._dataByIdForKeywords(__temps[4]))
                else:
                    row_resultat.append(None)

                row_resultat.append(game.name)
                row_resultat.append(game.rating)
                row_resultat.append(game.rating_count)

                __temps = []
                for theme in game.themes:
                    __temps.append(theme.id)

                if __temps != []:
                    row_resultat.append(self._dataByIdForTheme(__temps[0]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 1:
                    row_resultat.append(self._dataByIdForTheme(__temps[0]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 2:
                    row_resultat.append(self._dataByIdForTheme(__temps[2]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 3:
                    row_resultat.append(self._dataByIdForTheme(__temps[3]))
                else:
                    row_resultat.append(None)

                if len(__temps) > 4:
                    row_resultat.append(self._dataByIdForTheme(__temps[4]))
                else:
                    row_resultat.append(None)

        return row_resultat

    def dataForGames(self, game_list: list, file_name: str = None):
        data_game = []
        for game in tqdm(game_list, desc="IGDB Wrapping ", colour="red"):
            data_game.append(self._dataForGame(game))

        outputFrame = pd.DataFrame(data_game, columns=self.GAME_OUTPUT_DATAFRAME)

        if file_name != None:
            outputFrame.to_csv(str(self.PATH) + str(file_name), index=False)
        return outputFrame

    def searchByGenre(self, genre_str: str, top: int):
        genres = self.dataForGenre()
        rand = random.randint(0, 10)

        if genre_str not in genres.genre.values:
            return "Le genre n'exite pas !"

        genre_id = genres[genres["genre"] == genre_str]["id"].values[0]

        request = self._requesting(
            endpoint=self.EP_GAME,
            fields=["name"],
            selection="genres=" + str(genre_id) + " & aggregated_rating>=75 & hypes>=0",
            offset=rand,
            limit=10,
        )

        response_handle = GameResult()
        response_handle.ParseFromString(request)

        myresultat = []
        for game in response_handle.games:
            myresultat.append(game.name)

        if myresultat == []:
            request = self._requesting(
                endpoint=self.EP_GAME,
                fields=["name"],
                selection="genres="
                + str(genre_id)
                + " & aggregated_rating>=0 & hypes>=0",
                offset=rand,
                limit=10,
            )

        response_handle = GameResult()
        response_handle.ParseFromString(request)

        myresultat = []
        for game in response_handle.games:
            myresultat.append(game.name)

        if myresultat == []:
            request = self._requesting(
                endpoint=self.EP_GAME,
                fields=["name"],
                selection="genres=" + str(genre_id) + " & aggregated_rating>=0",
                offset=rand,
                limit=10,
            )

        response_handle = GameResult()
        response_handle.ParseFromString(request)

        myresultat = []
        for game in response_handle.games:
            myresultat.append(game.name)

        return myresultat[:top]

    def dataForGenre(self):
        request = self._requesting(
            endpoint=self.EP_GENRE, fields="*", selection="", offset=0, limit=500
        )

        response_handle = GenreResult()
        response_handle.ParseFromString(request)

        myresultat = []
        for genre in response_handle.genres:
            myresultat.append([genre.id, genre.name])

        genreFrame = pd.DataFrame(myresultat, columns=["id", "genre"])

        return genreFrame


if __name__ == "__main__":
    CLIENT_ID = "ta1dkgd2vk4qh2guo13snd55lc94qc"
    CLIENT_KEY = "6gbxtkoi7m06o8fc7ic806f4bpew71"
    handle = IGDB_handle(CLIENT_ID, CLIENT_KEY)
    print(handle.searchByGenre("Role-playing (RPG)", 3))
    print(handle.searchByGenre("Role-playing (RPG)", 3))
    print(handle.searchByGenre("Role-playing (RPG)", 3))
    print(handle.searchByGenre("Shooter", 3))
    print(handle.searchByGenre("Shooter", 3))
    print(handle.searchByGenre("Shooter", 3))
    print(handle.searchByGenre("Simulator", 3))
    print(handle.searchByGenre("Simulator", 3))
    print(handle.searchByGenre("Simulator", 3))
    print(handle.searchByGenre("Racing", 3))
    print(handle.searchByGenre("Racing", 3))
    print(handle.searchByGenre("Racing", 3))
    print(handle.searchByGenre("Real Time Strategy (RTS)", 3))
    print(handle.searchByGenre("Real Time Strategy (RTS)", 3))
    print(handle.searchByGenre("Real Time Strategy (RTS)", 3))
    # TEST = handle.dataForGames(
    #     [
    #         "Rocksmith",
    #         "Devil May Cry 4",
    #         "Lost Horizon",
    #         "Borderlands",
    #         "Homeworld Remastered Collection",
    #         "NBA 2K11",
    #         "Street Fighter X Tekken",
    #         "F.E.A.R. 3",
    #         "Worms Reloaded",
    #     ],
    #     "text.csv",
    # )
    # print(TEST[["keywords1", "keywords2", "keywords3", "keywords4", "keywords5"]])
    # print(TEST[["genre1", "genre2", "genre3"]])
    # print(TEST[["themes1", "themes2", "themes3", "themes4", "themes5"]])
    # print(TEST)
