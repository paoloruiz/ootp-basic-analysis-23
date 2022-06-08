from typing import Callable, Dict, List, Tuple
from analysis.determine_batting_player import get_batting_player_formulas
from analysis.determine_linear_weights import get_woba_constants
from analysis.determine_pitching_player import get_pitching_player_formulas
from analysis.regression_analysis import RegressionAnalysisModel
from analysis.test_batting_fns import get_batter_bats_hl_formula, get_batter_bats_no_hl_formula, get_batter_formula, get_batter_hl_formula, get_pitcher_throws_hl_formula, get_pitcher_throws_no_hl_formula
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
sp_player_formulas = get_pitching_player_formulas(sp_players_analysis, all_pitcher_stats)
rp_player_formulas = get_pitching_player_formulas(rp_players_analysis, all_pitcher_stats)

sp_players_sample = filter_cards_for_tourney(
    sample_tourneys,
    "STARTER"
)
rp_players_sample = filter_cards_for_tourney(
    sample_tourneys,
    "RELIEVER"
)

qualifying_sample_sp = list(filter(lambda player: player.stats_pitcher.pitcher_bf >= 50, sp_players_sample))
qualifying_sample_rp = list(filter(lambda player: player.stats_pitcher.pitcher_bf >= 50, rp_players_sample))
print(len(qualifying_sample_sp), "qualifying sp")
print(len(qualifying_sample_rp), "qualifying rp")

# Assumptions, 7000, 0.8, hr > so > bb
pa_max_cases = ["7000"]
pct_stats_cases = ["0.8"]
bat_stats = ["stu", "mov", "ctl"]

bat_stat_order_rams = {
    "stu": {
        "none": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "aw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ahw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "awh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "h": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "haw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hwa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.stu_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
    },
    "mov": {
        "none": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "aw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ahw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "awh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "h": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "haw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hwa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks - player.stats_pitcher.pitcher_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks - player.stats_pitcher.pitcher_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.mov_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_walks,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
    },
    "ctl": {
        "none": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "aw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ahw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "awh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "h": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "ha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "haw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hw": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "hwa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wa": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wah": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "w": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wh": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
            min_y_denom=30,
            should_use_cooks_distance=True
        ),
        "wha": RegressionAnalysisModel(
            get_x=lambda player: player.card_player.ctl_ovr, 
            get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks, 
            get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
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
        if stat == "stu":
            stat_fn = lambda player: player.card_player.stu_ovr
        elif stat == "ctl":
            stat_fn = lambda player: player.card_player.ctl_ovr
        elif stat == "mov":
            stat_fn = lambda player: player.card_player.mov_ovr

        bat_stats_cases[stat][stat_order] = {
            "throws_no_hl": get_pitcher_throws_no_hl_formula(sp_players_analysis, stat_fn, bat_stat_order_rams[stat][stat_order]),
            "throws_hl": get_pitcher_throws_hl_formula(sp_players_analysis, stat_fn, bat_stat_order_rams[stat][stat_order]),
        }

        batter_with_pos_to_batter_data[stat][stat_order] = {}
        for player in sp_players_analysis:
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
for stat_order in bat_stat_order_rams["ctl"]:
    orders_off_by[stat_order] = 0.0

bat_type_off_by = {
    "throws_no_hl": 0.0,
    "throws_hl": 0.0,
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

bats_sample_only = list(filter(lambda player: player.get_fielding_position() == 0, sp_players_sample))

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

f = open('output/pit_off_by.csv', 'w')
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

