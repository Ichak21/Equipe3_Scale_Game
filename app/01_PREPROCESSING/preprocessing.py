import pandas as pd
from Utilities._handle_HLTB import HLTB_handle
from Utilities._handle_IGDB import IGDB_handle


df_steam_user = pd.read_csv("../../DataSet/start_steam-200k.csv")
df_vg_sales = pd.read_csv("../../DataSet/start_vgsales.csv")
sets_platform = pd.read_csv("../../DataSet/platform_settings.csv")

df_vg_sales = df_vg_sales[df_vg_sales["Platform"] == "PC"]
print(df_steam_user.shape)
print(df_vg_sales.shape)

df_full_dataset = pd.merge(
    df_steam_user, df_vg_sales, left_on="game_name", right_on="Name"
)
print(df_full_dataset.shape)

game_list = [*set(df_full_dataset["game_name"])]
len(game_list)
