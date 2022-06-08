from dataclasses import dataclass
from typing import Callable, Dict, List
from analysis.regression_analysis import RegressionAnalysis, perform_multi_regression
from class_model.BaseCardPlayer import BaseCardPlayer
from util.ip_math import ip_to_ip_w_remainder

from class_model.zips.MatchedZipsPlayer import MatchedZipsPlayer


@dataclass
class ZipsBatterProjections:
    # babip / bip -> babip rating
    get_babip: Callable[[float], float]
    # hr / pa - hbp -> pow rating
    get_pow: Callable[[float], float]
    # bb / pa - hbp -> eye rating
    get_eye: Callable[[float], float]
    # k / pa - hbp - walks -> avk rating
    get_avk: Callable[[float], float]
    # xbh / non_hr_hits -> gap rating
    get_gap: Callable[[float], float]
    # avk, babip, pow, eye, gap, card_player -> ovr rating
    get_ovr: Callable[[float, float, float, float, float, BaseCardPlayer], float]

@dataclass
class ZipsPitcherProjections:
    # k_per_9 -> stu rating
    get_stu: Callable[[float], float]
    # hr_per_9, gb_type -> mov rating
    get_mov: Callable[[float, BaseCardPlayer], float]
    # bb_per_9 -> ctl rating
    get_ctl: Callable[[float], float]
    # stu, mov, ctl, card_player -> ovr rating
    get_ovr: Callable[[float, float, float, BaseCardPlayer], float]

def __get_relevant_positional_defense__(player: BaseCardPlayer) -> int:
    if player.position == 0:
        return 0
    elif player.position == 2:
        return player.defensec
    elif player.position == 3:
        return player.defense1b
    elif player.position == 4:
        return player.defense2b
    elif player.position == 5:
        return player.defense3b
    elif player.position == 6:
        return player.defensess
    elif player.position == 7:
        return player.defenself
    elif player.position == 8:
        return player.defensecf
    elif player.position == 9:
        return player.defenserf

def __get_num_positions__(player: BaseCardPlayer) -> int:
    positions_played = 0
    if player.defensec > 20:
        positions_played += 1
    if player.defense1b > 20:
        positions_played += 1
    if player.defense2b > 20:
        positions_played += 1
    if player.defense3b > 20:
        positions_played += 1
    if player.defensess > 20:
        positions_played += 1
    if player.defenself > 20:
        positions_played += 1
    if player.defensecf > 20:
        positions_played += 1
    if player.defenserf > 20:
        positions_played += 1

    return positions_played

def get_batter_projections(batters: List[MatchedZipsPlayer]) -> ZipsBatterProjections:
    batter_k_X = []
    batter_bb_X = []
    batter_hr_X = []
    batter_babip_X = []
    batter_xbh_X = []
    batter_k_y = []
    batter_bb_y = []
    batter_hr_y = []
    batter_babip_y = []
    batter_xbh_y = []

    batter_ovr_X: Dict[int, List[float]] = {}
    batter_ovr_y: Dict[int, List[float]] = {}

    for batter in batters:
        if batter.zips_batter.pa > 50 and batter.card_player.ovr < 100:
            batter_k_X.append([ batter.zips_batter.strikeouts / (batter.zips_batter.pa - batter.zips_batter.hbp - batter.zips_batter.walks) ])
            batter_k_y.append(batter.card_player.avk_ovr)
            
            batter_bb_X.append([ batter.zips_batter.walks / (batter.zips_batter.pa - batter.zips_batter.hbp) ])
            batter_bb_y.append(batter.card_player.eye_ovr)
            
            batter_hr_X.append([ batter.zips_batter.homeruns / (batter.zips_batter.pa - batter.zips_batter.hbp) ])
            batter_hr_y.append(batter.card_player.pow_ovr)
            
            batter_babip_X.append([ (batter.zips_batter.singles + batter.zips_batter.doubles + batter.zips_batter.triples) / (batter.zips_batter.ab - batter.zips_batter.strikeouts - batter.zips_batter.homeruns) ])
            batter_babip_y.append(batter.card_player.babip_ovr)
            
            batter_xbh_X.append([ (batter.zips_batter.doubles + batter.zips_batter.triples) / (batter.zips_batter.singles + batter.zips_batter.doubles + batter.zips_batter.triples) ])
            batter_xbh_y.append(batter.card_player.gap_ovr)


            if batter.card_player.position not in batter_ovr_X:
                batter_ovr_X[batter.card_player.position] = []
                batter_ovr_y[batter.card_player.position] = []

            batter_ovr_X[batter.card_player.position].append([
                batter.card_player.avk_ovr,
                batter.card_player.babip_ovr,
                batter.card_player.pow_ovr,
                batter.card_player.eye_ovr,
                batter.card_player.gap_ovr,
                __get_relevant_positional_defense__(batter.card_player),
                __get_num_positions__(batter.card_player),
                batter.card_player.speed,
                batter.card_player.steal,
                batter.card_player.baserunning
            ])
            batter_ovr_y[batter.card_player.position].append(batter.card_player.ovr)

    k_analysis = perform_multi_regression(batter_k_X, batter_k_y)
    bb_analysis = perform_multi_regression(batter_bb_X, batter_bb_y)
    hr_analysis = perform_multi_regression(batter_hr_X, batter_hr_y)
    babip_analysis = perform_multi_regression(batter_babip_X, batter_babip_y)
    xbh_analysis = perform_multi_regression(batter_xbh_X, batter_xbh_y)

    ovr_analysis: Dict[int, RegressionAnalysis] = {}
    for pos in batter_ovr_X.keys():
        ovr_analysis[pos] = perform_multi_regression(batter_ovr_X[pos], batter_ovr_y[pos])

    def __get_ovr__(avk: float, babip: float, pow_st: float, eye: float, gap: float, card_player: BaseCardPlayer) -> float:
        oa = ovr_analysis[card_player.position]
        return (avk * oa.slope[0] + babip * oa.slope[1] + pow_st * oa.slope[2] + eye * oa.slope[3] + gap * oa.slope[4] + __get_relevant_positional_defense__(card_player) * oa.slope[5] + 
            __get_num_positions__(card_player) * oa.slope[6] + card_player.speed * oa.slope[7] +
            card_player.steal * oa.slope[8] + card_player.baserunning * oa.slope[9] + oa.intercept)

    return ZipsBatterProjections(
        get_avk=lambda st_rate: st_rate * k_analysis.slope[0] + k_analysis.intercept,
        get_babip=lambda st_rate: st_rate * babip_analysis.slope[0] + babip_analysis.intercept,
        get_eye=lambda st_rate: st_rate * bb_analysis.slope[0] + bb_analysis.intercept,
        get_pow=lambda st_rate: st_rate * hr_analysis.slope[0] + hr_analysis.intercept,
        get_gap=lambda st_rate: st_rate * xbh_analysis.slope[0] + xbh_analysis.intercept,
        get_ovr=__get_ovr__
    )

def get_pitcher_projections(pitchers: List[MatchedZipsPlayer]) -> ZipsPitcherProjections:
    pitcher_k_X = []
    pitcher_bb_X = []
    pitcher_hr_X = []
    pitcher_k_y = []
    pitcher_bb_y = []
    pitcher_hr_y = []

    pitcher_ovr_X = []
    pitcher_ovr_y = []

    for pitcher in pitchers:
        if pitcher.zips_pitcher.ip > 30 and pitcher.card_player.ovr < 100:
            pitcher_k_X.append([ pitcher.zips_pitcher.k_per_9 ])
            pitcher_k_y.append(pitcher.card_player.stu_ovr)
            
            pitcher_bb_X.append([ pitcher.zips_pitcher.bb_per_9 ])
            pitcher_bb_y.append(pitcher.card_player.ctl_ovr)
            
            pitcher_hr_X.append([ pitcher.zips_pitcher.hr_per_9, pitcher.card_player.gb_type ])
            pitcher_hr_y.append(pitcher.card_player.mov_ovr)

            pitcher_ovr_X.append([ pitcher.card_player.stu_ovr, pitcher.card_player.mov_ovr, pitcher.card_player.ctl_ovr, pitcher.card_player.stamina ])
            pitcher_ovr_y.append(pitcher.card_player.ovr)

    k_analysis = perform_multi_regression(pitcher_k_X, pitcher_k_y)
    bb_analysis = perform_multi_regression(pitcher_bb_X, pitcher_bb_y)
    hr_analysis = perform_multi_regression(pitcher_hr_X, pitcher_hr_y)

    ovr_analysis = perform_multi_regression(pitcher_ovr_X, pitcher_ovr_y)

    return ZipsPitcherProjections(
        get_stu=lambda st: st * k_analysis.slope[0] + k_analysis.intercept,
        get_mov=lambda st, card_player: st * hr_analysis.slope[0] + card_player.gb_type * hr_analysis.slope[1] + hr_analysis.intercept,
        get_ctl=lambda st: st * bb_analysis.slope[0] + bb_analysis.intercept,
        get_ovr=lambda stu, mov, ctl, card_player: stu * ovr_analysis.slope[0] + mov * ovr_analysis.slope[1] + ctl * ovr_analysis.slope[2] + card_player.stamina * ovr_analysis.slope[3] + ovr_analysis.intercept
    )