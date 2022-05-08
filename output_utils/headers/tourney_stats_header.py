from typing import List, Tuple, Callable
from analysis.determine_linear_weights import LinearWeightsFormulas, get_positional_adjustment
from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer
from class_model.BaseProjectedBatter import BaseProjectedBatter
from class_model.global_stats.AllLeagueStats import LeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from util.ip_math import ip_to_ip_w_remainder

def get_batter_headers(woba_constants: LinearWeightsFormulas, league_stats: LeagueStats) -> List[Tuple[str, Callable[[SingleLineStatsPlayer], any]]]:
    def calculate_war(player: SingleLineStatsPlayer) -> float:
        batr = (player.stats_batter.batter_batting_runs / player.stats_batter.batter_pa) * player.get_assumed_pa()
        basr = (player.stats_batter.batter_base_running_runs / player.stats_batter.batter_pa) * player.get_assumed_pa()
        fielding_runs = player.get_prorated_zr() + player.get_prorated_arm_runs() + player.get_prorated_frame_runs()
        positional_adjustment = player.get_assumed_ip() / (9 * 162) * get_positional_adjustment(player.get_fielding_position())
        replacement_level_adjustment = league_stats.get_replacement_level_runs_per_pa() * player.get_assumed_pa()

        return (batr + basr + fielding_runs + positional_adjustment + replacement_level_adjustment) / woba_constants.runs_per_win
    return [
        ["cid", lambda x: x.get_cid_with_pos()],
        ["full_title", lambda x: x.card_player.full_title],
        ["position", lambda x: x.position],
        ["team", lambda x: x.card_player.team],
        ["year", lambda x: int(x.card_player.year)],
        ["ovr", lambda x: int(x.card_player.ovr)],
        ["bats", lambda x: x.card_player.bats],
        ["throws", lambda x: x.card_player.throws],
        ["con", lambda x: int(x.card_player.con_ovr)],
        ["gap", lambda x: int(x.card_player.gap_ovr)],
        ["pow", lambda x: int(x.card_player.pow_ovr)],
        ["eye", lambda x: int(x.card_player.eye_ovr)],
        ["avk", lambda x: int(x.card_player.avk_ovr)],
        ["babip", lambda x: int(x.card_player.babip_ovr)],
        ["cx", lambda x: int(x.card_player.defensec)],
        ["1bx", lambda x: int(x.card_player.defense1b)],
        ["2bx", lambda x: int(x.card_player.defense2b)],
        ["3bx", lambda x: int(x.card_player.defense3b)],
        ["ssx", lambda x: int(x.card_player.defensess)],
        ["lfx", lambda x: int(x.card_player.defenself)],
        ["cfx", lambda x: int(x.card_player.defensecf)],
        ["rfx", lambda x: int(x.card_player.defenserf)],
        ["fielding position", lambda x: int(x.get_fielding_position())],
        ["pa", lambda x: int(x.stats_batter.batter_pa)],
        ["wOBA", lambda x: float(x.stats_batter.batter_woba)],
        ["wRC", lambda x: float((x.stats_batter.batter_wrc / x.stats_batter.batter_pa) * x.get_assumed_pa())],
        ["wRAA", lambda x: float((x.stats_batter.batter_wraa / x.stats_batter.batter_pa) * x.get_assumed_pa())],
        ["BatR", lambda x: float((x.stats_batter.batter_batting_runs / x.stats_batter.batter_pa) * x.get_assumed_pa())],
        ["wSB", lambda x: float((x.stats_batter.batter_weighted_stolen_bases / x.stats_batter.batter_pa) * x.get_assumed_pa())],
        ["UBR", lambda x: float((x.stats_batter.batter_ubr / x.stats_batter.batter_pa) * x.get_assumed_pa())],
        ["BsR", lambda x: float((x.stats_batter.batter_base_running_runs / x.stats_batter.batter_pa) * x.get_assumed_pa())],
        ["ZR", lambda x: float((x.get_prorated_zr()))],
        ["Frame Runs", lambda x: float((x.get_prorated_frame_runs()))],
        ["Arm Runs", lambda x: float((x.get_prorated_arm_runs()))],
        ["WAR", calculate_war],
    ]
batter_hidden_cols = [
    "throws",
    "con",
    "gap",
    "pow",
    "eye",
    "avk",
    "babip"
]
def get_sp_headers(woba_constants: LinearWeightsFormulas, pitcher_stats: PitcherStats) -> List[Tuple[str, Callable[[BaseStatsPlayer], any]]]:
    def get_war_against(player: SingleLineStatsPlayer):
        bf = player.stats_pitcher.pitcher_bf
        singles_against = player.stats_pitcher.pitcher_singles / bf * 500
        doubles_against = player.stats_pitcher.pitcher_doubles / bf * 500
        triples_against = player.stats_pitcher.pitcher_triples / bf * 500
        homeruns_against = player.stats_pitcher.pitcher_homeruns / bf * 500
        walks_against = (player.stats_pitcher.pitcher_walks - player.stats_pitcher.pitcher_intentional_walks) / bf * 500
        hbp_against = pitcher_stats.get_hbp_rate(player.card_player) * 500

        stolen_bases_against = player.stats_pitcher.pitcher_stolen_bases / bf * 500
        caught_stealing_against = player.stats_pitcher.pitcher_caught_stealing / bf * 500

        wraa = woba_constants.woba_to_wraa_per_pa(woba_constants.woba_mult_by_pa_from_hits(walks_against, hbp_against, singles_against, doubles_against, triples_against, homeruns_against) / 500) * 500
        wsb = woba_constants.wsb_from_steal_stats(stolen_bases_against, caught_stealing_against)

        return (wraa + wsb) / woba_constants.runs_per_win
    return [
        ["cid", lambda x: x.cid],
        ["full_title", lambda x: x.card_player.full_title],
        ["position", lambda x: x.position],
        ["team", lambda x: x.card_player.team],
        ["year", lambda x: int(x.card_player.year)],
        ["ovr", lambda x: int(x.card_player.ovr)],
        ["bats", lambda x: x.card_player.bats],
        ["throws", lambda x: x.card_player.throws],
        ["stu", lambda x: int(x.card_player.stu_ovr)],
        ["mov", lambda x: int(x.card_player.mov_ovr)],
        ["ctl", lambda x: int(x.card_player.ctl_ovr)],
        ["stm", lambda x: int(x.card_player.stamina)],
        ["bf", lambda x: int(x.card_player.stamina)],
        ["ip", lambda x: float(x.stats_pitcher.pitcher_ip)],
        ["k/9", lambda x: float(x.stats_pitcher.pitcher_strikeouts / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["bb + hbp/9", lambda x: float((x.stats_pitcher.pitcher_walks + x.stats_pitcher.pitcher_hit_by_pitch) / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["hr/9", lambda x: float(x.stats_pitcher.pitcher_homeruns / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["whip", lambda x: float((x.stats_pitcher.pitcher_walks + x.stats_pitcher.pitcher_hit_by_pitch + x.stats_pitcher.pitcher_hits_against) / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip))],
        ["fip", lambda x: float(x.stats_pitcher.pitcher_fip)],
        ["era", lambda x: float(x.stats_pitcher.pitcher_earned_runs_against / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["ip/g", lambda x: float(ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) / x.stats_pitcher.pitcher_games)],
        ["siera", lambda x: float(x.stats_pitcher.pitcher_siera)],
        ["war / 500 bf", get_war_against],
    ]

def get_rp_headers(woba_constants: LinearWeightsFormulas, pitcher_stats: PitcherStats) -> List[Tuple[str, Callable[[BaseStatsPlayer], any]]]:
    def get_war_against(player: SingleLineStatsPlayer):
        bf = player.stats_pitcher.pitcher_bf
        singles_against = player.stats_pitcher.pitcher_singles / bf * 150
        doubles_against = player.stats_pitcher.pitcher_doubles / bf * 150
        triples_against = player.stats_pitcher.pitcher_triples / bf * 150
        homeruns_against = player.stats_pitcher.pitcher_homeruns / bf * 150
        walks_against = (player.stats_pitcher.pitcher_walks - player.stats_pitcher.pitcher_intentional_walks) / bf * 150
        hbp_against = pitcher_stats.get_hbp_rate(player.card_player) * 150

        stolen_bases_against = player.stats_pitcher.pitcher_stolen_bases / bf * 150
        caught_stealing_against = player.stats_pitcher.pitcher_caught_stealing / bf * 150

        wraa = woba_constants.woba_to_wraa_per_pa(woba_constants.woba_mult_by_pa_from_hits(walks_against, hbp_against, singles_against, doubles_against, triples_against, homeruns_against) / 150) * 150
        wsb = woba_constants.wsb_from_steal_stats(stolen_bases_against, caught_stealing_against)

        return (wraa + wsb) / woba_constants.runs_per_win
    return [
        ["cid", lambda x: x.cid],
        ["full_title", lambda x: x.card_player.full_title],
        ["position", lambda x: x.position],
        ["team", lambda x: x.card_player.team],
        ["year", lambda x: int(x.card_player.year)],
        ["ovr", lambda x: int(x.card_player.ovr)],
        ["bats", lambda x: x.card_player.bats],
        ["throws", lambda x: x.card_player.throws],
        ["stu", lambda x: int(x.card_player.stu_ovr)],
        ["mov", lambda x: int(x.card_player.mov_ovr)],
        ["ctl", lambda x: int(x.card_player.ctl_ovr)],
        ["stm", lambda x: int(x.card_player.stamina)],
        ["bf", lambda x: int(x.card_player.stamina)],
        ["ip", lambda x: float(x.stats_pitcher.pitcher_ip)],
        ["k/9", lambda x: float(x.stats_pitcher.pitcher_strikeouts / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["bb + hbp/9", lambda x: float((x.stats_pitcher.pitcher_walks + x.stats_pitcher.pitcher_hit_by_pitch) / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["hr/9", lambda x: float(x.stats_pitcher.pitcher_homeruns / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["whip", lambda x: float((x.stats_pitcher.pitcher_walks + x.stats_pitcher.pitcher_hit_by_pitch + x.stats_pitcher.pitcher_hits_against) / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip))],
        ["fip", lambda x: float(x.stats_pitcher.pitcher_fip)],
        ["era", lambda x: float(x.stats_pitcher.pitcher_earned_runs_against / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["ip/g", lambda x: float(ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) / x.stats_pitcher.pitcher_games)],
        ["siera", lambda x: float(x.stats_pitcher.pitcher_siera)],
        ["pLi", lambda x: float(x.stats_pitcher.pitcher_pli)],
        ["war / 150 bf", get_war_against],
    ]

proj_batter_headers: List[Tuple[str, Callable[[BaseProjectedBatter], any]]] = [
    ["cid", lambda x: x.cid],
    ["full_title", lambda x: x.card_player.full_title],
    ["position", lambda x: x.position],
    ["team", lambda x: x.card_player.team],
    ["year", lambda x: int(x.card_player.year)],
    ["ovr", lambda x: int(x.card_player.ovr)],
    ["bats", lambda x: x.card_player.bats],
    ["throws", lambda x: x.card_player.throws],
    ["con", lambda x: int(x.card_player.con_ovr)],
    ["gap", lambda x: int(x.card_player.gap_ovr)],
    ["pow", lambda x: int(x.card_player.pow_ovr)],
    ["eye", lambda x: int(x.card_player.eye_ovr)],
    ["avk", lambda x: int(x.card_player.avk_ovr)],
    ["babip", lambda x: int(x.card_player.babip_ovr)],
    ["cx", lambda x: int(x.card_player.defensec)],
    ["1bx", lambda x: int(x.card_player.defense1b)],
    ["2bx", lambda x: int(x.card_player.defense2b)],
    ["3bx", lambda x: int(x.card_player.defense3b)],
    ["ssx", lambda x: int(x.card_player.defensess)],
    ["lfx", lambda x: int(x.card_player.defenself)],
    ["cfx", lambda x: int(x.card_player.defensecf)],
    ["rfx", lambda x: int(x.card_player.defenserf)],
    ["pa", lambda x: int(x.pa)],
    ["wOBA", lambda x: float(x.woba)],
    ["BatR", lambda x: float(x.batr)],
    ["wSB", lambda x: float(x.wsb)],
    ["UBR", lambda x: float(x.ubr)],
    ["BsR", lambda x: float(x.bsr)],
    ["Fielding Runs", lambda x: float(x.fielding_runs)],
    ["WAR", lambda x: float(x.war)]
]
proj_batter_hidden_cols = [
    "throws",
    "con",
    "gap",
    "pow",
    "eye",
    "avk",
    "babip"
]