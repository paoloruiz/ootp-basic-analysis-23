from typing import Dict, List
from analysis.determine_batting_player import get_batting_player_formulas
from analysis.determine_linear_weights import get_woba_constants
from analysis.determine_pitching_player import get_pitching_player_formulas
from analysis.lin_weights_modifiers import LeagueLWM, LinearWeightsModifiers
from analysis.war_funcs import get_batter_war_func, get_pitcher_war_func
from class_model.BaseProjectedBatter import generate_projected_batters
from class_model.BaseStatsPlayer import BaseStatsPlayer
from class_model.ProjectedPitcher import generate_projected_pitchers
from class_model.global_stats.AllLeagueStats import AllLeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from class_model.league_stats.league_stats import IndividualLeagueStats
from class_model.league_stats.top_team_pitcher_analysis import analyze_league_pitching
from class_model.league_stats.top_team_stats_analysis import analyze_leagues
from class_model.stats_player.batting_stats import get_batter_stats_for_players
from class_model.stats_player.filter_cards import filter_cards_for_tourney
from class_model.stats_player.pitching_stats import get_pitcher_stats_for_players
from output_utils.csvwriter import CsvWriter
from output_utils.generate_tourney_selections_sheet import generate_tourney_proj_batter_selections, generate_tourney_selections
from output_utils.generate_worksheet import generate_worksheet
from output_utils.progress.progress_bar import ProgressBar
from output_utils.headers.tourney_stats_header import get_batter_headers, batter_hidden_cols, get_sp_headers, get_rp_headers, proj_batter_headers, proj_batter_hidden_cols, proj_pitcher_headers
from class_model.load_players import load_card_players
from util.load_tourney_stats_players import load_tourney_stats_players_flat
import xlsxwriter

projections_tourney_types = {
    "openiron": lambda player: player.ovr < 60,
    "openbronze": lambda player: player.ovr < 70,
    "pd": lambda player: True
}

lwmods = {
    "openiron": LeagueLWM(
        batting=LinearWeightsModifiers(),
        pitching=LinearWeightsModifiers()
    ),
    "openbronze": LeagueLWM(
        batting=LinearWeightsModifiers(),
        pitching=LinearWeightsModifiers()
    ),
    "pd": LeagueLWM(
        batting=LinearWeightsModifiers(),
        pitching=LinearWeightsModifiers()
    ),
}

all_league_stats = AllLeagueStats()
all_pitcher_stats = PitcherStats()
individual_league_stats = IndividualLeagueStats()

base_card_players = load_card_players()

tourney_types: Dict[str, List[Dict[str, BaseStatsPlayer]]] = load_tourney_stats_players_flat(base_card_players, all_league_stats, all_pitcher_stats, individual_league_stats=individual_league_stats, ttype=None)

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

    batter_war_func = get_batter_war_func(woba_constants, all_league_stats.league_stats[tourney_type])
    sp_war_func = get_pitcher_war_func(woba_constants, all_pitcher_stats, 500, True)
    rp_war_func = get_pitcher_war_func(woba_constants, all_pitcher_stats, 150, False)

    batter_players.sort(key=lambda pd: batter_war_func(pd), reverse=True)
    sp_players.sort(key=lambda pd: sp_war_func(pd), reverse=True)
    rp_players.sort(key=lambda pd: rp_war_func(pd), reverse=True)

    # Write different stats to sheet
    generate_worksheet(batter_players, batter_sheet, get_batter_headers(batter_war_func), "con", batter_hidden_cols, "batter analysis")
    generate_worksheet(sp_players, sp_sheet, get_sp_headers(sp_war_func), "stu", [], "sp analysis")
    generate_worksheet(rp_players, rp_sheet, get_rp_headers(rp_war_func), "stu", [], "rp analysis")
    generate_tourney_selections(selections_sheet, "selections tourney")

    if tourney_type in projections_tourney_types:
        filter_fn = projections_tourney_types[tourney_type]
        proj_batter_sheet = workbook.add_worksheet("proj-BAT")
        proj_sp_sheet = workbook.add_worksheet("proj-SP")
        proj_rp_sheet = workbook.add_worksheet("proj-RP")
        bat_selections_sheet = workbook.add_worksheet("proj-bat-selections")
        
        batting_player_formulas = get_batting_player_formulas(batter_players)
        sp_player_formulas = get_pitching_player_formulas(sp_players, all_pitcher_stats)
        rp_player_formulas = get_pitching_player_formulas(rp_players, all_pitcher_stats)

        possible_players = list(filter(filter_fn, base_card_players.values()))
        possible_batters = list(filter(lambda player: player.position != 1 or player.con_ovr > 35, possible_players))

        batter_stats_for_projection: Dict[str, any] = get_batter_stats_for_players(batter_players)
        sp_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(sp_players)
        rp_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(rp_players)

        projected_batters = generate_projected_batters(
            players=possible_players,
            linear_weights_formulas=woba_constants,
            batting_player_formulas=batting_player_formulas,
            batter_stats_for_players=batter_stats_for_projection,
            platoon_splits=individual_league_stats.get_platoon_splits(tourney_type),
            league_stats=all_league_stats.league_stats[tourney_type],
            lwm=lwmods[tourney_type].batting
        )
        projected_batters.sort(key=lambda pd: pd.tpbs.ovr.war, reverse=True)
        generate_worksheet(projected_batters, proj_batter_sheet, proj_batter_headers, "con", proj_batter_hidden_cols, "projected batters")

        generate_tourney_proj_batter_selections(bat_selections_sheet, projected_batters, "projected batter selections")

        possible_pitchers = list(filter(lambda player: player.defensep > 10, possible_players))
        projected_sp = generate_projected_pitchers(
            players=possible_pitchers,
            linear_weights_formulas=woba_constants,
            pitcher_stats=all_pitcher_stats,
            projected_pitching_formulas=sp_player_formulas,
            pitcher_stats_for_players=sp_stats_for_projection,
            platoon_splits=individual_league_stats.get_platoon_splits(tourney_type),
            lwm=lwmods[tourney_type].pitching
        )
        projected_sp.sort(key=lambda pd: pd.war_with_relief, reverse=True)
        generate_worksheet(projected_sp, proj_sp_sheet, proj_pitcher_headers, "stu", [], "projected sp")

        projected_rp = generate_projected_pitchers(
            players=possible_pitchers,
            linear_weights_formulas=woba_constants,
            pitcher_stats=all_pitcher_stats,
            projected_pitching_formulas=rp_player_formulas,
            pitcher_stats_for_players=rp_stats_for_projection,
            platoon_splits=individual_league_stats.get_platoon_splits(tourney_type),
            lwm=lwmods[tourney_type].pitching
        )
        projected_rp.sort(key=lambda pd: pd.war, reverse=True)
        generate_worksheet(projected_rp, proj_rp_sheet, proj_pitcher_headers, "stu", [], "projected rp")

    analyze_league_pitching(individual_league_stats.ils_d[tourney_type])

    close_pbar = ProgressBar(1, "Closing analysis sheet file")
    workbook.close()
    close_pbar.finish()
    print()

    league_analysis_csv = CsvWriter()
    analyze_leagues(individual_league_stats.ils_d[tourney_type], league_analysis_csv)
    f = open("output/" + tourney_type + "_lg_analysis.csv", "w")
    f.write(league_analysis_csv.getCSV())
    f.close()