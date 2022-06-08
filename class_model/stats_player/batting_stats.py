from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from class_model.BaseStatsPlayer import SingleLineStatsPlayer
from util.ip_math import add_ip


def __get_arm__(pos_num: int) -> Callable[[SingleLineStatsPlayer], int]:
    if pos_num >= 7:
        return lambda player: player.card_player.ofarm
    elif pos_num >= 3:
        return lambda player: player.card_player.ifarm
    return lambda player: player.card_player.carm

def __get_defense__(pos_num: int) -> Callable[[SingleLineStatsPlayer], int]:
    if pos_num == 2:
        return lambda player: player.card_player.defensec
    if pos_num == 3:
        return lambda player: player.card_player.defense1b
    if pos_num == 4:
        return lambda player: player.card_player.defense2b
    if pos_num == 5:
        return lambda player: player.card_player.defense3b
    if pos_num == 6:
        return lambda player: player.card_player.defensess
    if pos_num == 7:
        return lambda player: player.card_player.defenself
    if pos_num == 8:
        return lambda player: player.card_player.defensecf
    if pos_num == 9:
        return lambda player: player.card_player.defenserf
    if pos_num == 0:
        return 0

    raise Exception("Bad position number")


@dataclass
class BatterStats:
    get_rating_formula: Callable[[SingleLineStatsPlayer], int]
    get_stat_affected: Callable[[SingleLineStatsPlayer], int]
    get_stat_pa_affected: Callable[[SingleLineStatsPlayer], int]

batting_stats_formula_getters: Dict[str, BatterStats] = {
    "avk": BatterStats(
        get_rating_formula=lambda player: player.card_player.avk_ovr,
        get_stat_affected=lambda player: player.stats_batter.batter_strikeouts,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_intentional_walks
    ),
    "pow": BatterStats(
        get_rating_formula=lambda player: player.card_player.pow_ovr,
        get_stat_affected=lambda player: player.stats_batter.batter_homeruns,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_walks - player.stats_batter.batter_intentional_walks
    ),
    "eye": BatterStats(
        get_rating_formula=lambda player: player.card_player.eye_ovr,
        get_stat_affected=lambda player: player.stats_batter.batter_walks - player.stats_batter.batter_intentional_walks,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_intentional_walks
    ),
    "bab": BatterStats(
        get_rating_formula=lambda player: player.card_player.babip_ovr,
        get_stat_affected=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_strikeouts - player.stats_batter.batter_walks - player.stats_batter.batter_homeruns - player.stats_batter.batter_intentional_walks
    ),
    "gap": BatterStats(
        get_rating_formula=lambda player: player.card_player.gap_ovr,
        get_stat_affected=lambda player: player.stats_batter.batter_doubles + player.stats_batter.batter_triples,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples
    ),
    "triple": BatterStats(
        get_rating_formula=lambda player: player.card_player.speed,
        get_stat_affected=lambda player: player.stats_batter.batter_triples,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_doubles + player.stats_batter.batter_triples
    ),
    "sba": BatterStats(
        get_rating_formula=lambda player: player.card_player.speed,
        get_stat_affected=lambda player: player.stats_batter.batter_stolen_bases + player.stats_batter.batter_caught_stealing,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_walks + player.stats_batter.batter_hit_by_pitch
    ),
    "steal_rate": BatterStats(
        get_rating_formula=lambda player: player.card_player.steal,
        get_stat_affected=lambda player: player.stats_batter.batter_stolen_bases,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_stolen_bases + player.stats_batter.batter_caught_stealing
    ),
    "ubr": BatterStats(
        get_rating_formula=lambda player: player.card_player.baserunning,
        get_stat_affected=lambda player: player.stats_batter.batter_ubr,
        get_stat_pa_affected=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples
    ),
    "arm_runs": BatterStats(
        get_rating_formula=lambda player: __get_arm__(player.get_fielding_position()),
        get_stat_affected=lambda player: player.stats_fielder.fielding_arm_runs,
        get_stat_pa_affected=lambda player: player.stats_fielder.fielding_ip
    ),
    "frame_runs": BatterStats(
        get_rating_formula=lambda player: player.card_player.cabi,
        get_stat_affected=lambda player: player.stats_fielder.fielding_framing_runs if player.stats_fielder.fielding_position == 2 else 0,
        get_stat_pa_affected=lambda player: player.stats_fielder.fielding_ip if player.stats_fielder.fielding_position == 2 else 0
    ),
    "zr": BatterStats(
        get_rating_formula=lambda player: __get_defense__(player.get_fielding_position()),
        get_stat_affected=lambda player: player.stats_fielder.fielding_zr,
        get_stat_pa_affected=lambda player: player.stats_fielder.fielding_ip
    ),
    "sba_against": BatterStats(
        get_rating_formula=lambda player: player.card_player.carm,
        get_stat_affected=lambda player: player.stats_fielder.fielding_stolen_bases_against + player.stats_fielder.fielding_runners_thrown_out if player.stats_fielder.fielding_position == 2 else 0,
        get_stat_pa_affected=lambda player: player.stats_fielder.fielding_ip
    ),
    "cs_against": BatterStats(
        get_rating_formula=lambda player: player.card_player.carm,
        get_stat_affected=lambda player: player.stats_fielder.fielding_runners_thrown_out if player.stats_fielder.fielding_position == 2 else 0,
        get_stat_pa_affected=lambda player: player.stats_fielder.fielding_stolen_bases_against + player.stats_fielder.fielding_runners_thrown_out
    ),
}

def __fill_stat__(bs: BatterStats, player: SingleLineStatsPlayer, d: Dict[int, Tuple[int, int]], is_ip: bool):
    rating = bs.get_rating_formula(player)
    if rating not in d:
        d[rating] = (0, 0)

    if is_ip:
        d[rating] = (d[rating][0] + bs.get_stat_affected(player), add_ip(d[rating][1], bs.get_stat_pa_affected(player)))
    else:
        d[rating] = (d[rating][0] + bs.get_stat_affected(player), d[rating][1] + bs.get_stat_pa_affected(player))

__stats_to_handedness__ = ["avk", "pow", "eye", "bab", "gap"]

def get_batter_stats_for_players(players: List[SingleLineStatsPlayer]) -> Dict[str, any]:
    stats_for_players: Dict[str, any] = {}
    for k in batting_stats_formula_getters.keys():
        if k in __stats_to_handedness__:
            stats_for_players[k] = { "L": {}, "R": {}, "S": {} }
        else:
            stats_for_players[k] = {}
    for player in players:
        __fill_stat__(batting_stats_formula_getters["avk"], player, stats_for_players["avk"][player.card_player.bats], False)
        __fill_stat__(batting_stats_formula_getters["pow"], player, stats_for_players["pow"][player.card_player.bats], False)
        __fill_stat__(batting_stats_formula_getters["eye"], player, stats_for_players["eye"][player.card_player.bats], False)
        __fill_stat__(batting_stats_formula_getters["bab"], player, stats_for_players["bab"][player.card_player.bats], False)
        __fill_stat__(batting_stats_formula_getters["gap"], player, stats_for_players["gap"][player.card_player.bats], False)
        __fill_stat__(batting_stats_formula_getters["triple"], player, stats_for_players["triple"], False)
        __fill_stat__(batting_stats_formula_getters["sba"], player, stats_for_players["sba"], False)
        __fill_stat__(batting_stats_formula_getters["steal_rate"], player, stats_for_players["steal_rate"], False)
        __fill_stat__(batting_stats_formula_getters["ubr"], player, stats_for_players["ubr"], False)

        if player.get_fielding_position() > 1:
            __fill_stat__(batting_stats_formula_getters["arm_runs"], player, stats_for_players["arm_runs"], True)
            __fill_stat__(batting_stats_formula_getters["zr"], player, stats_for_players["zr"], True)
            __fill_stat__(batting_stats_formula_getters["frame_runs"], player, stats_for_players["frame_runs"], True)
            __fill_stat__(batting_stats_formula_getters["sba_against"], player, stats_for_players["sba_against"], True)
            __fill_stat__(batting_stats_formula_getters["cs_against"], player, stats_for_players["cs_against"], True)
    
    return stats_for_players