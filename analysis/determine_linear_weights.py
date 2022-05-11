from dataclasses import dataclass
from typing import Callable, List
from analysis.regression_analysis import RegressionAnalysisModel, perform_multi_regression, perform_regression

from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer
from class_model.global_stats.AllLeagueStats import LeagueStats
from util.ip_math import add_ip, ip_to_ip_w_remainder


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
    # give [stolen bases, caught stealing] get wSB
    wsb_from_steal_stats: Callable[[float, float], float]
    # give [baserunning rating] get ubr / (hits - homeruns)
    ubr_per_chance_from_baserunning: Callable[[int], float]
    runs_per_win: float
    run_value_bases_out: float

def get_woba_constants(
    players: List[SingleLineStatsPlayer],
    league_stats: LeagueStats
) -> LinearWeightsFormulas:
    eligible_batters = list(filter(lambda player: player.get_fielding_position() == 0 and player.stats_batter != None and player.stats_batter.batter_pa > 20, players))
    wraa_ram = RegressionAnalysisModel(
        get_x=lambda player: player.stats_batter.batter_woba, 
        get_y_numerator=lambda player: player.stats_batter.batter_wraa, 
        get_y_denominator=lambda player: player.stats_batter.batter_pa,
        min_y_denom=10,
        should_use_cooks_distance=True
    )
    woba_to_wraa_analysis = perform_regression(eligible_batters, wraa_ram)


    X = []
    y = []
    for player in eligible_batters:
        X.append([ 
            player.stats_batter.batter_walks - player.stats_batter.batter_intentional_walks, 
            player.stats_batter.batter_hit_by_pitch, 
            player.stats_batter.batter_singles, 
            player.stats_batter.batter_doubles, 
            player.stats_batter.batter_triples, 
            player.stats_batter.batter_homeruns 
        ])
        y.append(player.stats_batter.batter_woba * (player.stats_batter.batter_ab + player.stats_batter.batter_walks - player.stats_batter.batter_intentional_walks + 
            player.stats_batter.batter_sac_flies + player.stats_batter.batter_hit_by_pitch))
    woba_weights_analysis = perform_multi_regression(X, y)


    X = []
    y = []
    for player in eligible_batters:
        X.append([ player.stats_batter.batter_stolen_bases, player.stats_batter.batter_caught_stealing ])
        y.append(player.stats_batter.batter_weighted_stolen_bases)
    wsb_analysis = perform_multi_regression(X, y)

    
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
        woba_to_wraa_per_pa=lambda woba: woba_to_wraa_analysis.slope * woba + woba_to_wraa_analysis.intercept,
        woba_mult_by_pa_from_hits=lambda walks, hbp, singles, doubles, triples, homeruns: walks * woba_weights_analysis.slope[0] + hbp * woba_weights_analysis.slope[1] + 
            singles * woba_weights_analysis.slope[2] + doubles * woba_weights_analysis.slope[3] + triples * woba_weights_analysis.slope[4] + homeruns * woba_weights_analysis.slope[5] + woba_weights_analysis.intercept,
        wsb_from_steal_stats=lambda stolen_bases, caught_stealing: stolen_bases * wsb_analysis.slope[0] + caught_stealing * wsb_analysis.slope[1] + wsb_analysis.intercept,
        ubr_per_chance_from_baserunning=lambda baserunning: baserunning * ubr_analysis.slope + ubr_analysis.intercept,
        runs_per_win=runs_per_win,
        run_value_bases_out=wsb_analysis.slope[1]
    )