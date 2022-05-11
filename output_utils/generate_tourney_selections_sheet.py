from typing import List
from class_model.BaseProjectedBatter import BaseProjectedBatter
from output_utils.progress.progress_bar import ProgressBar



def generate_tourney_selections(worksheet, sheet_name: str):
    progress_bar = ProgressBar(1, "Writing " + sheet_name + " sheet")

    worksheet.write(0, 0, "MIN_PA")
    worksheet.write(0, 1, 1)
    worksheet.write(0, 2, "MIN_BF")
    worksheet.write(0, 3, 1)

    progress_bar.finish()

def __write_projections__(worksheet, x, y, players: List[BaseProjectedBatter]):
    for i in range(len(players)):
        worksheet.write(x + i, y, players[i].card_player.full_title)
        worksheet.write(x + i, y + 1, players[i].war)

def generate_tourney_proj_batter_selections(worksheet, projected_batters: List[BaseProjectedBatter], sheet_name: str):
    progress_bar = ProgressBar(1, "Writing " + sheet_name + " sheet")

    filtered_batters = list(filter(lambda batter: batter.card_player.avk_ovr > 25, projected_batters))

    worksheet.write(0, 0, "C")
    worksheet.write(0, 1, "C_WAR")
    players = list(filter(lambda batter: batter.position == 2, filtered_batters))[0:5]
    __write_projections__(worksheet, 1, 0, players)

    worksheet.write(0, 3, "1B")
    worksheet.write(0, 4, "1B_WAR")
    players = list(filter(lambda batter: batter.position == 3, filtered_batters))[0:5]
    __write_projections__(worksheet, 1, 3, players)

    worksheet.write(0, 6, "2B")
    worksheet.write(0, 7, "2B_WAR")
    players = list(filter(lambda batter: batter.position == 4, filtered_batters))[0:5]
    __write_projections__(worksheet, 1, 6, players)

    worksheet.write(0, 9, "3B")
    worksheet.write(0, 10, "3B_WAR")
    players = list(filter(lambda batter: batter.position == 5, filtered_batters))[0:5]
    __write_projections__(worksheet, 1, 9, players)

    worksheet.write(0, 12, "SS")
    worksheet.write(0, 13, "SS_WAR")
    players = list(filter(lambda batter: batter.position == 6, filtered_batters))[0:5]
    __write_projections__(worksheet, 1, 12, players)

    worksheet.write(7, 0, "LF")
    worksheet.write(7, 1, "LF_WAR")
    players = list(filter(lambda batter: batter.position == 7, filtered_batters))[0:5]
    __write_projections__(worksheet, 8, 0, players)

    worksheet.write(7, 3, "CF")
    worksheet.write(7, 4, "CF_WAR")
    players = list(filter(lambda batter: batter.position == 8, filtered_batters))[0:5]
    __write_projections__(worksheet, 8, 3, players)

    worksheet.write(7, 6, "RF")
    worksheet.write(7, 7, "RF_WAR")
    players = list(filter(lambda batter: batter.position == 9, filtered_batters))[0:5]
    __write_projections__(worksheet, 8, 6, players)

    worksheet.write(7, 9, "DH")
    worksheet.write(7, 10, "DH_WAR")
    players = list(filter(lambda batter: batter.position == 0, filtered_batters))[0:5]
    __write_projections__(worksheet, 8, 9, players)


    progress_bar.finish()
