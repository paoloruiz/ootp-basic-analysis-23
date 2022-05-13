from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from class_model.BaseStatsPlayer import SingleLineStatsPlayer
from util.ip_math import add_ip


@dataclass
class PitcherStats:
    get_rating_formula: Callable[[SingleLineStatsPlayer], int]
    get_stat_affected: Callable[[SingleLineStatsPlayer], int]
    get_stat_pa_affected: Callable[[SingleLineStatsPlayer], int]

batting_stats_formula_getters: Dict[str, PitcherStats] = {
    "stu": PitcherStats(
        get_rating_formula=lambda player: player.card_player.stu_ovr,
        get_stat_affected=lambda player: player.stats_pitcher.pitcher_strikeouts,
        get_stat_pa_affected=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns
    ),
    "mov": PitcherStats(
        get_rating_formula=lambda player: player.card_player.mov_ovr,
        get_stat_affected=lambda player: player.stats_pitcher.pitcher_homeruns,
        get_stat_pa_affected=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch
    ),
    "ctl": PitcherStats(
        get_rating_formula=lambda player: player.card_player.ctl_ovr,
        get_stat_affected=lambda player: player.stats_pitcher.pitcher_walks,
        get_stat_pa_affected=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_homeruns
    ),
    "sba": PitcherStats(
        get_rating_formula=lambda player: player.card_player.hold,
        get_stat_affected=lambda player: player.stats_pitcher.pitcher_caught_stealing + player.stats_pitcher.pitcher_stolen_bases,
        get_stat_pa_affected=lambda player: player.stats_pitcher.pitcher_singles + player.stats_pitcher.pitcher_walks + player.stats_pitcher.pitcher_hit_by_pitch
    ),
    "cs": PitcherStats(
        get_rating_formula=lambda player: player.card_player.hold,
        get_stat_affected=lambda player: player.stats_pitcher.pitcher_caught_stealing,
        get_stat_pa_affected=lambda player: player.stats_pitcher.pitcher_caught_stealing + player.stats_pitcher.pitcher_stolen_bases
    ),
    "gidp": PitcherStats(
        get_rating_formula=lambda player: player.card_player.gb_type,
        get_stat_affected=lambda player: player.stats_pitcher.pitcher_double_plays,
        get_stat_pa_affected=lambda player: player.stats_pitcher.pitcher_ab - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_homeruns
    ),
    "bf_per_g": PitcherStats(
        get_rating_formula=lambda player: player.card_player.stamina,
        get_stat_affected=lambda player: player.stats_pitcher.pitcher_bf,
        get_stat_pa_affected=lambda player: player.stats_pitcher.pitcher_games
    ),
}

def __fill_stat__(ps: PitcherStats, player: SingleLineStatsPlayer, d: Dict[int, Tuple[int, int]], is_ip: bool):
    rating = ps.get_rating_formula(player)
    if rating not in d:
        d[rating] = (0, 0)

    if is_ip:
        d[rating] = (d[rating][0] + ps.get_stat_affected(player), add_ip(d[rating][1], ps.get_stat_pa_affected(player)))
    else:
        d[rating] = (d[rating][0] + ps.get_stat_affected(player), d[rating][1] + ps.get_stat_pa_affected(player))

__stats_to_handedness__ = ["stu", "mov", "ctl"]

def get_pitcher_stats_for_players(players: List[SingleLineStatsPlayer]) -> Dict[str, any]:
    stats_for_players: Dict[str, any] = {}
    for k in batting_stats_formula_getters.keys():
        if k in __stats_to_handedness__:
            stats_for_players[k] = { "L": {}, "R": {} }
        else:
            stats_for_players[k] = {}
    for player in players:
        __fill_stat__(batting_stats_formula_getters["stu"], player, stats_for_players["stu"][player.card_player.throws], False)
        __fill_stat__(batting_stats_formula_getters["mov"], player, stats_for_players["mov"][player.card_player.throws], False)
        __fill_stat__(batting_stats_formula_getters["ctl"], player, stats_for_players["ctl"][player.card_player.throws], False)
        __fill_stat__(batting_stats_formula_getters["sba"], player, stats_for_players["sba"], False)
        __fill_stat__(batting_stats_formula_getters["cs"], player, stats_for_players["cs"], False)
        __fill_stat__(batting_stats_formula_getters["gidp"], player, stats_for_players["gidp"], False)
        __fill_stat__(batting_stats_formula_getters["bf_per_g"], player, stats_for_players["bf_per_g"], False)
    
    return stats_for_players