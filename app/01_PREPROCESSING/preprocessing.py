import pandas as pd
import numpy
import logging
from pathlib import Path
from Utilities._handle_HLTB import HLTB_handle
from Utilities._handle_IGDB import IGDB_handle

Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(
    filename="logfile.log", filemode="w", format=Log_Format, level=logging.INFO
)

DATA_PATH = str(Path(__file__).parent.parent.parent.absolute()) + str("/DataSet/")


df_steam_user = pd.read_csv(str(DATA_PATH) + "start_steam-200k.csv")
print("==> Chargement dataset DataSet/start_steam-200k.csv | Done")
logging.info("Chargement dataset DataSet/start_steam-200k.csv | Done")
print("---")

df_steam_behavior = df_steam_user.groupby(["user_id", "game_name"], as_index=False)[
    " time_is_play"
].sum()
print("==> GroupBy ID/Games | Done")
logging.info(
    "GroupBy ID/Games | "
    + str(df_steam_behavior.shape)
    + "Nbr user_id in dataset : "
    + str(len(df_steam_behavior["user_id"].value_counts()))
)
print("Behabior DataSet : " + str(df_steam_behavior.shape))
print(
    "Nbr user_id in dataset : " + str(len(df_steam_behavior["user_id"].value_counts()))
)
print("---")

game_list = [
    *set(df_steam_behavior[df_steam_behavior[" time_is_play"] > 5]["game_name"])
]
print("==> Select all games with more than 5hours played | Done")
logging.info(
    "elect all games with more than 5hours played |"
    + "Nbr unique games selected : "
    + str(len(game_list))
)
print("Nbr unique games selected : " + str(len(game_list)))
print("---")

# game_list = game_list[0:30]  # Ligne de test pour limiter le sample

print("==> Wrapping data from How Long To Beat | Start")
handle_hltb = HLTB_handle.HLTB_handle(True, True, True, True)
DF_HLTB = handle_hltb.getDatas(game_list, "HLTB_Preprocessing_wrapped.csv")
logging.info("Wrapping data from How Long To Beat |" + str(DF_HLTB.shape))
print("HLTB DataSet : " + str(DF_HLTB.shape))
print("---")

print("==> Wrapping data from IGDB | Start")
CLIENT_ID = "ta1dkgd2vk4qh2guo13snd55lc94qc"
CLIENT_KEY = "6gbxtkoi7m06o8fc7ic806f4bpew71"
handle_igdb = IGDB_handle.IGDB_handle(CLIENT_ID, CLIENT_KEY)
DF_IGDB = handle_igdb.dataForGames(game_list, "IGDB_Preprocessing_wrapped.csv")
logging.info("Wrapping data from IGDB |" + str(DF_IGDB.shape))
print("IGDB DataSet : " + str(DF_IGDB.shape))
print("---")

df_full_api_datas = pd.merge(
    DF_HLTB, DF_IGDB, right_on="searchingName", left_on="01_game_name", how="left"
)
df_full_api_datas.pop("searchingName")
print("==> Merge of IGDB and HLTB | Done")
logging.info("Merge of IGDB and HLTB |" + str(df_full_api_datas.shape))
df_full_api_datas.to_csv(
    str(Path(__file__).parent.absolute())
    + str("/Utilities/_output_handles/full_api_preprocessing.csv")
)
print("FULL_API DataSet : " + str(df_full_api_datas.shape))

Final_Output = pd.merge(
    df_steam_behavior,
    df_full_api_datas,
    left_on="game_name",
    right_on="01_game_name",
    how="inner",
)
Final_Output.pop("01_game_name")
Final_Output.to_csv("preprosscedDataSet.csv")
print("==> Merge of SteamBehavior and API Data | Done")
print("OUTPUT : " + str(Final_Output.shape))
print("Nbr user_id in dataset : " + str(len(Final_Output["user_id"].value_counts())))
logging.info(
    "Merge of SteamBehavior and API Data |"
    + "OUTPUT : "
    + str(Final_Output.shape)
    + "Nbr user_id in dataset : "
    + str(len(Final_Output["user_id"].value_counts()))
)
