from dataclasses import dataclass
from typing import List

from class_model.BaseStatsPlayer import SingleLineStatsPlayer
from class_model.global_stats.AllLeagueStats import LeagueStats
from util.ip_math import ip_to_ip_w_remainder

@dataclass
class WobaWeights:
    woba_scale: float = 0.0
    woba_bb: float = 0.0
    woba_hb: float = 0.0
    woba_1b: float = 0.0
    woba_2b: float = 0.0
    woba_3b: float = 0.0
    woba_hr: float = 0.0
    woba_sb: float = 0.0
    woba_cs: float = 0.0
    woba_avg: float = 0.0
    lg_wsb: float = 0.0


def get_tango_woba_factors(players: List[SingleLineStatsPlayer], league_stats: LeagueStats) -> WobaWeights:
    r_per_out = league_stats.get_runs_per_out()

    run_bb = r_per_out + 0.14
    run_hb = run_bb + 0.025
    run_1b = run_bb + 0.155
    run_2b = run_1b + 0.3
    run_3b = run_2b + 0.27
    run_hr = 1.4
    run_sb = 0.2
    run_cs = -2 * r_per_out + 0.075

    sum_bb_no_ib = 0
    sum_hb = 0
    sum_1b = 0
    sum_2b = 0
    sum_3b = 0
    sum_hr = 0
    sum_sb = 0
    sum_cs = 0

    sum_ab = 0
    sum_hits = 0
    sum_sf = 0

    for player in players:
        if player.stats_batter == None or player.get_fielding_position() != 0:
            sum_bb_no_ib += player.stats_batter.batter_walks - player.stats_batter.batter_intentional_walks
            sum_hb += player.stats_batter.batter_hit_by_pitch
            sum_1b += player.stats_batter.batter_singles
            sum_2b += player.stats_batter.batter_doubles
            sum_3b += player.stats_batter.batter_triples
            sum_hr += player.stats_batter.batter_homeruns
            sum_sb += player.stats_batter.batter_stolen_bases
            sum_cs += player.stats_batter.batter_caught_stealing

            sum_ab += player.stats_batter.batter_ab
            sum_hits += player.stats_batter.batter_hits
            sum_sf += player.stats_batter.batter_sac_flies

    run_minus = (run_bb * sum_bb_no_ib + run_hb * sum_hb + run_1b * sum_1b + run_2b * sum_2b + run_3b * sum_3b + run_hr * sum_hr + run_sb * sum_sb + run_cs * sum_cs) / (sum_ab - sum_hits + sum_sf)
    run_plus = (run_bb * sum_bb_no_ib + run_hb * sum_hb + run_1b * sum_1b + run_2b * sum_2b + run_3b * sum_3b + run_hr * sum_hr + run_sb * sum_sb + run_cs * sum_cs) / (sum_bb_no_ib + sum_hb + sum_hits)

    woba_scale = 1.0 / (run_plus + run_minus)
    woba_bb = (run_bb + run_minus) * woba_scale
    woba_hb = (run_hb + run_minus) * woba_scale
    woba_1b = (run_1b + run_minus) * woba_scale
    woba_2b = (run_2b + run_minus) * woba_scale
    woba_3b = (run_3b + run_minus) * woba_scale
    woba_hr = (run_hr + run_minus) * woba_scale
    woba_sb = run_sb * woba_scale
    woba_cs = run_cs * woba_scale

    tot_pa = sum_ab + sum_bb_no_ib + sum_sf
    avg_woba = woba_bb / tot_pa * sum_bb_no_ib + woba_hb / tot_pa * sum_hb + woba_1b / tot_pa * sum_1b + woba_2b / tot_pa * sum_2b + woba_3b / tot_pa * sum_3b + woba_hr / tot_pa * sum_hr

    lg_wsb = (sum_sb * run_sb + sum_cs * run_cs) / (sum_1b + sum_bb_no_ib + sum_hb)
    
    return WobaWeights(
        woba_scale=woba_scale,
        woba_bb=woba_bb,
        woba_hb=woba_hb,
        woba_1b=woba_1b,
        woba_2b=woba_2b,
        woba_3b=woba_3b,
        woba_hr=woba_hr,
        woba_sb=woba_sb,
        woba_cs=woba_cs,
        woba_avg=avg_woba,
        lg_wsb=lg_wsb
    )