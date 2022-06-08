from typing import Dict, List
from analysis.determine_batting_player import get_batting_player_formulas
from analysis.determine_linear_weights import get_woba_constants
from analysis.determine_pitching_player import get_pitching_player_formulas
from analysis.lin_weights_modifiers import LeagueLWM, LinearWeightsModifiers
from analysis.war_funcs import get_batter_war_func, get_pitcher_war_func
from class_model.BaseProjectedBatter import generate_projected_batters
from class_model.BaseStatsPlayer import BaseStatsPlayer
from class_model.ProjectedPitcher import ProjectedPitcher, generate_projected_pitchers
from class_model.global_stats.AllLeagueStats import AllLeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from class_model.league_stats.league_stats import IndividualLeagueStats
from class_model.league_stats.top_team_pitcher_analysis import analyze_league_pitching
from class_model.stats_player.batting_stats import get_batter_stats_for_players
from class_model.stats_player.filter_cards import filter_cards_for_tourney
from class_model.stats_player.pitching_stats import get_pitcher_stats_for_players
from class_model.load_players import load_card_players
from output_utils.csvwriter import CsvWriter
from util.load_tourney_stats_players import load_tourney_stats_players_flat

pdmods = LeagueLWM(
    batting=LinearWeightsModifiers(),
    pitching=LinearWeightsModifiers()
)

all_league_stats = AllLeagueStats()
all_pitcher_stats = PitcherStats()
individual_league_stats = IndividualLeagueStats()

base_card_players = load_card_players()

tourney_types: Dict[str, List[Dict[str, BaseStatsPlayer]]] = load_tourney_stats_players_flat(base_card_players, all_league_stats, all_pitcher_stats, individual_league_stats=individual_league_stats, ttype="pd")

batter_players = filter_cards_for_tourney(
    tourney_types["pd"],
    "BATTER"
)
sp_players = filter_cards_for_tourney(
    tourney_types["pd"],
    "STARTER"
)
rp_players = filter_cards_for_tourney(
    tourney_types["pd"],
    "RELIEVER"
)

woba_constants = get_woba_constants(batter_players, all_league_stats.league_stats["pd"])

batting_player_formulas = get_batting_player_formulas(batter_players)
sp_player_formulas = get_pitching_player_formulas(sp_players, all_pitcher_stats)
rp_player_formulas = get_pitching_player_formulas(rp_players, all_pitcher_stats)

possible_players = list(base_card_players.values())

batter_stats_for_projection: Dict[str, any] = get_batter_stats_for_players(batter_players)
sp_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(sp_players)
rp_stats_for_projection: Dict[str, any] = get_pitcher_stats_for_players(rp_players)

projected_batters = generate_projected_batters(
    players=possible_players,
    linear_weights_formulas=woba_constants,
    batting_player_formulas=batting_player_formulas,
    batter_stats_for_players=batter_stats_for_projection,
    platoon_splits=individual_league_stats.get_platoon_splits("pd"),
    league_stats=all_league_stats.league_stats["pd"],
    lwm=pdmods.batting
)
projected_batters.sort(key=lambda pd: pd.tpbs.ovr.war, reverse=True)

possible_sp = list(filter(lambda p: p.stu_ovr > 10 and p.defensep > 10 and p.stamina > 40, possible_players))
projected_sp = generate_projected_pitchers(
    players=possible_sp,
    linear_weights_formulas=woba_constants,
    pitcher_stats=all_pitcher_stats,
    projected_pitching_formulas=sp_player_formulas,
    pitcher_stats_for_players=sp_stats_for_projection,
    platoon_splits=individual_league_stats.get_platoon_splits("pd"),
    lwm=pdmods.pitching
)
projected_sp.sort(key=lambda pd: pd.war_against)

projected_rp = generate_projected_pitchers(
    players=possible_players,
    linear_weights_formulas=woba_constants,
    pitcher_stats=all_pitcher_stats,
    projected_pitching_formulas=rp_player_formulas,
    pitcher_stats_for_players=rp_stats_for_projection,
    platoon_splits=individual_league_stats.get_platoon_splits("pd"),
    lwm=pdmods.pitching
)
projected_rp.sort(key=lambda pd: pd.war)

csv_writer = CsvWriter()
csv_writer.record(["full title", "cid", "pos", "war", "wsb+ubr", "pos"])
for batter in projected_batters:
    csv_writer.record([batter.card_player.full_title, batter.card_player.cid, batter.position, batter.tpbs.ovr.war, batter.tpbs.ovr.wsb + batter.tpbs.ovr.ubr, batter.card_player.position])

for sp in projected_sp:
    csv_writer.record([sp.card_player.full_title, sp.card_player.cid, 10, sp.war_with_relief, 0.0, sp.card_player.position])

for rp in projected_rp:
    csv_writer.record([rp.card_player.full_title, rp.card_player.cid, 11, rp.war, 0.0, rp.card_player.position])

f = open("output/pddraftplayers.csv", "w")
f.write(csv_writer.getCSV())
f.close()

def __sp_filter_fn__(player: ProjectedPitcher) -> bool:
    if player.card_player.defensep < 11:
        return False

    if player.card_player.stu_ovr < 20:
        return False

    if " SP " in player.card_player.full_title:
        return True

    return player.card_player.stamina  >= 60

possible_c = list(filter(lambda player: player.card_player.defensec > 35 and player.position == 2, projected_batters))
possible_1b = list(filter(lambda player: player.card_player.defense1b > 35 and player.position == 3, projected_batters))
possible_2b = list(filter(lambda player: player.card_player.defense2b > 35 and player.position == 4, projected_batters))
possible_3b = list(filter(lambda player: player.card_player.defense3b > 35 and player.position == 5, projected_batters))
possible_ss = list(filter(lambda player: player.card_player.defensess > 35 and player.position == 6, projected_batters))
possible_lf = list(filter(lambda player: player.card_player.defenself > 35 and player.position == 7, projected_batters))
possible_cf = list(filter(lambda player: player.card_player.defensecf > 35 and player.position == 8, projected_batters))
possible_rf = list(filter(lambda player: player.card_player.defenserf > 35 and player.position == 9, projected_batters))
possible_dh = list(filter(lambda player: player.card_player.con_ovr > 45 and player.position == 0, projected_batters))
possible_sp = list(filter(__sp_filter_fn__, projected_sp))
possible_rp = list(filter(lambda player: player.card_player.defensep > 10 and player.card_player.stu_ovr > 20, projected_rp))

ovr_filters = {
    "diamond": lambda player: player.card_player.ovr >= 90 and player.card_player.ovr < 100,
    "gold": lambda player: player.card_player.ovr >= 80 and player.card_player.ovr < 90,
    "silver": lambda player: player.card_player.ovr >= 70 and player.card_player.ovr < 80,
    "bronze": lambda player: player.card_player.ovr >= 60 and player.card_player.ovr < 70,
    "iron": lambda player: player.card_player.ovr >= 40 and player.card_player.ovr < 60,
}

csv_writer_avg_levels = CsvWriter()
csv_writer_avg_levels.record(["level", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "sp", "rp"])

def __avg__(lst: List[float]) -> float:
    return sum(lst) / len(lst)
for level, flt in ovr_filters.items():
    ps_c = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_c)))
    ps_1b = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_1b)))
    ps_2b = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_2b)))
    ps_3b = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_3b)))
    ps_ss = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_ss)))
    ps_lf = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_lf)))
    ps_cf = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_cf)))
    ps_rf = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_rf)))
    ps_dh = list(map(lambda p: p.tpbs.ovr.war, filter(flt, possible_dh)))
    ps_sp = list(map(lambda p: p.war_with_relief, filter(flt, possible_sp)))
    ps_rp = list(map(lambda p: p.war, filter(flt, possible_rp)))

    csv_writer_avg_levels.record([level, __avg__(ps_c), __avg__(ps_1b), __avg__(ps_2b), __avg__(ps_3b), __avg__(ps_ss), __avg__(ps_lf), __avg__(ps_cf), __avg__(ps_rf), __avg__(ps_dh), __avg__(ps_sp), __avg__(ps_rp)])
f = open("output/pddraft_levels.csv", "w")
f.write(csv_writer_avg_levels.getCSV())
f.close()