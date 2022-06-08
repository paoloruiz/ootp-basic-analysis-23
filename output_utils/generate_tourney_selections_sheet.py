from turtle import width
from typing import Callable, List
from class_model.BaseProjectedBatter import BaseProjectedBatter
from output_utils.progress.progress_bar import ProgressBar



def generate_tourney_selections(worksheet, sheet_name: str):
    progress_bar = ProgressBar(1, "Writing " + sheet_name + " sheet")

    worksheet.write(0, 0, "MIN_PA")
    worksheet.write(0, 1, 1000)
    worksheet.write(0, 2, "MIN_BF")
    worksheet.write(0, 3, 1000)

    worksheet.set_column('B:B', 45)
    worksheet.set_column('F:F', 45)
    worksheet.set_column('J:J', 45)

    progress_bar.finish()

def __write_projections__(worksheet, x, y, players: List[BaseProjectedBatter], war_fun: Callable[[BaseProjectedBatter], float]):
    for i in range(len(players)):
        worksheet.write(x + i, y, players[i].card_player.full_title)
        worksheet.write(x + i, y + 1, war_fun(players[i]))

positions = [("C", 2), ("1B", 3), ("2B", 4), ("3B", 5), ("SS", 6), ("LF", 7), ("CF", 8), ("RF", 9), ("DH", 0)]

def generate_tourney_proj_batter_selections(worksheet, projected_batters: List[BaseProjectedBatter], sheet_name: str):
    good_batters = list(filter(lambda player: player.card_player.avk_ovr > 25, projected_batters))
    progress_bar = ProgressBar(1, "Writing " + sheet_name + " sheet")

    for i in range(len(positions)):
        pos, pos_num = positions[i]
        worksheet.write(i * 7, 0, pos)
        worksheet.write(i * 7, 1, pos + "_WAR")
        players = list(filter(lambda batter: batter.position == pos_num, good_batters))[0:5]
        __write_projections__(worksheet, i * 7 + 1, 0, players, war_fun=lambda player: player.tpbs.ovr.war)

        worksheet.write(i * 7, 3, pos + " vL")
        worksheet.write(i * 7, 4, pos + "_vL_WAR")
        players = list(filter(lambda batter: batter.position == pos_num, sorted(good_batters, key=lambda player: player.tpbs.vl.war, reverse=True)))[0:5]
        __write_projections__(worksheet, i * 7 + 1, 3, players, war_fun=lambda player: player.tpbs.vl.war)

        worksheet.write(i * 7, 6, pos + " vR")
        worksheet.write(i * 7, 7, pos + "_vR_WAR")
        players = list(filter(lambda batter: batter.position == pos_num, sorted(good_batters, key=lambda player: player.tpbs.vr.war, reverse=True)))[0:5]
        __write_projections__(worksheet, i * 7 + 1, 6, players, war_fun=lambda player: player.tpbs.vr.war)

    worksheet.set_column('A:A', 45)
    worksheet.set_column('D:D', 45)
    worksheet.set_column('G:G', 45)

    progress_bar.finish()
