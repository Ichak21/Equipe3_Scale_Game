from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry
from itertools import compress
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import json
import warnings

warnings.filterwarnings("ignore")


class HLTB_handle:
    PATH = str(Path(__file__).parent.parent.absolute()) + str("/_output_handles/")
    OUTPUT: list = [
        "01_game_name",
        "02_hltb_name",
        "03_hltb_id",
        "04_time_main",
        "05_time_plus",
        "06_time_100",
        "07_time_allstyle",
        "08_count_main",
        "09_count_plus",
        "10_count_100",
        "11_count_allstyle",
        "12_count_completed",
        "13_count_speedrun",
        "14_count_backlog",
        "15_count_playing",
        "16_count_retired",
        "17_review_score",
        "18_count_review",
    ]
    TIME_MAIN: int = 3
    TIME_PLUS: int = 4
    TIME_100: int = 5
    TIME_ALLSTYLE: int = 6
    COUNT_MAIN: int = 7
    COUNT_PLUS: int = 8
    COUNT_100: int = 9
    COUNT_ALLSTYLE: int = 10
    COUNT_COMPLETED: int = 11
    COUNT_SPEEDRUN: int = 12
    COUNT_BACKLOG: int = 13
    COUNT_PLAYING: int = 14
    COUNT_RETIRED: int = 15
    REVIEW_SCORE: int = 16
    COUNT_REVIEW: int = 17
    mask: list = [
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ]

    def __init__(
        self,
        set_time_data: bool = False,
        set_count_data: bool = False,
        set_popularity_data: bool = False,
        set_review_data: bool = False,
    ):
        self.setTimeDate(set_time_data)
        self.setCountDate(set_count_data)
        self.setPopularityData(set_popularity_data)
        self.setReviewData(set_review_data)

    def setTimeDate(self, set_time_data: bool):
        self.mask[self.TIME_MAIN] = set_time_data
        self.mask[self.TIME_PLUS] = set_time_data
        self.mask[self.TIME_100] = set_time_data
        self.mask[self.TIME_ALLSTYLE] = set_time_data

    def setCountDate(self, set_count_data: bool):
        self.mask[self.COUNT_MAIN] = set_count_data
        self.mask[self.COUNT_PLUS] = set_count_data
        self.mask[self.COUNT_100] = set_count_data
        self.mask[self.COUNT_ALLSTYLE] = set_count_data

    def setPopularityData(self, set_popularity_data: bool):
        self.mask[self.COUNT_BACKLOG] = set_popularity_data
        self.mask[self.COUNT_COMPLETED] = set_popularity_data
        self.mask[self.COUNT_PLAYING] = set_popularity_data
        self.mask[self.COUNT_SPEEDRUN] = set_popularity_data
        self.mask[self.COUNT_RETIRED] = set_popularity_data

    def setReviewData(self, set_review_data: bool):
        self.mask[self.REVIEW_SCORE] = set_review_data
        self.mask[self.COUNT_REVIEW] = set_review_data

    def getDatas(self, game_name_list: list, file_name: str = None):

        output_columns: list = [*set(compress(self.OUTPUT, self.mask))]
        output_columns.sort()

        df_output: pd.DataFrame = pd.DataFrame(columns=output_columns)

        game_name_list_unique: list = [*set(game_name_list)]

        for game_name in tqdm(
            game_name_list_unique, desc="HLTB Wrapping ", colour="blue"
        ):

            current_anwser = HowLongToBeat().search(game_name)
            current_row: list = []

            if current_anwser != []:

                current_data = max(
                    current_anwser, key=lambda element: element.similarity
                )
                current_json = json.loads(
                    json.dumps(current_data.json_content, indent=4).capitalize()
                )
                current_row.append(game_name)
                current_row.append(current_json["game_name"])
                current_row.append(current_json["game_id"])
                if self.mask[self.TIME_MAIN]:
                    current_row.append(current_json["comp_main"])
                if self.mask[self.TIME_PLUS]:
                    current_row.append(current_json["comp_plus"])
                if self.mask[self.TIME_100]:
                    current_row.append(current_json["comp_100"])
                if self.mask[self.TIME_ALLSTYLE]:
                    current_row.append(current_json["comp_all"])
                if self.mask[self.COUNT_MAIN]:
                    current_row.append(current_json["comp_main_count"])
                if self.mask[self.COUNT_PLUS]:
                    current_row.append(current_json["comp_plus_count"])
                if self.mask[self.COUNT_100]:
                    current_row.append(current_json["comp_100_count"])
                if self.mask[self.COUNT_ALLSTYLE]:
                    current_row.append(current_json["comp_all_count"])
                if self.mask[self.COUNT_COMPLETED]:
                    current_row.append(current_json["count_comp"])
                if self.mask[self.COUNT_SPEEDRUN]:
                    current_row.append(current_json["count_speedrun"])
                if self.mask[self.COUNT_BACKLOG]:
                    current_row.append(current_json["count_backlog"])
                if self.mask[self.COUNT_PLAYING]:
                    current_row.append(current_json["count_playing"])
                if self.mask[self.COUNT_RETIRED]:
                    current_row.append(current_json["count_retired"])
                if self.mask[self.REVIEW_SCORE]:
                    current_row.append(current_json["review_score"])
                if self.mask[self.COUNT_REVIEW]:
                    current_row.append(current_json["count_review"])

            else:
                current_row.append(game_name)
                current_row.append(None)
                current_row.append(None)
                if self.mask[self.TIME_MAIN]:
                    current_row.append(None)
                if self.mask[self.TIME_PLUS]:
                    current_row.append(None)
                if self.mask[self.TIME_100]:
                    current_row.append(None)
                if self.mask[self.TIME_ALLSTYLE]:
                    current_row.append(None)
                if self.mask[self.COUNT_MAIN]:
                    current_row.append(None)
                if self.mask[self.COUNT_PLUS]:
                    current_row.append(None)
                if self.mask[self.COUNT_100]:
                    current_row.append(None)
                if self.mask[self.COUNT_ALLSTYLE]:
                    current_row.append(None)
                if self.mask[self.COUNT_COMPLETED]:
                    current_row.append(None)
                if self.mask[self.COUNT_SPEEDRUN]:
                    current_row.append(None)
                if self.mask[self.COUNT_BACKLOG]:
                    current_row.append(None)
                if self.mask[self.COUNT_PLAYING]:
                    current_row.append(None)
                if self.mask[self.COUNT_RETIRED]:
                    current_row.append(None)
                if self.mask[self.REVIEW_SCORE]:
                    current_row.append(None)
                if self.mask[self.COUNT_REVIEW]:
                    current_row.append(None)

            df_output = df_output.append(
                dict(zip(output_columns, current_row)), ignore_index=True
            )

        if file_name != None:
            df_output.to_csv(str(self.PATH) + str(file_name), index=False)

        return df_output


# if __name__ == "__main__":
#     myhand = HLTB_handle(True, True, True)
#     print(
#         myhand.getDatas(
#             ["Elven Legacy", "LEGO Jurassic World", "Hearts of Iron III"],
#             "time_for_dataset.csv",
#         )
#     )
