from dataclasses import dataclass
from typing import Callable, List, Dict
from analysis.regression_analysis import RegressionAnalysisModel, RegressionAnalysis, perform_multi_regression, perform_regression, perform_throws_handedness_no_hl_regression

from class_model.BaseStatsPlayer import SingleLineStatsPlayer
from class_model.global_stats.PitcherStats import PitcherStats

min_pa_denom = 30
low_min_denom = 15

def __generate_stat_formula__(analysis: Dict[str, Dict[str, RegressionAnalysis]]) -> Callable[[str, int], float]:
    def formula(throws: str, stat: int) -> float:
        handed_analysis: RegressionAnalysis = analysis["R"]
        if throws == "L":
            handed_analysis = analysis["L"]
        
        if stat <= 25:
            if handed_analysis.slope < 0:
                return handed_analysis.slope * stat / 2 + handed_analysis.intercept
            return handed_analysis.slope * stat * 2 + handed_analysis.intercept

        if stat > 90:
            return ((handed_analysis.slope * stat + handed_analysis.intercept) + (handed_analysis.slope * 90 + handed_analysis.intercept)) / 2
        return handed_analysis.slope * stat + handed_analysis.intercept

    return formula


@dataclass
class PitchingPlayerFormulas:
    # (throws, stuff) => strikeouts / (bf - hbp)
    get_strikeouts_per_pa: Callable[[str, int], float]
    # (throws, movement) => homeruns / (bf - hbp - so)
    get_homeruns_per_mod_pa: Callable[[str, int], float]
    # (throws, control) => walks / (bf - hbp - so)
    get_walks_per_mod_pa: Callable[[str, int], float]
    # (gb_type, stuff, mov, ctrl) => hits / (bip)
    get_babip_rate: Callable[[int, int, int, int], float]
    # (hold) => (steal attempts) / (hits)
    get_stolen_bases_attempted_per_hit: Callable[[int], float]
    # (hold) => (steal successes) / (steal attempt)
    get_caught_stealing_per_steal: Callable[[int], float]
    # (gb_type) => gidp / bip
    get_gidp_per_bip: Callable[[int], float]
    # (stamina) => bf / game
    get_bf_per_game: Callable[[int], float]


def get_pitching_player_formulas(players: List[SingleLineStatsPlayer], pitcher_stats: PitcherStats, plat_only: bool = False) -> PitchingPlayerFormulas:
    pitchers_only = list(filter(lambda player: player.stats_pitcher.pitcher_bf > 0, players))
    k_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.stu_ovr, 
        get_y_numerator=lambda player: player.stats_pitcher.pitcher_strikeouts, 
        get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns,
        min_y_denom=min_pa_denom,
        should_use_cooks_distance=True
    )
    k_analysis = perform_throws_handedness_no_hl_regression(pitchers_only, k_ram)
    

    hr_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.mov_ovr, 
        get_y_numerator=lambda player: player.stats_pitcher.pitcher_homeruns, 
        get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch,
        min_y_denom=min_pa_denom,
        should_use_cooks_distance=True
    )
    hr_analysis = perform_throws_handedness_no_hl_regression(pitchers_only, hr_ram)
    

    walks_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.ctl_ovr,
        get_y_numerator=lambda player: player.stats_pitcher.pitcher_walks - player.stats_pitcher.pitcher_intentional_walks, 
        get_y_denominator=lambda player: player.stats_pitcher.pitcher_bf - player.stats_pitcher.pitcher_hit_by_pitch - player.stats_pitcher.pitcher_homeruns - player.stats_pitcher.pitcher_strikeouts,
        min_y_denom=min_pa_denom,
        should_use_cooks_distance=True
    )
    walks_analysis = perform_throws_handedness_no_hl_regression(pitchers_only, walks_ram)

    X_data = {}
    X_control_var = {}
    for player in players:
        k = str(player.card_player.gb_type) + "_" + str(player.card_player.stu_ovr) + "_" + str(player.card_player.mov_ovr) + "_" + str(player.card_player.ctl_ovr)
        X_control_var[k] = [player.card_player.gb_type, player.card_player.stu_ovr, player.card_player.mov_ovr, player.card_player.ctl_ovr]
        if k not in X_data:
            X_data[k] = [0, 0]
        X_data[k][0] += player.stats_pitcher.pitcher_singles + player.stats_pitcher.pitcher_doubles + player.stats_pitcher.pitcher_triples
        X_data[k][1] += player.stats_pitcher.pitcher_ab - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_homeruns

    X = []
    y = []
    for k in X_data.keys():
        if X_data[k][1] > 500:
            X.append(X_control_var[k])
            y.append(X_data[k][0] / X_data[k][1])

    if len(X) <= 2:
        for k in X_data.keys():
            if X_data[k][1] > 30:
                X.append(X_control_var[k])
                y.append(X_data[k][0] / X_data[k][1])
    babip_analysis = perform_multi_regression(X, y)

    sba_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.hold,
        get_y_numerator=lambda player: player.stats_pitcher.pitcher_stolen_bases + player.stats_pitcher.pitcher_caught_stealing, 
        get_y_denominator=lambda player: player.stats_pitcher.pitcher_singles + player.stats_pitcher.pitcher_walks + player.stats_pitcher.pitcher_hit_by_pitch,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    sba_analysis = perform_regression(pitchers_only, sba_ram) if not plat_only else RegressionAnalysis(slope=0, intercept=0, r_squared=0, len_x=0)
    

    steal_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.hold,
        get_y_numerator=lambda player: player.stats_pitcher.pitcher_caught_stealing, 
        get_y_denominator=lambda player: player.stats_pitcher.pitcher_stolen_bases + player.stats_pitcher.pitcher_caught_stealing,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    steal_analysis = perform_regression(pitchers_only, steal_ram) if not plat_only else RegressionAnalysis(slope=0, intercept=0, r_squared=0, len_x=0)
    

    gidp_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.gb_type,
        get_y_numerator=lambda player: player.stats_pitcher.pitcher_double_plays, 
        get_y_denominator=lambda player: player.stats_pitcher.pitcher_ab - player.stats_pitcher.pitcher_strikeouts - player.stats_pitcher.pitcher_homeruns,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    gidp_analysis = perform_regression(pitchers_only, gidp_ram) if not plat_only else RegressionAnalysis(slope=0, intercept=0, r_squared=0, len_x=0)


    stam_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.stamina,
        get_y_numerator=lambda player: player.stats_pitcher.pitcher_bf, 
        get_y_denominator=lambda player: player.stats_pitcher.pitcher_games,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    stam_analysis = perform_regression(pitchers_only, stam_ram) if not plat_only else RegressionAnalysis(slope=0, intercept=0, r_squared=0, len_x=0)

    return PitchingPlayerFormulas(
        get_strikeouts_per_pa=__generate_stat_formula__(k_analysis),
        get_homeruns_per_mod_pa=__generate_stat_formula__(hr_analysis),
        get_walks_per_mod_pa=__generate_stat_formula__(walks_analysis),
        get_babip_rate=lambda gb_type, stu, mov, ctl: gb_type * babip_analysis.slope[0] + stu * babip_analysis.slope[1] + mov * babip_analysis.slope[2] + ctl * babip_analysis.slope[3] + babip_analysis.intercept,
        get_stolen_bases_attempted_per_hit=lambda stat: sba_analysis.slope * stat + sba_analysis.intercept,
        get_caught_stealing_per_steal=lambda stat: steal_analysis.slope * stat + steal_analysis.slope,
        get_gidp_per_bip=lambda gb_type: gb_type * gidp_analysis.slope + gidp_analysis.intercept,
        get_bf_per_game=lambda stamina: stamina * stam_analysis.slope + stam_analysis.intercept
    )