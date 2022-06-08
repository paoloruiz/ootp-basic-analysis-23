from typing import Dict, List
from analysis.determine_batting_player import get_batting_player_formulas
from analysis.determine_linear_weights import get_woba_constants
from analysis.determine_pitching_player import get_pitching_player_formulas
from analysis.lin_weights_modifiers import LeagueLWM, LinearWeightsModifiers
from class_model.BaseProjectedBatter import BaseProjectedBatter, generate_projected_batters_lg
from class_model.BaseStatsPlayer import BaseStatsPlayer
from class_model.ProjectedPitcher import generate_projected_pitchers_lg
from class_model.global_stats.AllLeagueStats import AllLeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from class_model.league_stats.league_stats import IndividualLeagueStats
from class_model.stats_player.batting_stats import get_batter_stats_for_players
from class_model.stats_player.filter_cards import filter_cards_for_tourney
from class_model.stats_player.pitching_stats import get_pitcher_stats_for_players
from output_utils.generate_worksheet import generate_worksheet
from output_utils.progress.progress_bar import ProgressBar
from class_model.load_players import load_card_players
from output_utils.headers.lg_stats_headers import proj_lg_batter_headers, proj_lg_batter_hidden_cols, proj_lg_pitcher_headers
from util.load_tourney_stats_players import load_league_stats_players_flat
import xlsxwriter


lwmods = LeagueLWM(
    batting=LinearWeightsModifiers(),
    pitching=LinearWeightsModifiers()
)

all_league_stats = AllLeagueStats()
all_pitcher_stats = PitcherStats()
individual_league_stats = IndividualLeagueStats()

base_card_players = load_card_players()

leagues: List[Dict[str, BaseStatsPlayer]] = load_league_stats_players_flat(base_card_players, all_league_stats, all_pitcher_stats, individual_league_stats=individual_league_stats)

sheet_pbar = ProgressBar(1, "Creating leauge sheet")
workbook = xlsxwriter.Workbook('output/leauge_analysis_sheet.xlsx', { "use_future_functions": True })

sheet_pbar.finish()

ovr_batters = filter_cards_for_tourney(
    leagues,
    "BATTER"
)
vl_batters = filter_cards_for_tourney(
    leagues,
    "BATTER_VL"
)
vr_batters = filter_cards_for_tourney(
    leagues,
    "BATTER_VR"
)
sp_ovr = filter_cards_for_tourney(
    leagues,
    "STARTER"
)
sp_vl = filter_cards_for_tourney(
    leagues,
    "STARTER_VL"
)
sp_vr = filter_cards_for_tourney(
    leagues,
    "STARTER_VR"
)
rp_ovr = filter_cards_for_tourney(
    leagues,
    "RELIEVER"
)
rp_vl = filter_cards_for_tourney(
    leagues,
    "RELIEVER_VL"
)
rp_vr = filter_cards_for_tourney(
    leagues,
    "RELIEVER_VR"
)

woba_constants = get_woba_constants(ovr_batters, all_league_stats.league_stats["lg"])

proj_batter_sheet = workbook.add_worksheet("proj-BAT")
proj_sp_sheet = workbook.add_worksheet("proj-SP")
proj_rp_sheet = workbook.add_worksheet("proj-RP")

ovr_batting_player_formulas = get_batting_player_formulas(ovr_batters)
vl_batting_player_formulas = get_batting_player_formulas(vl_batters, plat_only=True)
vr_batting_player_formulas = get_batting_player_formulas(vr_batters, plat_only=True)
sp_ovr_player_formulas = get_pitching_player_formulas(sp_ovr, all_pitcher_stats)
sp_vl_player_formulas = get_pitching_player_formulas(sp_vl, all_pitcher_stats, plat_only=True)
sp_vr_player_formulas = get_pitching_player_formulas(sp_vr, all_pitcher_stats, plat_only=True)
rp_ovr_player_formulas = get_pitching_player_formulas(rp_ovr, all_pitcher_stats)
rp_vl_player_formulas = get_pitching_player_formulas(rp_vl, all_pitcher_stats, plat_only=True)
rp_vr_player_formulas = get_pitching_player_formulas(rp_vr, all_pitcher_stats, plat_only=True)

possible_players = list(base_card_players.values())
possible_batters = list(filter(lambda player: player.position != 1 or player.con_ovr > 35, possible_players))

ovr_batter_stats_for_projection: Dict[str, any] = get_batter_stats_for_players(ovr_batters)
vl_batter_stats_for_projection: Dict[str, any] = get_batter_stats_for_players(vl_batters)
vr_batter_stats_for_projection: Dict[str, any] = get_batter_stats_for_players(vr_batters)
sp_ovr_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(sp_ovr)
sp_vl_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(sp_vl)
sp_vr_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(sp_vr)
rp_ovr_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(rp_ovr)
rp_vl_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(rp_vl)
rp_vr_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(rp_vr)

projected_batters: List[BaseProjectedBatter] = generate_projected_batters_lg(
    players=possible_players,
    linear_weights_formulas=woba_constants,
    ovr_batting_player_formulas=ovr_batting_player_formulas,
    vl_batting_player_formulas=vl_batting_player_formulas,
    vr_batting_player_formulas=vr_batting_player_formulas,
    ovr_batter_stats_for_players=ovr_batter_stats_for_projection,
    vl_batter_stats_for_players=vl_batter_stats_for_projection,
    vr_batter_stats_for_players=vr_batter_stats_for_projection,
    league_stats=all_league_stats.league_stats["lg"],
    lwm=lwmods.batting
)
projected_batters.sort(key=lambda pd: pd.tpbs.ovr.war, reverse=True)
generate_worksheet(projected_batters, proj_batter_sheet, proj_lg_batter_headers, "con", proj_lg_batter_hidden_cols, "projected batters")

possible_pitchers = list(filter(lambda player: player.defensep > 10, possible_players))
projected_sp = generate_projected_pitchers_lg(
    players=possible_pitchers,
    linear_weights_formulas=woba_constants,
    pitcher_stats=all_pitcher_stats,
    ovr_projected_pitching_formulas=sp_ovr_player_formulas,
    vl_projected_pitching_formulas=sp_vl_player_formulas,
    vr_projected_pitching_formulas=sp_vr_player_formulas,
    ovr_pitcher_stats_for_players=sp_ovr_stats_for_projection,
    vl_pitcher_stats_for_players=sp_vl_stats_for_projection,
    vr_pitcher_stats_for_players=sp_vr_stats_for_projection,
    platoon_splits=individual_league_stats.get_platoon_splits("lg", ignore_validity=True),
    lwm=lwmods.pitching
)
projected_sp.sort(key=lambda pd: pd.ovr.war_with_relief, reverse=True)
generate_worksheet(projected_sp, proj_sp_sheet, proj_lg_pitcher_headers, "stu", [], "projected sp")

projected_rp = generate_projected_pitchers_lg(
    players=possible_pitchers,
    linear_weights_formulas=woba_constants,
    pitcher_stats=all_pitcher_stats,
    ovr_projected_pitching_formulas=rp_ovr_player_formulas,
    vl_projected_pitching_formulas=rp_vl_player_formulas,
    vr_projected_pitching_formulas=rp_vr_player_formulas,
    ovr_pitcher_stats_for_players=rp_ovr_stats_for_projection,
    vl_pitcher_stats_for_players=rp_vl_stats_for_projection,
    vr_pitcher_stats_for_players=rp_vr_stats_for_projection,
    platoon_splits=individual_league_stats.get_platoon_splits("lg", ignore_validity=True),
    lwm=lwmods.pitching
)
projected_rp.sort(key=lambda pd: pd.ovr.war, reverse=True)
generate_worksheet(projected_rp, proj_rp_sheet, proj_lg_pitcher_headers, "stu", [], "projected rp")

close_pbar = ProgressBar(1, "Closing analysis sheet file")
workbook.close()
close_pbar.finish()
print()