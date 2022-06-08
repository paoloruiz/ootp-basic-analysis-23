from typing import List, Tuple, Callable
from analysis.determine_linear_weights import LinearWeightsFormulas, get_positional_adjustment
from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer
from class_model.BaseProjectedBatter import BaseProjectedBatter
from class_model.ProjectedPitcher import ProjectedPitcher
from class_model.global_stats.AllLeagueStats import LeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from util.ip_math import ip_to_ip_w_remainder

def get_batter_headers(war_func: Callable[[SingleLineStatsPlayer], float]) -> List[Tuple[str, Callable[[SingleLineStatsPlayer], any]]]:
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
        ["ZR", lambda x: float(x.get_prorated_zr())],
        ["Frame Runs", lambda x: float(x.get_prorated_frame_runs())],
        ["Arm Runs", lambda x: float(x.get_prorated_arm_runs())],
        ["fielding_runs", lambda x: float(x.get_prorated_arm_runs() + x.get_prorated_zr() + x.get_prorated_frame_runs())],
        ["WAR", war_func],
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
def get_sp_headers(war_func: Callable[[SingleLineStatsPlayer], float]) -> List[Tuple[str, Callable[[BaseStatsPlayer], any]]]:
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
        ["bf", lambda x: int(x.stats_pitcher.pitcher_bf)],
        ["ip", lambda x: float(x.stats_pitcher.pitcher_ip)],
        ["k/9", lambda x: float(x.stats_pitcher.pitcher_strikeouts / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["bb + hbp/9", lambda x: float((x.stats_pitcher.pitcher_walks + x.stats_pitcher.pitcher_hit_by_pitch) / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["hr/9", lambda x: float(x.stats_pitcher.pitcher_homeruns / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["whip", lambda x: float((x.stats_pitcher.pitcher_walks + x.stats_pitcher.pitcher_hit_by_pitch + x.stats_pitcher.pitcher_hits_against) / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip))],
        ["fip", lambda x: float(x.stats_pitcher.pitcher_fip)],
        ["era", lambda x: float(x.stats_pitcher.pitcher_earned_runs_against / ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) * 9)],
        ["ip/g", lambda x: float(ip_to_ip_w_remainder(x.stats_pitcher.pitcher_ip) / x.stats_pitcher.pitcher_games)],
        ["siera", lambda x: float(x.stats_pitcher.pitcher_siera)],
        ["war / 500 bf", war_func],
    ]

def get_rp_headers(war_func: Callable[[SingleLineStatsPlayer], float]) -> List[Tuple[str, Callable[[BaseStatsPlayer], any]]]:
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
        ["bf", lambda x: int(x.stats_pitcher.pitcher_bf)],
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
        ["war / 150 bf", war_func],
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
    ["pa", lambda x: int(x.tpbs.ovr.pa)],
    ["singles", lambda x: float(x.tpbs.ovr.singles)],
    ["doubles", lambda x: float(x.tpbs.ovr.doubles)],
    ["triples", lambda x: float(x.tpbs.ovr.triples)],
    ["homeruns", lambda x: float(x.tpbs.ovr.homeruns)],
    ["walks", lambda x: float(x.tpbs.ovr.walks)],
    ["strikeouts", lambda x: float(x.tpbs.ovr.strikeouts)],
    ["avg", lambda x: float((x.tpbs.ovr.singles + x.tpbs.ovr.doubles + x.tpbs.ovr.triples + x.tpbs.ovr.homeruns) / (x.tpbs.ovr.pa - x.tpbs.ovr.walks))],
    ["obp", lambda x: float((x.tpbs.ovr.singles + x.tpbs.ovr.doubles + x.tpbs.ovr.triples + x.tpbs.ovr.homeruns + x.tpbs.ovr.walks) / (x.tpbs.ovr.pa))],
    ["BABIP", lambda x: float((x.tpbs.ovr.singles + x.tpbs.ovr.doubles + x.tpbs.ovr.triples) / (x.tpbs.ovr.pa - x.tpbs.ovr.strikeouts - x.tpbs.ovr.homeruns - x.tpbs.ovr.walks))],
    ["wOBA", lambda x: float(x.tpbs.ovr.woba)],
    ["BatR", lambda x: float(x.tpbs.ovr.batr)],
    ["wSB", lambda x: float(x.tpbs.ovr.wsb)],
    ["UBR", lambda x: float(x.tpbs.ovr.ubr)],
    ["BsR", lambda x: float(x.tpbs.ovr.bsr)],
    ["ZR", lambda x: float(x.tpbs.ovr.zr)],
    ["Frame Runs", lambda x: float(x.tpbs.ovr.frame_runs)],
    ["Arm Runs", lambda x: float(x.tpbs.ovr.arm_runs)],
    ["Fielding Runs", lambda x: float(x.tpbs.ovr.fielding_runs)],
    ["WAR", lambda x: float(x.tpbs.ovr.war)],
    ["WAR vL" , lambda x: float(x.tpbs.vl.war)],
    ["WAR vR", lambda x: float(x.tpbs.vr.war)]
]
proj_batter_hidden_cols = [
    "throws",
    "con",
    "gap",
    "pow",
    "eye",
    "avk",
    "babip",
    "singles",
    "doubles",
    "triples",
    "homeruns",
    "walks",
    "strikeouts",
    "avg",
    "obp",
    "BABIP"
]

proj_pitcher_headers: List[Tuple[str, Callable[[ProjectedPitcher], any]]] = [
    ["cid", lambda x: x.cid],
    ["full_title", lambda x: x.card_player.full_title],
    ["team", lambda x: x.card_player.team],
    ["year", lambda x: int(x.card_player.year)],
    ["ovr", lambda x: int(x.card_player.ovr)],
    ["bats", lambda x: x.card_player.bats],
    ["throws", lambda x: x.card_player.throws],
    ["stu", lambda x: int(x.card_player.stu_ovr)],
    ["mov", lambda x: int(x.card_player.mov_ovr)],
    ["ctl", lambda x: int(x.card_player.ctl_ovr)],
    ["stm", lambda x: int(x.card_player.stamina)],
    ["bf", lambda x: float(x.bf)],
    ["k/9", lambda x: float(x.k_per_9)],
    ["bb + hbp/9", lambda x: float(x.bb_per_9)],
    ["hr/9", lambda x: float(x.hr_per_9)],
    ["ip/g", lambda x: float(x.ip_per_g)],
    ["fip", lambda x: float(x.fip)],
    ["war against (no other pitchers)", lambda x: (float(x.only_pit_war_against))],
    ["war against (per game)", lambda x: float(x.war_against)],
    ["war", lambda x: float(x.war)],
    ["war_with_relief", lambda x: float(x.war_with_relief)]
]