from dataclasses import dataclass
from typing import Callable, List, Dict
from analysis.regression_analysis import RegressionAnalysisModel, RegressionAnalysis, perform_bats_handedness_reg_regression, perform_bats_handedness_regression, perform_reg_regression, perform_regression

from class_model.BaseStatsPlayer import SingleLineStatsPlayer
from util.ip_math import ip_to_ip_w_remainder

min_pa_denom = 50
low_min_denom = 10
defensive_position_nums = [2, 3, 4, 5, 6, 7, 8, 9]

def __generate_stat_formula__(analysis: Dict[str, RegressionAnalysis]) -> Callable[[str, int], float]:
    def formula(bats: str, stat: int) -> float:
        high_low = "high" if stat >= 50 else "low"
        handed_analysis: RegressionAnalysis = analysis["R"][high_low]
        if bats == "L":
            handed_analysis = analysis["L"][high_low]
        elif bats == "S":
            handed_analysis = analysis["S"]
        
        if stat <= 25:
            if handed_analysis.slope < 0:
                return handed_analysis.slope * stat / 2 + handed_analysis.intercept
            return handed_analysis.slope * stat * 2 + handed_analysis.intercept

        if stat > 100:
            return ((handed_analysis.slope * stat + handed_analysis.intercept) + (handed_analysis.slope * 100 + handed_analysis.intercept)) / 2
        
        return handed_analysis.slope * stat + handed_analysis.intercept

    return formula

@dataclass
class DefenseFormulas:
    # (ifarm|ofarm|carm) => arm_runs per fielding_ip
    get_arm_runs: Callable[[int], float]
    # (defense) => zr per fielding_ip
    get_zr: Callable[[int], float]
    # (cabi) => frame_runs per fielding_ip
    get_frame_runs: Callable[[int], float]
    # (carm) => steals attempted per fielding_ip
    get_steal_attempt_rate: Callable[[int], float]
    # (carm) => caught steals per steal attempts
    get_caught_stealing_rate: Callable[[int], float]

@dataclass
class BattingPlayerFormulas:
    # (bats, avoid k) => strikeouts / (pa - hbp)
    get_strikeouts_per_pa: Callable[[str, int], float]
    # (bats, power) => homeruns / (pa - hbp - so)
    get_homeruns_per_mod_pa: Callable[[str, int], float]
    # (bats, eye) => walks / (pa - hbp - so)
    get_walks_per_mod_pa: Callable[[str, int], float]
    # (bats, babip) => (hits - homeruns) / (pa - hbp - so - walks - hr)
    get_non_hr_hits_per_mod_pa: Callable[[str, int], float]
    # (bats, gap) => xbh / (hits - homeruns)
    get_xbh_per_hit: Callable[[str, int], float]
    # (speed) => triples / (doubles + triples)
    get_triple_rate_per_xbh: Callable[[int], float]
    # (speed) => sba / (walks + hbp + singles)
    get_stolen_base_attempt_per_1b: Callable[[int], float]
    # (stealing) => steal / sba
    get_successful_steal_rate: Callable[[int], float]
    
    defense_formulas: Dict[int, DefenseFormulas]


def __get_defensive_formulas__(players: List[SingleLineStatsPlayer], pos_num: int):
    def get_arm(pos_num: int) -> Callable[[SingleLineStatsPlayer], int]:
        if pos_num >= 7:
            return lambda player: player.card_player.ofarm
        elif pos_num >= 3:
            return lambda player: player.card_player.ifarm
        return lambda player: player.card_player.carm

    def get_defense(pos_num: int) -> Callable[[SingleLineStatsPlayer], int]:
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

        raise Exception("Bad position number")
    eligible_players = list(filter(lambda player: player.get_fielding_position() == pos_num and get_defense(pos_num)(player) > 20, players))

    arm_runs_ram = RegressionAnalysisModel(
        get_x=get_arm(pos_num),
        get_y_numerator=lambda player: player.stats_fielder.fielding_arm_runs,
        get_y_denominator=lambda player: ip_to_ip_w_remainder(player.stats_fielder.fielding_ip),
        min_y_denom=10,
        should_use_cooks_distance=True
    )
    arm_runs_analysis = perform_reg_regression(
        eligible_players,
        arm_runs_ram
    )

    zr_ram = RegressionAnalysisModel(
        get_x=get_defense(pos_num),
        get_y_numerator=lambda player: player.stats_fielder.fielding_zr,
        get_y_denominator=lambda player: ip_to_ip_w_remainder(player.stats_fielder.fielding_ip),
        min_y_denom=10,
        should_use_cooks_distance=True
    )
    zr_analysis = perform_reg_regression(
        eligible_players,
        zr_ram
    )

    frame_runs_analysis = None
    steal_attempt_analysis = None
    caught_steal_analysis = None
    if pos_num == 2:
        frame_runs_ram = RegressionAnalysisModel(
            get_x=lambda player: player.card_player.cabi,
            get_y_numerator=lambda player: player.stats_fielder.fielding_framing_runs,
            get_y_denominator=lambda player: ip_to_ip_w_remainder(player.stats_fielder.fielding_ip),
            min_y_denom=10,
            should_use_cooks_distance=True
        )
        frame_runs_analysis = perform_reg_regression(
            eligible_players,
            frame_runs_ram
        )

        steal_attempt_ram = RegressionAnalysisModel(
            get_x=lambda player: player.card_player.carm,
            get_y_numerator=lambda player: player.stats_fielder.fielding_stolen_bases_against + player.stats_fielder.fielding_runners_thrown_out,
            get_y_denominator=lambda player: ip_to_ip_w_remainder(player.stats_fielder.fielding_ip),
            min_y_denom=10,
            should_use_cooks_distance=True
        )
        steal_attempt_analysis = perform_reg_regression(
            eligible_players,
            steal_attempt_ram
        )

        caught_steal_ram = RegressionAnalysisModel(
            get_x=lambda player: player.card_player.carm,
            get_y_numerator=lambda player: player.stats_fielder.fielding_runners_thrown_out,
            get_y_denominator=lambda player: player.stats_fielder.fielding_stolen_bases_against + player.stats_fielder.fielding_runners_thrown_out,
            min_y_denom=10,
            should_use_cooks_distance=True
        )
        caught_steal_analysis = perform_reg_regression(
            eligible_players,
            caught_steal_ram
        )

    return DefenseFormulas(
        get_arm_runs=lambda arm: arm * arm_runs_analysis.slope + arm_runs_analysis.intercept,
        get_zr=lambda defense: zr_analysis.slope * defense + zr_analysis.intercept,
        get_frame_runs=lambda cabi: 0.0 if frame_runs_analysis == None else frame_runs_analysis.slope * cabi + frame_runs_analysis.intercept,
        get_steal_attempt_rate=lambda carm: 0.0 if steal_attempt_analysis == None else steal_attempt_analysis.slope * carm + steal_attempt_analysis.intercept,
        get_caught_stealing_rate=lambda carm: 0.0 if caught_steal_analysis == None else caught_steal_analysis.slope * carm + caught_steal_analysis.intercept
    )


def get_batting_player_formulas(players: List[SingleLineStatsPlayer], plat_only: bool = False) -> BattingPlayerFormulas:
    batting_only = list(filter(lambda player: player.get_fielding_position() == 0, players))
    k_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.avk_ovr, 
        get_y_numerator=lambda player: player.stats_batter.batter_strikeouts, 
        get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_intentional_walks - player.stats_batter.batter_walks,
        min_y_denom=min_pa_denom,
        should_use_cooks_distance=True
    )
    k_analysis = perform_bats_handedness_reg_regression(batting_only, k_ram)
    

    hr_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.pow_ovr, 
        get_y_numerator=lambda player: player.stats_batter.batter_homeruns, 
        get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_intentional_walks - player.stats_batter.batter_strikeouts - player.stats_batter.batter_walks,
        min_y_denom=min_pa_denom,
        should_use_cooks_distance=True
    )
    hr_analysis = perform_bats_handedness_reg_regression(batting_only, hr_ram)
    

    walks_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.eye_ovr,
        get_y_numerator=lambda player: player.stats_batter.batter_walks - player.stats_batter.batter_intentional_walks, 
        get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_intentional_walks,
        min_y_denom=min_pa_denom,
        should_use_cooks_distance=True
    )
    walks_analysis = perform_bats_handedness_reg_regression(batting_only, walks_ram)
    

    hits_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.babip_ovr,
        get_y_numerator=lambda player: player.stats_batter.batter_hits - player.stats_batter.batter_homeruns, 
        get_y_denominator=lambda player: player.stats_batter.batter_pa - player.stats_batter.batter_hit_by_pitch - player.stats_batter.batter_intentional_walks - player.stats_batter.batter_strikeouts - player.stats_batter.batter_homeruns - player.stats_batter.batter_walks,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    hits_analysis = perform_bats_handedness_reg_regression(batting_only, hits_ram)
    

    xbh_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.gap_ovr,
        get_y_numerator=lambda player: player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
        get_y_denominator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    xbh_analysis = perform_bats_handedness_reg_regression(batting_only, xbh_ram)
    

    triple_rate_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.speed,
        get_y_numerator=lambda player: player.stats_batter.batter_doubles + player.stats_batter.batter_triples, 
        get_y_denominator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_doubles + player.stats_batter.batter_triples,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    triple_rate_analysis = perform_reg_regression(batting_only, triple_rate_ram) if not plat_only else RegressionAnalysis(slope=0, intercept=0, r_squared=0, len_x=0)
    

    sba_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.speed,
        get_y_numerator=lambda player: player.stats_batter.batter_stolen_bases + player.stats_batter.batter_caught_stealing, 
        get_y_denominator=lambda player: player.stats_batter.batter_singles + player.stats_batter.batter_walks + player.stats_batter.batter_hit_by_pitch,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    sba_analysis = perform_reg_regression(batting_only, sba_ram) if not plat_only else RegressionAnalysis(slope=0, intercept=0, r_squared=0, len_x=0)
    

    steal_ram = RegressionAnalysisModel(
        get_x=lambda player: player.card_player.steal,
        get_y_numerator=lambda player: player.stats_batter.batter_stolen_bases, 
        get_y_denominator=lambda player: player.stats_batter.batter_stolen_bases + player.stats_batter.batter_caught_stealing,
        min_y_denom=low_min_denom,
        should_use_cooks_distance=True
    )
    steal_analysis = perform_reg_regression(batting_only, steal_ram) if not plat_only else RegressionAnalysis(slope=0, intercept=0, r_squared=0, len_x=0)

    defense_formulas = {}
    for position_number in defensive_position_nums:
        defense_formulas[position_number] = __get_defensive_formulas__(players, position_number)

    return BattingPlayerFormulas(
        get_strikeouts_per_pa=__generate_stat_formula__(k_analysis),
        get_homeruns_per_mod_pa=__generate_stat_formula__(hr_analysis),
        get_walks_per_mod_pa=__generate_stat_formula__(walks_analysis),
        get_non_hr_hits_per_mod_pa=__generate_stat_formula__(hits_analysis),
        get_xbh_per_hit=__generate_stat_formula__(xbh_analysis),
        get_triple_rate_per_xbh=lambda stat: triple_rate_analysis.slope * stat + triple_rate_analysis.intercept,
        get_stolen_base_attempt_per_1b=lambda stat: sba_analysis.slope * stat + sba_analysis.intercept,
        get_successful_steal_rate=lambda stat: steal_analysis.slope * stat + steal_analysis.slope,
        defense_formulas=defense_formulas
    )