from dataclasses import dataclass
from typing import Callable, List
from analysis.regression_analysis import RegressionAnalysisModel, perform_regression
from analysis.tango_woba import get_tango_woba_factors

from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer
from class_model.global_stats.AllLeagueStats import LeagueStats


batting_positions = [0, 2, 3, 4, 5, 6, 7, 8, 9]

def get_positional_adjustment(pos_num: int) -> float:
    if pos_num == 2:
        return 12.5
    elif pos_num == 3:
        return -12.5
    elif pos_num == 4:
        return 2.5
    elif pos_num == 5:
        return 2.5
    elif pos_num == 6:
        return 7.5
    elif pos_num == 7:
        return -7.5
    elif pos_num == 8:
        return 2.5
    elif pos_num == 9:
        return -7.5
    else:
        return -17.5


@dataclass
class LinearWeightsFormulas:
    # Give woba, get wraa/pa
    woba_to_wraa_per_pa: Callable[[float], float]
    # give [walks, hit by pitch, singles, doubles, triples, homeruns] get woba * pa
    woba_mult_by_pa_from_hits: Callable[[float, float, float, float, float, float], float]
    # give [stolen bases, caught stealing, singles, walks, hit by pitch] get wSB
    wsb_from_steal_stats: Callable[[float, float, float, float, float], float]
    # give [baserunning rating] get ubr / (hits - homeruns)
    ubr_per_chance_from_baserunning: Callable[[int], float]
    runs_per_win: float
    run_value_bases_out: float

def get_woba_constants(
    players: List[SingleLineStatsPlayer],
    league_stats: LeagueStats
) -> LinearWeightsFormulas:
    woba_weights = get_tango_woba_factors(players, league_stats=league_stats)
    
    ubr_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.baserunning, 
        get_y_numerator=lambda player: player.stats_batter.batter_ubr, 
        get_y_denominator=lambda player: player.stats_batter.batter_hits - player.stats_batter.batter_homeruns,
        min_y_denom=10,
        should_use_cooks_distance=True
    )
    ubr_analysis = perform_regression(players, ubr_ram)

    runs_per_win = league_stats.get_runs_per_win()

    return LinearWeightsFormulas(
        woba_to_wraa_per_pa=lambda woba: (woba - woba_weights.woba_avg) / woba_weights.woba_scale,
        woba_mult_by_pa_from_hits=lambda walks, hbp, singles, doubles, triples, homeruns: walks * woba_weights.woba_bb + hbp * woba_weights.woba_hb + singles * woba_weights.woba_1b + 
            doubles * woba_weights.woba_1b + triples * woba_weights.woba_3b + homeruns * woba_weights.woba_hr,
        wsb_from_steal_stats=lambda stolen_bases, caught_stealing, singles, bb_no_ib, hb: stolen_bases * woba_weights.woba_sb + caught_stealing * woba_weights.woba_cs - (woba_weights.lg_wsb * (singles + bb_no_ib + hb)),
        ubr_per_chance_from_baserunning=lambda baserunning: baserunning * ubr_analysis.slope + ubr_analysis.intercept,
        runs_per_win=runs_per_win,
        run_value_bases_out=woba_weights.woba_cs
    )