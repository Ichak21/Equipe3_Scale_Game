from igdb.wrapper import IGDBWrapper
from igdb.igdbapi_pb2 import GameResult
from Levenshtein import distance as lev
from tqdm import tqdm  
from time import sleep 
import numpy as np
import pandas as pd 
import requests

class IGDB_handle:
    EP_GAME = 'games.pb'
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
        request += 'limit ' + str(limit) + '; where '        
        request += selections + ';'
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
            # else: 
                # for i in range(0, len(self.GAME_OUTPUT_DATAFRAME)):
                #     row_resultat.append(None)
            
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


if __name__ == "__main__":
    CLIENT_ID = "ta1dkgd2vk4qh2guo13snd55lc94qc"
    CLIENT_KEY = "6gbxtkoi7m06o8fc7ic806f4bpew71"
    handle = IGDB_handle(CLIENT_ID, CLIENT_KEY)
    DF = handle.dataForGames(['Sleeping Dogs',
 'Left 4 Dead',
 'Dragon Age II',
 'Star Trek Online',
 'Bejeweled 2 Deluxe',
 'Saints Row IV',
 'TimeShift',
 'F1 2011',
 'Homeworld Remastered Collection',
 'F1 2012',
 'Age of Empires Online',
 'NBA 2K11',
 'Battlefield 2',
 'Alan Wake',
 'GRID',
 'Pillars of Eternity',
 'Devil May Cry 4',
 'Test Drive Unlimited 2',
 'Section 8',
 'Sacred Gold',
 'Stronghold 3',
 'Split/Second',
 'Euro Truck Simulator 2',
 'Alter Ego',
 'RACE On',
 'Street Fighter X Tekken',
 'Rayman Origins',
 'Supreme Commander 2',
 'The Last Remnant',
 'Blur',
 'Supreme Commander',
 'Dark Void',
 'Praetorians',
 'Darkspore',
 'Clockwork Empires',
 'Venetica',
 'Evil Genius',
 'Imperial Glory',
 'Wildlife Park 3',
 'Tropico 4',
 'Guild Wars Trilogy',
 'Airline Tycoon 2',
 'Railroad Tycoon 3',
 'GT Legends',
 'Crysis',
 'Dead Rising 2',
 'Legendary',
 'Ridge Racer Unbounded',
 'The 7th Guest',
 'Botanicula',
 'Evolve',
 'Jack Keane',
 'Machinarium',
 'Spore',
 '15 Days',
 'NBA 2K16',
 'Deponia',
 'Demigod',
 'Rocket League',
 'Dungeon Defenders',
 'Might & Magic Heroes VI',
 'Stronghold Legends',
 'Rocksmith 2014',
 'Impossible Creatures',
 'Mafia II',
 'Cities in Motion',
 'East India Company',
 'Worldwide Soccer Manager 2009',
 "Mirror's Edge",
 'GRID Autosport',
 'War for the Overworld',
 'Act of Aggression',
 'Mortal Kombat X',
 'Pro Evolution Soccer 2014',
 'Championship Manager 2010',
 "Assassin's Creed III",
 'Defiance',
 'The Crew',
 'F.E.A.R. 3',
 'Football Manager 2014',
 'Majesty 2 Collection',
 'Goodbye Deponia',
 'Alone in the Dark',
 'Fable III',
 'Magicka',
 'Football Manager 2011',
 'Damnation',
 'Just Cause',
 'GTR Evolution',
 'Ghost Pirates of Vooju Island',
 'Metro 2033',
 'Just Cause 3',
 'Company of Heroes',
 "Sid Meier's Civilization V",
 'Captain Morgane and the Golden Turtle',
 'DarkStar One',
 'NBA 2K12',
 'LEGO The Lord of the Rings',
 'Grand Theft Auto IV',
 'Mass Effect',
 'Prey',
 'F1 2010',
 'Mass Effect 2',
 'Wasteland 2',
 'Elven Legacy',
 'Max Payne',
 'Tomb Raider II',
 'RIFT',
 'Take On Helicopters',
 "Sid Meier's Railroads!",
 'Sonic Generations',
 'Overlord II',
 'Saints Row 2',
 'Cities XL 2011',
 "Assassin's Creed II",
 'Peggle Nights',
 'Contrast',
 'Syberia',
 'Oil Rush',
 'Rugby League Team Manager 2015',
 'Sacred 3',
 'Football Manager 2016',
 'Ski Region Simulator',
 'APB Reloaded',
 'A Vampyre Story',
 'X Rebirth',
 'Trials Fusion',
 'Sonic & All-Stars Racing Transformed',
 'Company of Heroes 2',
 'BioShock 2',
 'Call of Juarez',
 'Stronghold Kingdoms',
 'LEGO The Hobbit',
 'Alpha Protocol',
 'Gray Matter',
 'The Evil Within',
 'NBA 2K13',
 'The First Templar',
 'BioShock Infinite',
 'Hospital Tycoon',
 'Bejeweled Twist',
 'DiRT 3',
 'Half-Life 2',
 'DC Universe Online',
 'The Secret World',
 'The Void',
 'Pro Evolution Soccer 2016',
 'Dying Light',
 'Left 4 Dead 2',
 'Emergency 2012',
 'Borderlands',
 'The Testament of Sherlock Holmes',
 'Fallout 3',
 'Men of War',
 'Football Manager 2015',
 'Dawn of Discovery',
 'Farming Simulator 2011',
 'Two Worlds II',
 'Tomb Raider',
 'Dungeon Siege III',
 "Tom Clancy's EndWar",
 'Post Mortem',
 'Dishonored',
 'Anno 2070',
 'Project CARS',
 'Guild Wars',
 'Port Royale 2',
 'Rocksmith',
 'Quake 4',
 'The Cursed Crusade',
 'Knights of Honor',
 'DiRT Rally',
 'Darksiders',
 'The Next BIG Thing',
 'RollerCoaster Tycoon',
 'The Whispered World',
 'Grand Theft Auto III',
 'F.E.A.R. Perseus Mandate',
 'World of Zoo',
 'Breach',
 'Duke Nukem Forever',
 'Hotel Giant 2',
 'Bejeweled 3',
 'Half-Life',
 'The Movies',
 'Homefront',
 'Singularity',
 'The Night of the Rabbit',
 'F1 2014',
 'Euro Truck Simulator',
 'Worms Reloaded',
 'R.U.S.E.',
 'Far Cry',
 'Overlord',
 'GRID 2',
 'Far Cry 3',
 'Lost Horizon',
 "Assassin's Creed",
 "Clive Barker's Jericho",
 'Far Cry 2',
 'Bulletstorm',
 'Trapped Dead',
 'Virtua Tennis 4',
 'Borderlands 2',
 'Street Fighter IV',
 'Crysis 2',
 'Sengoku',
 'Blitzkrieg 2 Anthology',
 "Sid Meier's Civilization IV",
 'Titan Quest',
 'World of Goo',
 'Unreal Tournament 2004',
 "Assassin's Creed Syndicate",
 'Monopoly',
 'World in Conflict',
 'Gothic 3',
 'EVE Online',
 'Lost Planet 3',
 'Trine',
 'LEGO Jurassic World',
 'Football Manager 2012',
 'Torchlight',
 'DiRT',
 'Pro Evolution Soccer 2013',
 'TERA',
 'Darksiders II',
 'Mini Ninjas',
 'Off-Road Drive',
 'Far Cry 4',
 'Ship Simulator Extremes',
 'F1 Race Stars',
 'Front Mission Evolved',
 'Just Cause 2',
 'Anno 2205',
 'Still Life 2',
 'Braid',
 'Dead Space',
 'Remember Me',
 'Football Manager 2013',
 'The Darkness II',
 'Spore Galactic Adventures',
 '4 Elements',
 'Order of War',
 'Lost Planet 2',
 'Terraria',
 'Trine 2',
 'Hearts of Iron III',
 'Lara Croft and the Temple of Osiris',
 'Football Manager 2010',
 'Fallout 4',
 'Call of Duty 2',
 'Grand Theft Auto V',
 'F1 2015',
 'Wolfenstein',
 'The Binding of Isaac',
 'Risen',
 'BioShock',
 'Dead Space 2',
 'Cities XL 2012',
 'The Book of Unwritten Tales',
 'Farming Simulator 2013',
 'Dead Island',
 'DiRT 2',
 'Max Payne 3',
 'Sniper Elite',
 'Silent Hunter III',
 'Tropico 5',
 'The Inner World',
 'Pro Evolution Soccer 2015',
 'Portal 2',
 'The Longest Journey',
 'Stormrise',
 'Indigo Prophecy',
 'Mount & Blade',
 'Mafia'])  
DF.to_csv("exportIGDB.csv")  
print(DF)


    
