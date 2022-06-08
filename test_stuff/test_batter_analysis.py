from typing import Callable, Dict, List, Tuple
from analysis.determine_batting_player import get_batting_player_formulas
from analysis.determine_linear_weights import get_woba_constants
from analysis.determine_pitching_player import get_pitching_player_formulas
from analysis.regression_analysis import RegressionAnalysisModel
from analysis.test_batting_fns import get_batter_bats_hl_formula, get_batter_bats_hl_poly2_formula, get_batter_bats_hl_poly3_formula, get_batter_bats_no_hl_formula, get_batter_bats_reg_formula, get_batter_formula, get_batter_hl_formula
from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer
from class_model.global_stats.AllLeagueStats import AllLeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from class_model.load_players import load_card_players
from class_model.stats_player.filter_cards import filter_cards_for_tourney
from output_utils.csvwriter import CsvWriter
from util.load_tourney_stats_players import load_tourney_stats_players_by_tourney

all_league_stats = AllLeagueStats()
all_pitcher_stats = PitcherStats()

# Variables to set up
TESTING_TOURNEY = "openiron"
TEST_MOD_SAMPLE_NUM = 5

base_card_players = load_card_players()

tourney_data = load_tourney_stats_players_by_tourney(base_card_players, all_league_stats, all_pitcher_stats)

# Filter tourney data into analysis and sample data to test upon
tourney_data_by_type = tourney_data[TESTING_TOURNEY]
analysis_tourneys: List[Dict[str, BaseStatsPlayer]] = []
sample_tourneys: List[Dict[str, BaseStatsPlayer]] = []

tourney_ids = list(tourney_data_by_type.keys())
for i in range(len(tourney_ids)):
    if i % TEST_MOD_SAMPLE_NUM == 0:
        sample_tourneys.append(tourney_data_by_type[tourney_ids[i]])
    else:
        analysis_tourneys.append(tourney_data_by_type[tourney_ids[i]])

# Transform into single line players for analysis
batter_players_analysis = filter_cards_for_tourney(
    analysis_tourneys,
    "BATTER"
)

sp_players_analysis = filter_cards_for_tourney(
    analysis_tourneys,
    "STARTER"
)
sp_with_pos_to_sp_data = {}
for sp in sp_players_analysis:
    sp_with_pos_to_sp_data[sp.cid] = sp

rp_players_analysis = filter_cards_for_tourney(
    analysis_tourneys,
    "RELIEVER"
)
rp_with_pos_to_rp_data = {}
for rp in rp_players_analysis:
    rp_with_pos_to_rp_data[rp.cid] = rp


# Create some formulas
woba_constants = get_woba_constants(batter_players_analysis, all_league_stats.league_stats[TESTING_TOURNEY])
batting_player_formulas = get_batting_player_formulas(batter_players_analysis)
sp_player_formulas = get_pitching_player_formulas(sp_players_analysis, all_pitcher_stats)
rp_player_formulas = get_pitching_player_formulas(rp_players_analysis, all_pitcher_stats)

batter_players_sample = filter_cards_for_tourney(
    sample_tourneys,
    "BATTER"
)
sp_players_sample = filter_cards_for_tourney(
    sample_tourneys,
    "STARTER"
)
rp_players_sample = filter_cards_for_tourney(
    sample_tourneys,
    "RELIEVER"
)

qualifying_sample_batters = list(filter(lambda player: player.stats_batter.batter_pa >= 50, batter_players_sample))
qualifying_sample_c = list(filter(lambda player: player.stats_fielder != None and player.stats_fielder.fielding_position == 2 and player.stats_fielder.fielding_ip >= 10.0, batter_players_sample))
qualifying_sample_1b = list(filter(lambda player: player.stats_fielder != None and player.stats_fielder.fielding_position == 3 and player.stats_fielder.fielding_ip >= 10.0, batter_players_sample))
qualifying_sample_2b = list(filter(lambda player: player.stats_fielder != None and player.stats_fielder.fielding_position == 4 and player.stats_fielder.fielding_ip >= 10.0, batter_players_sample))
qualifying_sample_3b = list(filter(lambda player: player.stats_fielder != None and player.stats_fielder.fielding_position == 5 and player.stats_fielder.fielding_ip >= 10.0, batter_players_sample))
qualifying_sample_ss = list(filter(lambda player: player.stats_fielder != None and player.stats_fielder.fielding_position == 6 and player.stats_fielder.fielding_ip >= 10.0, batter_players_sample))
qualifying_sample_lf = list(filter(lambda player: player.stats_fielder != None and player.stats_fielder.fielding_position == 7 and player.stats_fielder.fielding_ip >= 10.0, batter_players_sample))
qualifying_sample_cf = list(filter(lambda player: player.stats_fielder != None and player.stats_fielder.fielding_position == 8 and player.stats_fielder.fielding_ip >= 10.0, batter_players_sample))
qualifying_sample_rf = list(filter(lambda player: player.stats_fielder != None and player.stats_fielder.fielding_position == 9 and player.stats_fielder.fielding_ip >= 10.0, batter_players_sample))
qualifying_sample_sp = list(filter(lambda player: player.stats_pitcher.pitcher_bf >= 50, sp_players_sample))
qualifying_sample_rp = list(filter(lambda player: player.stats_pitcher.pitcher_bf >= 50, rp_players_sample))
print(len(qualifying_sample_batters), "qualifying batters")
print(len(qualifying_sample_c), "qualifying c")
print(len(qualifying_sample_1b), "qualifying 1b")
print(len(qualifying_sample_2b), "qualifying 2b")
print(len(qualifying_sample_3b), "qualifying 3b")
print(len(qualifying_sample_ss), "qualifying ss")
print(len(qualifying_sample_lf), "qualifying lf")
print(len(qualifying_sample_cf), "qualifying cf")
print(len(qualifying_sample_rf), "qualifying rf")
print(len(qualifying_sample_sp), "qualifying sp")
print(len(qualifying_sample_rp), "qualifying rp")

# Assumptions - 5000, 0.8, wah, all
pa_max_cases = ["5000"]
pct_stats_cases = ["0.6", "0.7", "0.8", "0.85", "0.9", ".95", "0.975", "1.0"]
bat_stats = ["avk", "pow", "eye", "bab"]

bat_stat_order_rams = {
    "avk": {
        "ah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "aw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ahw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "awh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "h": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "haw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hwa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.avk_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
    },
    "pow": {
        "ah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "aw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ahw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "awh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "h": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "haw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hwa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks - player.stats_batter.batter_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks - player.stats_batter.batter_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.pow_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
    },
    "eye": {
        "ah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "aw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ahw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "awh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "h": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "haw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hwa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.eye_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_walks, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
    },
    "bab": {
        "ah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "aw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ahw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "awh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "h": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "haw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hwa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns - player.stats_batter.batter_strikeouts - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.babip_ovr, 
            get_y_numerator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
            get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
    },
}
bat_stats_cases = {}
batter_with_pos_to_batter_data: Dict[str, Dict[str, Dict[int, Tuple[int, int]]]] = {}
for stat in bat_stat_order_rams.keys():
    bat_stats_cases[stat] = {}
    batter_with_pos_to_batter_data[stat] = {}
    for stat_order in bat_stat_order_rams[stat].keys():
        stat_fn = None
        if stat == "avk":
            stat_fn = lambda player: player.card_player.avk_ovr
        elif stat == "eye":
            stat_fn = lambda player: player.card_player.eye_ovr
        elif stat == "pow":
            stat_fn = lambda player: player.card_player.pow_ovr
        elif stat == "bab":
            stat_fn = lambda player: player.card_player.babip_ovr
        bat_stats_cases[stat][stat_order] = {
            "bats_hl": get_batter_bats_hl_formula(batter_players_analysis, stat_fn, bat_stat_order_rams[stat][stat_order]),
            "bats_poly2": get_batter_bats_hl_poly2_formula(batter_players_analysis, stat_fn, bat_stat_order_rams[stat][stat_order]),
            "bats_poly3": get_batter_bats_hl_poly3_formula(batter_players_analysis, stat_fn, bat_stat_order_rams[stat][stat_order]),
            "bats_reg_elast": get_batter_bats_reg_formula(batter_players_analysis, stat_fn, bat_stat_order_rams[stat][stat_order], "elastic_net"),
            "bats_reg_lasso": get_batter_bats_reg_formula(batter_players_analysis, stat_fn, bat_stat_order_rams[stat][stat_order], "sqrt_lasso"),
        }

        batter_with_pos_to_batter_data[stat][stat_order] = {}
        for player in batter_players_analysis:
            rating = stat_fn(player)
            if rating not in batter_with_pos_to_batter_data[stat][stat_order]:
                batter_with_pos_to_batter_data[stat][stat_order][rating] = (0, 0)
            batter_with_pos_to_batter_data[stat][stat_order][rating] = (batter_with_pos_to_batter_data[stat][stat_order][rating][0] + bat_stat_order_rams[stat][stat_order].get_y_numerator(player),
                bat_stat_order_rams[stat][stat_order].get_y_denominator(player) + batter_with_pos_to_batter_data[stat][stat_order][rating][1])


pa_off_by: Dict[str, float] = {}
for pa_max in pa_max_cases:
    pa_off_by[pa_max] = 0.0

pct_off_by: Dict[str, float] = {}
for pct_stats in pct_stats_cases:
    pct_off_by[pct_stats] = 0.0

orders_off_by: Dict[str, float] = {}
for stat_order in bat_stat_order_rams["avk"]:
    orders_off_by[stat_order] = 0.0

bat_type_off_by = {
    "bats_hl": 0.0,
    "bats_poly2": 0.0,
    "bats_poly3": 0.0,
    "bats_reg_elast": 0.0,
    "bats_reg_lasso": 0.0,
}

def measure_batter_off_by(
    formula: Callable[[SingleLineStatsPlayer], float], 
    bat_pos_dict: Dict[str, Dict[str, Dict[int, Tuple[int, int]]]], 
    sample_player: SingleLineStatsPlayer,
    existing_stats_weight: float,
    existing_stats_max_pa: int,
    ram: RegressionAnalysisModel,
    stat: str,
    stat_order: str
) -> float:
    if ram.get_y_denominator(sample_player) == 0:
        return 0.0


    stat_to_pred = ram.get_y_numerator(sample_player)

    sample_rating = ram.get_x(sample_player)
    
    stats_count = 0
    stats_pred = 0
    if sample_rating in bat_pos_dict[stat][stat_order]:
        stats_pred = bat_pos_dict[stat][stat_order][sample_rating][0] / bat_pos_dict[stat][stat_order][sample_rating][1]
        stats_count = bat_pos_dict[stat][stat_order][sample_rating][1]
    elif sample_rating - 1 in bat_pos_dict[stat][stat_order] and sample_rating + 1 in bat_pos_dict[stat][stat_order]:
        low_pred = bat_pos_dict[stat][stat_order][sample_rating - 1][0] / bat_pos_dict[stat][stat_order][sample_rating - 1][1]
        low_count = bat_pos_dict[stat][stat_order][sample_rating - 1][1]
        high_pred = bat_pos_dict[stat][stat_order][sample_rating + 1][0] / bat_pos_dict[stat][stat_order][sample_rating + 1][1]
        high_count = bat_pos_dict[stat][stat_order][sample_rating + 1][1]
        stats_pred = (low_pred + high_pred) / 2
        stats_count = round((low_count + high_count) / 2)
    elif sample_rating - 1 in bat_pos_dict[stat][stat_order]:
        stats_pred = bat_pos_dict[stat][stat_order][sample_rating - 1][0] / bat_pos_dict[stat][stat_order][sample_rating - 1][1]
        stats_count = bat_pos_dict[stat][stat_order][sample_rating - 1][1]
    elif sample_rating + 1 in bat_pos_dict[stat][stat_order]:
        stats_pred = bat_pos_dict[stat][stat_order][sample_rating + 1][0] / bat_pos_dict[stat][stat_order][sample_rating + 1][1]
        stats_count = bat_pos_dict[stat][stat_order][sample_rating + 1][1]

    fill_pct = None
    if stats_count > existing_stats_max_pa:
        fill_pct = existing_stats_weight
    else:
        fill_pct = float(stats_count) / existing_stats_max_pa * existing_stats_weight

    if fill_pct > 0.0:
        prediction_from_player = stats_pred * ram.get_y_denominator(sample_player)
        prediction_from_formula = formula(sample_player) * ram.get_y_denominator(sample_player)

        prediction = prediction_from_player * fill_pct + (1.0 - fill_pct) * prediction_from_formula

        return abs(prediction - stat_to_pred)

    return abs(formula(sample_player) * ram.get_y_denominator(sample_player) - stat_to_pred)

bats_sample_only = list(filter(lambda player: player.get_fielding_position() == 0, batter_players_sample))

for pa_max in pa_off_by.keys():
    for pct_stats in pct_off_by.keys():
        for stat in bat_stats:
            for stat_order in orders_off_by.keys():
                for btypeform in bat_type_off_by.keys():
                    bsc_s = bat_stats_cases[stat]
                    bsc_o = bsc_s[stat_order]
                    formula = bsc_o[btypeform]
                    ram = bat_stat_order_rams[stat][stat_order]
                    pa_max_int = int(pa_max)
                    pct_stat_float = float(pct_stats)
                    for sample_pl in bats_sample_only:
                        off_by = measure_batter_off_by(
                            formula=formula,
                            bat_pos_dict=batter_with_pos_to_batter_data,
                            sample_player=sample_pl,
                            existing_stats_weight=pct_stat_float,
                            existing_stats_max_pa=pa_max_int,
                            ram=ram,
                            stat=stat,
                            stat_order=stat_order
                        )


                        pa_off_by[pa_max] += off_by
                        pct_off_by[pct_stats] += off_by
                        orders_off_by[stat_order] += off_by
                        bat_type_off_by[btypeform] += off_by

f = open('output/off_by.csv', 'w')
csv_writer = CsvWriter()
csv_writer.record(['pa_off_by'])
csv_writer.record(list(pa_off_by.keys()))
csv_writer.record(list(pa_off_by.values()))
csv_writer.record([])
csv_writer.record([])
csv_writer.record(['pct_off_by'])
csv_writer.record(list(pct_off_by.keys()))
csv_writer.record(list(pct_off_by.values()))
csv_writer.record([])
csv_writer.record([])
csv_writer.record(['orders_off_by'])
csv_writer.record(list(orders_off_by.keys()))
csv_writer.record(list(orders_off_by.values()))
csv_writer.record([])
csv_writer.record([])
csv_writer.record(['bat_type_off_by'])
csv_writer.record(list(bat_type_off_by.keys()))
csv_writer.record(list(bat_type_off_by.values()))
f.write(csv_writer.getCSV())
f.close()

