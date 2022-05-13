from dataclasses import dataclass
from typing import Dict, List

from util.ip_math import add_ip, ip_to_ip_w_remainder


@dataclass
class StatsFielder:
    fielding_position: int = 0
    fielding_games: int = 0
    fielding_games_started: int = 0
    fielding_total_chances: int = 0
    fielding_assists: int = 0
    fielding_putouts: int = 0
    fielding_errors: int = 0
    fielding_double_plays: int = 0
    fielding_triple_plays: int = 0
    fielding_pct: float = 0.0
    fielding_rng: float = 0.0
    fielding_zr: float = 0.0
    fielding_eff: float = 0.0
    fielding_stolen_bases_against: int = 0
    fielding_runners_thrown_out: int = 0
    fielding_ip: float = 0.0
    fielding_passed_balls: int = 0
    fielding_catcher_earned_runs: int = 0
    fielding_reg_balls_in_zone: int = 0
    fielding_reg_balls_in_zone_fielded: int = 0
    fielding_likely_balls_in_zone: int = 0
    fielding_likely_balls_in_zone_fielded: int = 0
    fielding_even_balls_in_zone: int = 0
    fielding_even_balls_in_zone_fielded: int = 0
    fielding_unlikely_balls_in_zone: int = 0
    fielding_unlikely_balls_in_zone_fielded: int = 0
    fielding_remote_balls_in_zone: int = 0
    fielding_remote_balls_in_zone_fielded: int = 0
    fielding_impossible_balls_in_zone: int = 0
    fielding_framing_runs: float = 0.0
    fielding_arm_runs: float = 0.0

def __safe_int__(possible_int: str):
    try: 
        return int(possible_int)
    except:
        return 0

def __safe_float__(possible_float: str):
    try:
        return float(possible_float)
    except:
        return 0.0

def __search_with_reasonable_error__(headers: List[str], index_name: str, starting_idx: int = 0):
    try:
        return headers.index(index_name, starting_idx)
    except ValueError:
        raise Exception(index_name + " not included in headers: " + str(headers))

def get_fielder_header_indices(headers: List[str]) -> Dict[str, int]:
    header_indices = {}
    
    fielding_starting_index = __search_with_reasonable_error__(headers, "SIERA")

    header_indices["fld_g_index"] = __search_with_reasonable_error__(headers, "G", fielding_starting_index)
    header_indices["fld_gs_index"] = __search_with_reasonable_error__(headers, "GS", fielding_starting_index)
    header_indices["fld_tc_index"] = __search_with_reasonable_error__(headers, "TC", fielding_starting_index)
    header_indices["fld_ast_index"] = __search_with_reasonable_error__(headers, "A", fielding_starting_index)
    header_indices["fld_po_index"] = __search_with_reasonable_error__(headers, "PO", fielding_starting_index)
    header_indices["fld_err_index"] = __search_with_reasonable_error__(headers, "E", fielding_starting_index)
    header_indices["fld_db_index"] = __search_with_reasonable_error__(headers, "DP", fielding_starting_index)
    header_indices["fld_tp_index"] = __search_with_reasonable_error__(headers, "TP", fielding_starting_index)
    header_indices["fld_pct_index"] = __search_with_reasonable_error__(headers, "PCT", fielding_starting_index)
    header_indices["fld_rng_index"] = __search_with_reasonable_error__(headers, "RNG", fielding_starting_index)
    header_indices["fld_zr_index"] = __search_with_reasonable_error__(headers, "ZR", fielding_starting_index)
    header_indices["fld_eff_index"] = __search_with_reasonable_error__(headers, "EFF", fielding_starting_index)
    header_indices["fld_sba_index"] = __search_with_reasonable_error__(headers, "SBA", fielding_starting_index)
    header_indices["fld_rto_index"] = __search_with_reasonable_error__(headers, "RTO", fielding_starting_index)
    header_indices["fld_ip_index"] = __search_with_reasonable_error__(headers, "IP", fielding_starting_index)
    header_indices["fld_pb_index"] = __search_with_reasonable_error__(headers, "PB", fielding_starting_index)
    header_indices["fld_cer_index"] = __search_with_reasonable_error__(headers, "CER", fielding_starting_index)
    header_indices["fld_rbiz_index"] = __search_with_reasonable_error__(headers, "BIZ-R", fielding_starting_index)
    header_indices["fld_rbizm_index"] = __search_with_reasonable_error__(headers, "BIZ-Rm", fielding_starting_index)
    header_indices["fld_lbiz_index"] = __search_with_reasonable_error__(headers, "BIZ-L", fielding_starting_index)
    header_indices["fld_lbizm_index"] = __search_with_reasonable_error__(headers, "BIZ-Lm", fielding_starting_index)
    header_indices["fld_ebiz_index"] = __search_with_reasonable_error__(headers, "BIZ-E", fielding_starting_index)
    header_indices["fld_ebizm_index"] = __search_with_reasonable_error__(headers, "BIZ-Em", fielding_starting_index)
    header_indices["fld_ubiz_index"] = __search_with_reasonable_error__(headers, "BIZ-U", fielding_starting_index)
    header_indices["fld_ubizm_index"] = __search_with_reasonable_error__(headers, "BIZ-Um", fielding_starting_index)
    header_indices["fld_zbiz_index"] = __search_with_reasonable_error__(headers, "BIZ-Z", fielding_starting_index)
    header_indices["fld_zbizm_index"] = __search_with_reasonable_error__(headers, "BIZ-Zm", fielding_starting_index)
    header_indices["fld_ibiz_index"] = __search_with_reasonable_error__(headers, "BIZ-I", fielding_starting_index)
    header_indices["fld_frm_index"] = __search_with_reasonable_error__(headers, "FRM", fielding_starting_index)
    header_indices["fld_arm_index"] = __search_with_reasonable_error__(headers, "ARM", fielding_starting_index)

    return header_indices

def new_stats_fielder(header_indices: Dict[str, int], position_number: int, play_line: List[str]) -> StatsFielder:
    return StatsFielder(
        fielding_position=position_number,
        fielding_games=__safe_int__(play_line[header_indices["fld_g_index"]]),
        fielding_games_started=__safe_int__(play_line[header_indices["fld_gs_index"]]),
        fielding_total_chances=__safe_int__(play_line[header_indices["fld_tc_index"]]),
        fielding_assists=__safe_int__(play_line[header_indices["fld_ast_index"]]),
        fielding_putouts=__safe_int__(play_line[header_indices["fld_po_index"]]),
        fielding_errors=__safe_int__(play_line[header_indices["fld_err_index"]]),
        fielding_double_plays=__safe_int__(play_line[header_indices["fld_db_index"]]),
        fielding_triple_plays=__safe_int__(play_line[header_indices["fld_tp_index"]]),
        fielding_pct=__safe_float__(play_line[header_indices["fld_pct_index"]]),
        fielding_rng=__safe_float__(play_line[header_indices["fld_rng_index"]]),
        fielding_zr=__safe_float__(play_line[header_indices["fld_zr_index"]]),
        fielding_eff=__safe_float__(play_line[header_indices["fld_eff_index"]]),
        fielding_stolen_bases_against=__safe_int__(play_line[header_indices["fld_sba_index"]]),
        fielding_runners_thrown_out=__safe_int__(play_line[header_indices["fld_rto_index"]]),
        fielding_ip=__safe_float__(play_line[header_indices["fld_ip_index"]]),
        fielding_passed_balls=__safe_int__(play_line[header_indices["fld_pb_index"]]),
        fielding_catcher_earned_runs=__safe_int__(play_line[header_indices["fld_cer_index"]]),
        fielding_reg_balls_in_zone=__safe_int__(play_line[header_indices["fld_rbiz_index"]]),
        fielding_reg_balls_in_zone_fielded=__safe_int__(play_line[header_indices["fld_rbizm_index"]]),
        fielding_likely_balls_in_zone=__safe_int__(play_line[header_indices["fld_lbiz_index"]]),
        fielding_likely_balls_in_zone_fielded=__safe_int__(play_line[header_indices["fld_lbizm_index"]]),
        fielding_even_balls_in_zone=__safe_int__(play_line[header_indices["fld_ebiz_index"]]),
        fielding_even_balls_in_zone_fielded=__safe_int__(play_line[header_indices["fld_ebizm_index"]]),
        fielding_unlikely_balls_in_zone=__safe_int__(play_line[header_indices["fld_ubiz_index"]]),
        fielding_unlikely_balls_in_zone_fielded=__safe_int__(play_line[header_indices["fld_ubizm_index"]]),
        fielding_remote_balls_in_zone=__safe_int__(play_line[header_indices["fld_zbiz_index"]]),
        fielding_remote_balls_in_zone_fielded=__safe_int__(play_line[header_indices["fld_zbizm_index"]]),
        fielding_impossible_balls_in_zone=__safe_int__(play_line[header_indices["fld_ibiz_index"]]),
        fielding_framing_runs=__safe_float__(play_line[header_indices["fld_frm_index"]]),
        fielding_arm_runs=__safe_float__(play_line[header_indices["fld_arm_index"]])
    )
    
def __weighted_avg__(a_stat, a_weight, b_stat, b_weight):
    return (a_stat * a_weight + b_stat * b_weight) / (a_weight + b_weight) if (a_weight + b_weight) > 0 else 0

def merge_stats_fielder(a: StatsFielder, b: StatsFielder) -> StatsFielder:
    c = StatsFielder()

    c.fielding_position = a.fielding_position
    c.fielding_games = a.fielding_games + b.fielding_games
    c.fielding_games_started = a.fielding_games_started + b.fielding_games_started
    c.fielding_total_chances = a.fielding_total_chances + b.fielding_total_chances
    c.fielding_assists = a.fielding_assists + b.fielding_assists
    c.fielding_putouts = a.fielding_putouts + b.fielding_putouts
    c.fielding_errors = a.fielding_errors + b.fielding_errors
    c.fielding_double_plays = a.fielding_double_plays + b.fielding_double_plays
    c.fielding_double_plays = a.fielding_double_plays + b.fielding_double_plays
    c.fielding_pct = __weighted_avg__(a.fielding_pct, ip_to_ip_w_remainder(a.fielding_ip), b.fielding_pct, ip_to_ip_w_remainder(b.fielding_ip))
    c.fielding_rng = __weighted_avg__(a.fielding_rng, ip_to_ip_w_remainder(a.fielding_ip), b.fielding_rng, ip_to_ip_w_remainder(b.fielding_ip))
    c.fielding_zr = a.fielding_zr + b.fielding_zr
    c.fielding_eff = __weighted_avg__(a.fielding_eff, ip_to_ip_w_remainder(a.fielding_ip), b.fielding_eff, ip_to_ip_w_remainder(b.fielding_ip))
    c.fielding_stolen_bases_against = a.fielding_stolen_bases_against + b.fielding_stolen_bases_against
    c.fielding_runners_thrown_out = a.fielding_runners_thrown_out + b.fielding_runners_thrown_out
    c.fielding_ip = add_ip(a.fielding_ip, b.fielding_ip)
    c.fielding_passed_balls = a.fielding_passed_balls + b.fielding_passed_balls
    c.fielding_catcher_earned_runs = a.fielding_catcher_earned_runs + b.fielding_catcher_earned_runs
    c.fielding_reg_balls_in_zone = a.fielding_reg_balls_in_zone + b.fielding_reg_balls_in_zone
    c.fielding_reg_balls_in_zone_fielded = a.fielding_reg_balls_in_zone_fielded + b.fielding_reg_balls_in_zone_fielded
    c.fielding_likely_balls_in_zone = a.fielding_likely_balls_in_zone + b.fielding_likely_balls_in_zone
    c.fielding_likely_balls_in_zone_fielded = a.fielding_likely_balls_in_zone_fielded + b.fielding_likely_balls_in_zone_fielded
    c.fielding_even_balls_in_zone = a.fielding_even_balls_in_zone + b.fielding_even_balls_in_zone
    c.fielding_even_balls_in_zone_fielded = a.fielding_even_balls_in_zone_fielded + b.fielding_even_balls_in_zone_fielded
    c.fielding_unlikely_balls_in_zone = a.fielding_unlikely_balls_in_zone + b.fielding_unlikely_balls_in_zone
    c.fielding_unlikely_balls_in_zone_fielded = a.fielding_unlikely_balls_in_zone_fielded + b.fielding_unlikely_balls_in_zone_fielded
    c.fielding_remote_balls_in_zone = a.fielding_remote_balls_in_zone + b.fielding_remote_balls_in_zone
    c.fielding_remote_balls_in_zone_fielded = a.fielding_remote_balls_in_zone_fielded + b.fielding_remote_balls_in_zone_fielded
    c.fielding_impossible_balls_in_zone = a.fielding_impossible_balls_in_zone + b.fielding_impossible_balls_in_zone
    c.fielding_framing_runs = a.fielding_framing_runs + b.fielding_framing_runs
    c.fielding_arm_runs = a.fielding_arm_runs + b.fielding_arm_runs

    return c