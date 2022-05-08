from typing import Dict, List
from analysis.determine_batting_player import get_batting_player_formulas
from analysis.determine_linear_weights import get_woba_constants
from analysis.regression_analysis import RegressionAnalysisModel, perform_bats_handedness_regression, perform_regression
from class_model.BaseStatsPlayer import BaseStatsPlayer
from output_utils.progress.progress_bar import ProgressBar
from class_model.load_players import load_card_players, load_stats_players
import os

base_card_players = load_card_players()

tourney_files = os.listdir('data/tournament/')

tourney_types: Dict[str, List[BaseStatsPlayer]] = {}

progress_bar = ProgressBar(len(tourney_files), "Reading tourney files")
for tourney in tourney_files:
    tourney_type = tourney.split('_')[0][1:]

    if tourney_type not in tourney_types:
        tourney_types[tourney_type] = []

    stats_players = load_stats_players('data/tournament/' + tourney, base_card_players)

    tourney_types[tourney_type].extend(stats_players)
    progress_bar.increment()
progress_bar.finish()

players = tourney_types["openiron"]

get_woba_constants(players)

get_batting_player_formulas(players)

"""
y_denoms = [10, 50, 100, 200, 500]
cooks = [False, True]
for use_cooks_distance in cooks:
    for min_y_denom in y_denoms:
        ram_full = RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr,
            get_y_numerator=lambda player: player.batter_hits - player.batter_homeruns,
            get_y_denominator=lambda player: player.batter_pa - player.batter_hit_by_pitch - player.batter_homeruns - player.batter_walks - player.batter_strikeouts,
            min_y_denom=min_y_denom,
            should_use_cooks_distance=use_cooks_distance
        )
        ram_left_first = RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr,
            get_y_numerator=lambda player: player.batter_hits - player.batter_homeruns,
            get_y_denominator=lambda player: player.batter_pa - player.batter_strikeouts - player.batter_hit_by_pitch,
            min_y_denom=min_y_denom,
            should_use_cooks_distance=use_cooks_distance
        )
        ram_right_first = RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr,
            get_y_numerator=lambda player: player.batter_hits - player.batter_homeruns,
            get_y_denominator=lambda player: player.batter_pa - player.batter_strikeouts - player.batter_hit_by_pitch - player.batter_homeruns,
            min_y_denom=min_y_denom,
            should_use_cooks_distance=use_cooks_distance
        )
        ram_none = RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr,
            get_y_numerator=lambda player: player.batter_hits - player.batter_homeruns,
            get_y_denominator=lambda player: player.batter_pa - player.batter_hit_by_pitch,
            min_y_denom=min_y_denom,
            should_use_cooks_distance=use_cooks_distance
        )

        full = perform_bats_handedness_regression(
            players,
            ram_full
        )
        left_first = perform_bats_handedness_regression(
            players,
            ram_left_first
        )
        right_first = perform_bats_handedness_regression(
            players,
            ram_right_first
        )
        none_first = perform_bats_handedness_regression(
            players,
            ram_none
        )

        print(min_y_denom, "min denom")
        print(use_cooks_distance, "cooks")
        print("Right handed r_squared by ALL", full["R"].r_squared, "number of inputs analyzed", full["R"].len_x)
        print("Right handed r_squared by LEFT", left_first["R"].r_squared, "number of inputs analyzed", left_first["R"].len_x)
        print("Right handed r_squared by RIGHT", right_first["R"].r_squared, "number of inputs analyzed", right_first["R"].len_x)
        print("Right handed r_squared by NONE", none_first["R"].r_squared, "number of inputs analyzed", none_first["R"].len_x)
        print(full["R"].r_squared, left_first["R"].r_squared, right_first["R"].r_squared, none_first["R"].r_squared, min(full["R"].len_x, left_first["R"].len_x, none_first["R"].len_x))
        print()
"""