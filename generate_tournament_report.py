from typing import Dict, List
from analysis.determine_batting_player import get_batting_player_formulas
from analysis.determine_linear_weights import get_woba_constants
from class_model.BaseProjectedBatter import generate_projected_batters
from class_model.BaseStatsPlayer import BaseStatsPlayer
from class_model.global_stats.AllLeagueStats import AllLeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from class_model.stats_player.filter_cards import filter_cards_for_tourney
from output_utils.generate_tourney_selections_sheet import generate_tourney_selections
from output_utils.generate_worksheet import generate_worksheet
from output_utils.progress.progress_bar import ProgressBar
from output_utils.headers.tourney_stats_header import get_batter_headers, batter_hidden_cols, get_sp_headers, get_rp_headers, proj_batter_headers, proj_batter_hidden_cols
from class_model.load_players import load_card_players, load_stats_players
import xlsxwriter
import os

projections_tourney_types = {
    "openiron": lambda player: player.ovr < 60,
    "openbronze": lambda player: player.ovr < 70
}

all_league_stats = AllLeagueStats()
all_pitcher_stats = PitcherStats()

base_card_players = load_card_players()

tourney_files = os.listdir('data/tournament/')

tourney_types: Dict[str, List[Dict[str, BaseStatsPlayer]]] = {}

progress_bar = ProgressBar(len(tourney_files), "Reading tourney files")
for tourney in tourney_files:
    tourney_type = tourney.split('_')[0][1:]

    if tourney_type not in tourney_types:
        tourney_types[tourney_type] = []

    stats_players = load_stats_players('data/tournament/' + tourney, tourney_type, base_card_players, all_league_stats, all_pitcher_stats)

    tourney_types[tourney_type].append(stats_players)
    progress_bar.increment()
progress_bar.finish()

for tourney_type in tourney_types.keys():
    sheet_pbar = ProgressBar(1, "Creating " + tourney_type + " sheet")
    workbook = xlsxwriter.Workbook('output/' + tourney_type + '_tourney_sheet.xlsx', { "use_future_functions": True })
    batter_sheet = workbook.add_worksheet("BAT")
    sp_sheet = workbook.add_worksheet("SP")
    rp_sheet = workbook.add_worksheet("RP")
    selections_sheet = workbook.add_worksheet("selections")

    sheet_pbar.finish()

    batter_players = filter_cards_for_tourney(
        tourney_types[tourney_type],
        "BATTER"
    )
    sp_players = filter_cards_for_tourney(
        tourney_types[tourney_type],
        "STARTER"
    )
    rp_players = filter_cards_for_tourney(
        tourney_types[tourney_type],
        "RELIEVER"
    )

    woba_constants = get_woba_constants(batter_players, all_league_stats.league_stats[tourney_type])
    batting_player_formulas = get_batting_player_formulas(batter_players)

    batter_players.sort(key=lambda pd: pd.stats_batter.batter_woba, reverse=True)
    sp_players.sort(key=lambda pd: pd.stats_pitcher.pitcher_fip)
    rp_players.sort(key=lambda pd: pd.stats_pitcher.pitcher_fip)

    # Write different stats to sheet
    generate_worksheet(batter_players, batter_sheet, get_batter_headers(woba_constants, all_league_stats.league_stats[tourney_type]), "con", batter_hidden_cols, "batter analysis")
    generate_worksheet(sp_players, sp_sheet, get_sp_headers(woba_constants, all_pitcher_stats), "stu", [], "sp analysis")
    generate_worksheet(rp_players, rp_sheet, get_rp_headers(woba_constants, all_pitcher_stats), "stu", [], "rp analysis")
    generate_tourney_selections(selections_sheet, "selections tourney")

    if tourney_type in projections_tourney_types:
        filter_fn = projections_tourney_types[tourney_type]
        proj_batter_sheet = workbook.add_worksheet("proj-BAT")

        projected_batters = generate_projected_batters(list(filter(filter_fn, base_card_players.values())), woba_constants, batting_player_formulas)
        generate_worksheet(projected_batters, proj_batter_sheet, proj_batter_headers, "con", proj_batter_hidden_cols, "projected batters")

    close_pbar = ProgressBar(1, "Closing analysis sheet file")
    workbook.close()
    close_pbar.finish()
    print()