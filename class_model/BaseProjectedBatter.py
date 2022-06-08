from dataclasses import dataclass
from typing import Dict, List, Tuple
from analysis.determine_batting_player import BattingPlayerFormulas
from analysis.determine_linear_weights import LinearWeightsFormulas
from analysis.lin_weights_modifiers import LinearWeightsModifiers

from class_model.BaseCardPlayer import BaseCardPlayer
from class_model.global_stats.AllLeagueStats import LeagueStats
from class_model.league_stats.platoon_splits import PlatoonSplits

base_fill_pct = 0.65
base_pa_fill = 5000

@dataclass
class ProjBatterStats:
    pa: float = 0.0
    singles: float = 0.0
    doubles: float = 0.0
    triples: float = 0.0
    homeruns: float = 0.0
    walks: float = 0.0
    strikeouts: float = 0.0
    woba: float = 0.0
    batr: float = 0.0
    wsb: float = 0.0
    ubr: float = 0.0
    bsr: float = 0.0
    zr: float = 0.0
    frame_runs: float = 0.0
    arm_runs: float = 0.0
    wsb_against: float = 0.0
    fielding_runs: float = 0.0
    war: float = 0.0

@dataclass
class TotalProjBatterStats:
    ovr: ProjBatterStats
    vl: ProjBatterStats
    vr: ProjBatterStats

@dataclass
class BaseProjectedBatter:
    tpbs: TotalProjBatterStats
    cid: str = ""
    card_player: BaseCardPlayer = None
    position: int = 0

def __get_weighted_stat__(stat_pred: Tuple[float, int], formula_pred: float):
    if stat_pred[1] == 0:
        return formula_pred
    
    fill_pct = None
    if stat_pred[1] > base_pa_fill:
        fill_pct = base_fill_pct
    else:
        fill_pct = float(stat_pred[1]) / base_pa_fill * base_fill_pct

    if fill_pct > 0.0:
        return stat_pred[0] * fill_pct + (1.0 - fill_pct) * formula_pred

    return formula_pred


def __get_closest_stats__(stats_for_ratings: Dict[int, Tuple[int, int]], player_rating: int) -> Tuple[float, int]:
    if player_rating in stats_for_ratings and stats_for_ratings[player_rating][1] > 0:
        return (stats_for_ratings[player_rating][0] / stats_for_ratings[player_rating][1], stats_for_ratings[player_rating][1])

    if player_rating - 1 in stats_for_ratings and stats_for_ratings[player_rating - 1][1] > 0 and player_rating + 1 in stats_for_ratings and stats_for_ratings[player_rating + 1][1] > 0:
        low_tup = stats_for_ratings[player_rating - 1]
        low_pred = low_tup[0] / low_tup[1]

        high_tup = stats_for_ratings[player_rating + 1]
        high_pred = high_tup[0] / high_tup[1]

        return ((low_pred + high_pred) / 2.0, round((low_tup[1] + high_tup[1]) / 2))

    if player_rating - 1 in stats_for_ratings and stats_for_ratings[player_rating - 1][1] > 0:
        return (stats_for_ratings[player_rating - 1][0] / stats_for_ratings[player_rating - 1][1], stats_for_ratings[player_rating - 1][1])

    if player_rating + 1 in stats_for_ratings and stats_for_ratings[player_rating + 1][1] > 0:
        return (stats_for_ratings[player_rating + 1][0] / stats_for_ratings[player_rating + 1][1], stats_for_ratings[player_rating + 1][1])

    return (0, 0)

def __get_weighted_formula__(vl: float, vr: float, vlhp_pct: float) -> float:
    return vl * vlhp_pct + vr * (1.0 - vlhp_pct)

def __get_proj_batter__(
    player: BaseCardPlayer,
    linear_weights_formulas: LinearWeightsFormulas,
    batting_player_formulas: BattingPlayerFormulas,
    batter_stats_for_players: Dict[str, any],
    pa: float,
    games_started: float,
    pos_num: int,
    def_rating: int,
    vlhp_pct: float,
    lwm: LinearWeightsModifiers
) -> ProjBatterStats:
    walks = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["eye"][player.bats], player.eye_ovr), 
        __get_weighted_formula__(batting_player_formulas.get_walks_per_mod_pa(player.bats, player.eye_vl), batting_player_formulas.get_walks_per_mod_pa(player.bats, player.eye_vr), vlhp_pct=vlhp_pct)) * pa * lwm.bb_mod
    strikeouts = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["avk"][player.bats], player.avk_ovr), 
        __get_weighted_formula__(batting_player_formulas.get_strikeouts_per_pa(player.bats, player.avk_vl), batting_player_formulas.get_strikeouts_per_pa(player.bats, player.avk_vr), vlhp_pct=vlhp_pct)) * (pa - walks) * lwm.k_mod
    homeruns = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["pow"][player.bats], player.pow_ovr), 
        __get_weighted_formula__(batting_player_formulas.get_homeruns_per_mod_pa(player.bats, player.pow_vl), batting_player_formulas.get_homeruns_per_mod_pa(player.bats, player.pow_vr), 
        vlhp_pct)) * (pa - strikeouts - walks) * lwm.homeruns_mod
    non_hr_hits = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["bab"][player.bats], player.babip_ovr), 
        __get_weighted_formula__(batting_player_formulas.get_non_hr_hits_per_mod_pa(player.bats, player.babip_vl), batting_player_formulas.get_non_hr_hits_per_mod_pa(player.bats, player.babip_vr), 
        vlhp_pct=vlhp_pct)) * (pa - strikeouts - homeruns - walks) * lwm.babip_mod
    xbh = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["gap"][player.bats], player.gap_ovr), 
        __get_weighted_formula__(batting_player_formulas.get_xbh_per_hit(player.bats, player.gap_vl), batting_player_formulas.get_xbh_per_hit(player.bats, player.gap_vr), vlhp_pct=vlhp_pct)) * non_hr_hits * lwm.xbh_mod
    singles = (non_hr_hits - xbh)
    triples = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["triple"], player.speed), batting_player_formulas.get_triple_rate_per_xbh(player.speed)) * xbh
    doubles = xbh - triples

    stolen_base_attempts = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["sba"], player.speed), batting_player_formulas.get_stolen_base_attempt_per_1b(player.speed)) * (singles + walks)
    successful_steals = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["steal_rate"], player.steal), batting_player_formulas.get_successful_steal_rate(player.steal)) * stolen_base_attempts * lwm.sb_mod
    caught_stealing = (stolen_base_attempts - successful_steals) * lwm.cs_mod

    def_formulas = batting_player_formulas.defense_formulas[pos_num] if pos_num > 0 else None
    correct_arm_stat = player.ofarm if pos_num >= 7 else player.ifarm if pos_num >= 3 else player.carm
    arm_runs = (__get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["arm_runs"], correct_arm_stat), def_formulas.get_arm_runs(correct_arm_stat)) * games_started * 9.0 if def_formulas != None else 0.0) * lwm.arm_runs_mod
    zr = (__get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["zr"], def_rating), def_formulas.get_zr(def_rating)) * games_started * 9.0 if def_formulas != None else 0.0) * lwm.zr_mod
    frame_runs = (0.0 if pos_num != 2 else __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["frame_runs"], player.cabi), def_formulas.get_frame_runs(player.cabi)) * games_started * 9.0) * lwm.frame_runs_mod
    sba_against = (0.0 if pos_num != 2 else __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["sba_against"], player.carm), def_formulas.get_frame_runs(player.carm)) * games_started * 9.0) * lwm.sba_against_c_mod
    cs_against = (0.0 if pos_num != 2 else __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["cs_against"], player.carm), def_formulas.get_frame_runs(player.carm)) * sba_against) * lwm.cs_against_c_mod
    wsb_against = -1.0 * linear_weights_formulas.wsb_from_steal_stats(sba_against - cs_against, cs_against, games_started * 4.5, games_started * 4.5, 0)


    woba = linear_weights_formulas.woba_mult_by_pa_from_hits(walks, 2, singles, doubles, triples, homeruns) / pa
    wraa = linear_weights_formulas.woba_to_wraa_per_pa(woba) * pa

    wsb = linear_weights_formulas.wsb_from_steal_stats(successful_steals, caught_stealing, singles, walks, 2)
    ubr = __get_weighted_stat__(__get_closest_stats__(batter_stats_for_players["ubr"], player.baserunning), linear_weights_formulas.ubr_per_chance_from_baserunning(player.baserunning)) * non_hr_hits

    return ProjBatterStats(
        pa=pa,
        singles=singles,
        doubles=doubles,
        triples=triples,
        homeruns=homeruns,
        walks=walks,
        strikeouts=strikeouts,
        woba=woba,
        batr=wraa,
        wsb=wsb,
        ubr=ubr,
        bsr=wsb + ubr,
        zr=zr,
        frame_runs=frame_runs,
        arm_runs=arm_runs,
        wsb_against=wsb_against,
        fielding_runs=arm_runs + zr + frame_runs + wsb_against,
        war=(wraa + wsb + ubr + arm_runs + zr + frame_runs + wsb_against) / linear_weights_formulas.runs_per_win
    )

def __convert_stat_player__(
    player: BaseCardPlayer,
    linear_weights_formulas: LinearWeightsFormulas,
    batting_player_formulas: BattingPlayerFormulas,
    batter_stats_for_players: Dict[str, any],
    platoon_splits: PlatoonSplits,
    league_stats: LeagueStats,
    lwm: LinearWeightsModifiers
) -> List[BattingPlayerFormulas]:
    positions_to_run = [[0, 0]]
    if player.defensec > 20:
        positions_to_run.append([2, player.defensec])
    if player.defense1b > 20:
        positions_to_run.append([3, player.defense1b])
    if player.defense2b > 20:
        positions_to_run.append([4, player.defense2b])
    if player.defense3b > 20:
        positions_to_run.append([5, player.defense3b])
    if player.defensess > 20:
        positions_to_run.append([6, player.defensess])
    if player.defenself > 20:
        positions_to_run.append([7, player.defenself])
    if player.defensecf > 20:
        positions_to_run.append([8, player.defensecf])
    if player.defenserf > 20:
        positions_to_run.append([9, player.defenserf])

    players = []
    for pos_num, def_rating in positions_to_run:
        pa = 720 * 0.87 if pos_num != 2 else 720 * 0.73
        games_started = 162 * 0.87 if pos_num != 2 else 162 * 0.73

        vl_pct = platoon_splits.platoon_starts.get_vlhp_pct(pos_num=pos_num)

        vl_pa = 720 * vl_pct
        vl_gs = 162 * vl_pct

        vr_pa = 720 * (1.0 - vl_pct)
        vr_gs = 162 * (1.0 - vl_pct)

        players.append(
            BaseProjectedBatter(
                cid=player.cid + "_" + str(pos_num),
                card_player=player,
                position=pos_num,
                tpbs=TotalProjBatterStats(
                    ovr=__get_proj_batter__(
                        player=player,
                        linear_weights_formulas=linear_weights_formulas,
                        batting_player_formulas=batting_player_formulas,
                        batter_stats_for_players=batter_stats_for_players,
                        pa=pa,
                        games_started=games_started,
                        pos_num=pos_num,
                        def_rating=def_rating,
                        vlhp_pct=league_stats.get_left_pitcher_pct(),
                        lwm=lwm
                    ),
                    vl=__get_proj_batter__(
                        player=player,
                        linear_weights_formulas=linear_weights_formulas,
                        batting_player_formulas=batting_player_formulas,
                        batter_stats_for_players=batter_stats_for_players,
                        pa=vl_pa,
                        games_started=vl_gs,
                        pos_num=pos_num,
                        def_rating=def_rating,
                        vlhp_pct=0.67,
                        lwm=lwm
                    ),
                    vr=__get_proj_batter__(
                        player=player,
                        linear_weights_formulas=linear_weights_formulas,
                        batting_player_formulas=batting_player_formulas,
                        batter_stats_for_players=batter_stats_for_players,
                        pa=vr_pa,
                        games_started=vr_gs,
                        pos_num=pos_num,
                        def_rating=def_rating,
                        vlhp_pct=0.28,
                        lwm=lwm
                    )
                )
            )
        )
    return players

def generate_projected_batters(
    players: List[BaseCardPlayer],
    linear_weights_formulas: LinearWeightsFormulas,
    batting_player_formulas: BattingPlayerFormulas,
    batter_stats_for_players: Dict[str, Dict[int, Tuple[int, int]]],
    platoon_splits: PlatoonSplits,
    league_stats: LeagueStats,
    lwm: LinearWeightsModifiers
) -> List[BaseProjectedBatter]:
    projected_batters = []
    for player in players:
        projected_batters.extend(__convert_stat_player__(player, linear_weights_formulas, batting_player_formulas, batter_stats_for_players, platoon_splits, league_stats, lwm))
    return projected_batters

def __get_proj_batter_lg__(
    player: BaseCardPlayer,
    linear_weights_formulas: LinearWeightsFormulas,
    ovr_batting_player_formulas: BattingPlayerFormulas,
    vl_batting_player_formulas: BattingPlayerFormulas,
    vr_batting_player_formulas: BattingPlayerFormulas,
    ovr_batter_stats_for_players: Dict[str, any],
    vl_batter_stats_for_players: Dict[str, any],
    vr_batter_stats_for_players: Dict[str, any],
    pa: float,
    games_started: float,
    pos_num: int,
    def_rating: int,
    vlhp_pct: float,
    lwm: LinearWeightsModifiers
) -> ProjBatterStats:
    walks_vl = __get_weighted_stat__(__get_closest_stats__(vl_batter_stats_for_players["eye"][player.bats], player.eye_vl), vl_batting_player_formulas.get_walks_per_mod_pa(player.bats, player.eye_vl))
    walks_vr = __get_weighted_stat__(__get_closest_stats__(vr_batter_stats_for_players["eye"][player.bats], player.eye_vr), vr_batting_player_formulas.get_walks_per_mod_pa(player.bats, player.eye_vr))
    walks = __get_weighted_formula__(walks_vl, walks_vr, vlhp_pct=vlhp_pct) * pa * lwm.bb_mod
    
    strikeouts_vl = __get_weighted_stat__(__get_closest_stats__(vl_batter_stats_for_players["avk"][player.bats], player.avk_vl), vl_batting_player_formulas.get_strikeouts_per_pa(player.bats, player.avk_vl))
    strikeouts_vr = __get_weighted_stat__(__get_closest_stats__(vr_batter_stats_for_players["avk"][player.bats], player.avk_vr), vr_batting_player_formulas.get_strikeouts_per_pa(player.bats, player.avk_vr))
    strikeouts = __get_weighted_formula__(strikeouts_vl, strikeouts_vr, vlhp_pct=vlhp_pct) * (pa - walks) * lwm.k_mod

    homeruns_vl = __get_weighted_stat__(__get_closest_stats__(vl_batter_stats_for_players["pow"][player.bats], player.pow_vl), vl_batting_player_formulas.get_homeruns_per_mod_pa(player.bats, player.pow_vl))
    homeruns_vr = __get_weighted_stat__(__get_closest_stats__(vr_batter_stats_for_players["pow"][player.bats], player.pow_vr), vr_batting_player_formulas.get_homeruns_per_mod_pa(player.bats, player.pow_vr))
    homeruns = __get_weighted_formula__(homeruns_vl, homeruns_vr, vlhp_pct=vlhp_pct) * (pa - strikeouts - walks) * lwm.homeruns_mod

    non_hr_hits_vl = __get_weighted_stat__(__get_closest_stats__(vl_batter_stats_for_players["bab"][player.bats], player.babip_vl), vl_batting_player_formulas.get_non_hr_hits_per_mod_pa(player.bats, player.babip_vl))
    non_hr_hits_vr = __get_weighted_stat__(__get_closest_stats__(vr_batter_stats_for_players["bab"][player.bats], player.babip_vr), vr_batting_player_formulas.get_non_hr_hits_per_mod_pa(player.bats, player.babip_vr))
    non_hr_hits = __get_weighted_formula__(non_hr_hits_vl, non_hr_hits_vr, vlhp_pct=vlhp_pct) * (pa - strikeouts - homeruns - walks) * lwm.babip_mod

    xbh_vl = __get_weighted_stat__(__get_closest_stats__(vl_batter_stats_for_players["gap"][player.bats], player.gap_vl), vl_batting_player_formulas.get_xbh_per_hit(player.bats, player.gap_vl))
    xbh_vr = __get_weighted_stat__(__get_closest_stats__(vr_batter_stats_for_players["gap"][player.bats], player.gap_vr), vr_batting_player_formulas.get_xbh_per_hit(player.bats, player.gap_vr))
    xbh = __get_weighted_formula__(xbh_vl, xbh_vr, vlhp_pct=vlhp_pct) * non_hr_hits * lwm.xbh_mod

    singles = (non_hr_hits - xbh)
    triples = __get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["triple"], player.speed), ovr_batting_player_formulas.get_triple_rate_per_xbh(player.speed)) * xbh
    doubles = xbh - triples

    stolen_base_attempts = __get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["sba"], player.speed), ovr_batting_player_formulas.get_stolen_base_attempt_per_1b(player.speed)) * (singles + walks)
    successful_steals = __get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["steal_rate"], player.steal), ovr_batting_player_formulas.get_successful_steal_rate(player.steal)) * stolen_base_attempts * lwm.sb_mod
    caught_stealing = (stolen_base_attempts - successful_steals) * lwm.cs_mod

    def_formulas = ovr_batting_player_formulas.defense_formulas[pos_num] if pos_num > 0 else None
    correct_arm_stat = player.ofarm if pos_num >= 7 else player.ifarm if pos_num >= 3 else player.carm
    arm_runs = (__get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["arm_runs"], correct_arm_stat), def_formulas.get_arm_runs(correct_arm_stat)) * games_started * 9.0 if def_formulas != None else 0.0) * lwm.arm_runs_mod
    zr = (__get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["zr"], def_rating), def_formulas.get_zr(def_rating)) * games_started * 9.0 if def_formulas != None else 0.0) * lwm.zr_mod
    frame_runs = (0.0 if pos_num != 2 else __get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["frame_runs"], player.cabi), def_formulas.get_frame_runs(player.cabi)) * games_started * 9.0) * lwm.frame_runs_mod
    sba_against = (0.0 if pos_num != 2 else __get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["sba_against"], player.carm), def_formulas.get_frame_runs(player.carm)) * games_started * 9.0) * lwm.sba_against_c_mod
    cs_against = (0.0 if pos_num != 2 else __get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["cs_against"], player.carm), def_formulas.get_frame_runs(player.carm)) * sba_against) * lwm.cs_against_c_mod
    wsb_against = -1.0 * linear_weights_formulas.wsb_from_steal_stats(sba_against - cs_against, cs_against, games_started * 4.5, games_started * 4.5, 0)


    woba = linear_weights_formulas.woba_mult_by_pa_from_hits(walks, 2, singles, doubles, triples, homeruns) / pa
    wraa = linear_weights_formulas.woba_to_wraa_per_pa(woba) * pa

    wsb = linear_weights_formulas.wsb_from_steal_stats(successful_steals, caught_stealing, singles, walks, 2)
    ubr = __get_weighted_stat__(__get_closest_stats__(ovr_batter_stats_for_players["ubr"], player.baserunning), linear_weights_formulas.ubr_per_chance_from_baserunning(player.baserunning)) * non_hr_hits

    return ProjBatterStats(
        pa=pa,
        singles=singles,
        doubles=doubles,
        triples=triples,
        homeruns=homeruns,
        walks=walks,
        strikeouts=strikeouts,
        woba=woba,
        batr=wraa,
        wsb=wsb,
        ubr=ubr,
        bsr=wsb + ubr,
        zr=zr,
        frame_runs=frame_runs,
        arm_runs=arm_runs,
        wsb_against=wsb_against,
        fielding_runs=arm_runs + zr + frame_runs + wsb_against,
        war=(wraa + wsb + ubr + arm_runs + zr + frame_runs + wsb_against) / linear_weights_formulas.runs_per_win
    )

def __convert_stat_player_lg__(
    player: BaseCardPlayer,
    linear_weights_formulas: LinearWeightsFormulas,
    ovr_batting_player_formulas: BattingPlayerFormulas,
    vl_batting_player_formulas: BattingPlayerFormulas,
    vr_batting_player_formulas: BattingPlayerFormulas,
    ovr_batter_stats_for_players: Dict[str, any],
    vl_batter_stats_for_players: Dict[str, any],
    vr_batter_stats_for_players: Dict[str, any],
    league_stats: LeagueStats,
    lwm: LinearWeightsModifiers
) -> List[BattingPlayerFormulas]:
    positions_to_run = [[0, 0]]
    if player.defensec > 20:
        positions_to_run.append([2, player.defensec])
    if player.defense1b > 20:
        positions_to_run.append([3, player.defense1b])
    if player.defense2b > 20:
        positions_to_run.append([4, player.defense2b])
    if player.defense3b > 20:
        positions_to_run.append([5, player.defense3b])
    if player.defensess > 20:
        positions_to_run.append([6, player.defensess])
    if player.defenself > 20:
        positions_to_run.append([7, player.defenself])
    if player.defensecf > 20:
        positions_to_run.append([8, player.defensecf])
    if player.defenserf > 20:
        positions_to_run.append([9, player.defenserf])

    players = []
    for pos_num, def_rating in positions_to_run:

        players.append(
            BaseProjectedBatter(
                cid=player.cid + "_" + str(pos_num),
                card_player=player,
                position=pos_num,
                tpbs=TotalProjBatterStats(
                    ovr=__get_proj_batter_lg__(
                        player=player,
                        linear_weights_formulas=linear_weights_formulas,
                        ovr_batting_player_formulas=ovr_batting_player_formulas,
                        vl_batting_player_formulas=vl_batting_player_formulas,
                        vr_batting_player_formulas=vr_batting_player_formulas,
                        ovr_batter_stats_for_players=ovr_batter_stats_for_players,
                        vl_batter_stats_for_players=vl_batter_stats_for_players,
                        vr_batter_stats_for_players=vr_batter_stats_for_players,
                        pa=720,
                        games_started=162,
                        pos_num=pos_num,
                        def_rating=def_rating,
                        vlhp_pct=league_stats.get_left_pitcher_pct(),
                        lwm=lwm
                    ),
                    vl=__get_proj_batter_lg__(
                        player=player,
                        linear_weights_formulas=linear_weights_formulas,
                        ovr_batting_player_formulas=ovr_batting_player_formulas,
                        vl_batting_player_formulas=vl_batting_player_formulas,
                        vr_batting_player_formulas=vr_batting_player_formulas,
                        ovr_batter_stats_for_players=ovr_batter_stats_for_players,
                        vl_batter_stats_for_players=vl_batter_stats_for_players,
                        vr_batter_stats_for_players=vr_batter_stats_for_players,
                        pa=720,
                        games_started=162,
                        pos_num=pos_num,
                        def_rating=def_rating,
                        vlhp_pct=1,
                        lwm=lwm
                    ),
                    vr=__get_proj_batter_lg__(
                        player=player,
                        linear_weights_formulas=linear_weights_formulas,
                        ovr_batting_player_formulas=ovr_batting_player_formulas,
                        vl_batting_player_formulas=vl_batting_player_formulas,
                        vr_batting_player_formulas=vr_batting_player_formulas,
                        ovr_batter_stats_for_players=ovr_batter_stats_for_players,
                        vl_batter_stats_for_players=vl_batter_stats_for_players,
                        vr_batter_stats_for_players=vr_batter_stats_for_players,
                        pa=720,
                        games_started=162,
                        pos_num=pos_num,
                        def_rating=def_rating,
                        vlhp_pct=0,
                        lwm=lwm
                    )
                )
            )
        )
    return players

def generate_projected_batters_lg(
    players: List[BaseCardPlayer],
    linear_weights_formulas: LinearWeightsFormulas,
    ovr_batting_player_formulas: BattingPlayerFormulas,
    vl_batting_player_formulas: BattingPlayerFormulas,
    vr_batting_player_formulas: BattingPlayerFormulas,
    ovr_batter_stats_for_players: Dict[str, any],
    vl_batter_stats_for_players: Dict[str, any],
    vr_batter_stats_for_players: Dict[str, any],
    league_stats: LeagueStats,
    lwm: LinearWeightsModifiers
) -> List[BaseProjectedBatter]:
    projected_batters = []
    for player in players:
        projected_batters.extend(__convert_stat_player_lg__(
            player=player,
            linear_weights_formulas=linear_weights_formulas,
            ovr_batting_player_formulas=ovr_batting_player_formulas,
            vl_batting_player_formulas=vl_batting_player_formulas,
            vr_batting_player_formulas=vr_batting_player_formulas,
            ovr_batter_stats_for_players=ovr_batter_stats_for_players,
            vl_batter_stats_for_players=vl_batter_stats_for_players,
            vr_batter_stats_for_players=vr_batter_stats_for_players,
            league_stats=league_stats,
            lwm=lwm
        ))
    return projected_batters
