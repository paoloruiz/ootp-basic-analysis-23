from dataclasses import dataclass
from typing import Dict, List, Tuple
from analysis.determine_linear_weights import LinearWeightsFormulas
from analysis.determine_pitching_player import PitchingPlayerFormulas
from analysis.lin_weights_modifiers import LinearWeightsModifiers

from class_model.BaseCardPlayer import BaseCardPlayer
from class_model.global_stats.PitcherStats import PitcherStats
from class_model.league_stats.platoon_splits import PlatoonSplits


base_fill_pct = 0.8
base_pa_fill = 7000

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

@dataclass
class ProjectedPitcher:
    cid: str = ""
    card_player: BaseCardPlayer = None
    bf: float = 0.0
    k_per_9: float = 0.0
    bb_per_9: float = 0.0
    hr_per_9: float = 0.0
    ip_per_g: float = 0.0
    fip: float = 0.0
    only_pit_war_against: float = 0.0
    war_against: float = 0.0,
    war: float = 0.0
    war_with_relief: float = 0.0

@dataclass
class TotalProjectedPitcher:
    ovr: ProjectedPitcher
    vl: ProjectedPitcher
    vr: ProjectedPitcher

era_3_5 = (3.5 / 9.0)
era_5_5 = (5.5 / 9.0)
era_8_5 = (8.5 / 9.0)
era_12_0 = (12.0 / 9.0)

# Other pitchers behind this one also affect the "game" war - e.g. a higher stamina pitcher who throws good innings should be rewarded for going longer
def __get_other_pitchers_run_per_g__(ip_per_game_left):
    if ip_per_game_left < 1:
        return ip_per_game_left / 1.0 * era_3_5

    if ip_per_game_left < 2:
        return (ip_per_game_left - 1) / 1.0 * era_3_5 + era_3_5

    if ip_per_game_left < 4:
        return (ip_per_game_left - 2) * era_8_5 + era_3_5 + era_5_5

    return (ip_per_game_left - 4) * era_12_0 + era_3_5 + era_5_5 + era_8_5 * 2


def __get_weighted_formula__(vl: float, vr: float, vlhb_pct: float) -> float:
    return vl * vlhb_pct + vr * (1.0 - vlhb_pct)


def __convert_stat_player__(
    player: BaseCardPlayer,
    linear_weights_formulas: LinearWeightsFormulas,
    pitcher_stats: PitcherStats,
    projected_pitching_formulas: PitchingPlayerFormulas,
    pitcher_stats_for_players: Dict[str, Dict[str, Dict[int, Tuple[int, int]]]],
    platoon_splits: PlatoonSplits,
    lwm: LinearWeightsModifiers
) -> ProjectedPitcher:
    games_played = 30
    bf = __get_weighted_stat__(__get_closest_stats__(pitcher_stats_for_players["bf_per_g"], player.stamina), projected_pitching_formulas.get_bf_per_game(player.stamina)) * games_played

    hbp = pitcher_stats.get_hbp_rate(player) * bf * lwm.hbp_mod

    vlhb_pct = platoon_splits.batter_vs_pitcher_starts.get_vlhb_pct(player.throws)

    homeruns = __get_weighted_stat__(__get_closest_stats__(pitcher_stats_for_players["mov"][player.throws], player.mov_ovr),
        __get_weighted_formula__(projected_pitching_formulas.get_homeruns_per_mod_pa(player.bats, player.mov_vl), projected_pitching_formulas.get_homeruns_per_mod_pa(player.bats, player.mov_vr), 
        vlhb_pct=vlhb_pct)) * (bf - hbp) * lwm.homeruns_mod
    strikeouts = __get_weighted_stat__(__get_closest_stats__(pitcher_stats_for_players["stu"][player.throws], player.stu_ovr),
        __get_weighted_formula__(projected_pitching_formulas.get_strikeouts_per_pa(player.throws, player.stu_vl), projected_pitching_formulas.get_strikeouts_per_pa(player.throws, player.stu_vr), 
        vlhb_pct=vlhb_pct)) * (bf - hbp - homeruns) * lwm.k_mod
    walks = __get_weighted_stat__(__get_closest_stats__(pitcher_stats_for_players["ctl"][player.throws], player.ctl_ovr),
        __get_weighted_formula__(projected_pitching_formulas.get_walks_per_mod_pa(player.bats, player.ctl_vl), projected_pitching_formulas.get_walks_per_mod_pa(player.bats, player.ctl_vr), 
        vlhb_pct=vlhb_pct)) * (bf - hbp - homeruns - strikeouts) * lwm.bb_mod

    bip = bf - strikeouts - walks - homeruns - hbp

    hits = projected_pitching_formulas.get_babip_rate(player.gb_type, player.stu_ovr, player.mov_ovr, player.ctl_ovr) * bip * lwm.babip_mod
    singles, doubles, triples = pitcher_stats.get_hits_data(hits)

    stolen_base_attempts = __get_weighted_stat__(__get_closest_stats__(pitcher_stats_for_players["sba"], player.hold), projected_pitching_formulas.get_stolen_bases_attempted_per_hit(player.hold)) * (singles + walks + hbp)
    caught_stealing = __get_weighted_stat__(__get_closest_stats__(pitcher_stats_for_players["cs"], player.hold), projected_pitching_formulas.get_caught_stealing_per_steal(player.hold)) * stolen_base_attempts * lwm.cs_mod
    successful_steals = (stolen_base_attempts - caught_stealing) * lwm.sb_mod

    woba = linear_weights_formulas.woba_mult_by_pa_from_hits(walks, hbp, singles, doubles, triples, homeruns) / bf
    wraa = linear_weights_formulas.woba_to_wraa_per_pa(woba) * bf

    wsb = linear_weights_formulas.wsb_from_steal_stats(successful_steals, caught_stealing, singles, walks, hbp)

    gidp = __get_weighted_stat__(__get_closest_stats__(pitcher_stats_for_players["gidp"], player.gb_type), projected_pitching_formulas.get_gidp_per_bip(player.gb_type)) * bip
    gidp_val = gidp * linear_weights_formulas.run_value_bases_out

    ip = (bf - homeruns - singles - doubles - triples - walks - hbp + caught_stealing + gidp) / 3.0

    own_war = (wraa + wsb + gidp_val) / linear_weights_formulas.runs_per_win
    p_war = (-1 * (wraa + wsb) + gidp_val) / linear_weights_formulas.runs_per_win
    others_war = __get_other_pitchers_run_per_g__(9.0 - ip / games_played) * games_played / linear_weights_formulas.runs_per_win

    return ProjectedPitcher(
        cid=player.cid,
        card_player=player,
        bf=bf,
        k_per_9=strikeouts / ip * 9,
        bb_per_9=(walks + hbp) / ip * 9,
        hr_per_9=homeruns / ip * 9,
        ip_per_g=ip / games_played,
        fip=(13 * homeruns + 3 * (walks + hbp) - 2 * strikeouts) / ip + 3.1,
        only_pit_war_against=own_war,
        war_against=own_war + others_war,
        war=p_war,
        war_with_relief=p_war - others_war
    )

def generate_projected_pitchers(
    players: List[BaseCardPlayer],
    linear_weights_formulas: LinearWeightsFormulas,
    pitcher_stats: PitcherStats,
    projected_pitching_formulas: PitchingPlayerFormulas,
    pitcher_stats_for_players: Dict[str, Dict[int, Tuple[int, int]]],
    platoon_splits: PlatoonSplits,
    lwm=LinearWeightsModifiers
) -> List[ProjectedPitcher]:
    projected_pitchers = []
    for player in players:
        projected_pitchers.append(__convert_stat_player__(
            player,
            linear_weights_formulas,
            pitcher_stats,
            projected_pitching_formulas,
            pitcher_stats_for_players,
            platoon_splits,
            lwm
        ))
    return projected_pitchers


def __convert_stat_player_lg__(
    player: BaseCardPlayer,
    linear_weights_formulas: LinearWeightsFormulas,
    pitcher_stats: PitcherStats,
    ovr_projected_pitching_formulas: PitchingPlayerFormulas,
    vl_projected_pitching_formulas: PitchingPlayerFormulas,
    vr_projected_pitching_formulas: PitchingPlayerFormulas,
    ovr_pitcher_stats_for_players: Dict[str, Dict[int, Tuple[int, int]]],
    vl_pitcher_stats_for_players: Dict[str, Dict[int, Tuple[int, int]]],
    vr_pitcher_stats_for_players: Dict[str, Dict[int, Tuple[int, int]]],
    lwm: LinearWeightsModifiers,
    vlhb_pct: float
) -> ProjectedPitcher:
    games_played = 30
    bf = __get_weighted_stat__(__get_closest_stats__(ovr_pitcher_stats_for_players["bf_per_g"], player.stamina), ovr_projected_pitching_formulas.get_bf_per_game(player.stamina)) * games_played

    hbp = pitcher_stats.get_hbp_rate(player) * bf * lwm.hbp_mod

    homeruns_vl = __get_weighted_stat__(__get_closest_stats__(vl_pitcher_stats_for_players["mov"][player.throws], player.mov_vl), vl_projected_pitching_formulas.get_homeruns_per_mod_pa(player.throws, player.mov_vl))
    homeruns_vr = __get_weighted_stat__(__get_closest_stats__(vr_pitcher_stats_for_players["mov"][player.throws], player.mov_vr), vr_projected_pitching_formulas.get_homeruns_per_mod_pa(player.throws, player.mov_vr))
    homeruns = __get_weighted_formula__(homeruns_vl, homeruns_vr, vlhb_pct=vlhb_pct) * (bf - hbp) * lwm.homeruns_mod

    strikeouts_vl = __get_weighted_stat__(__get_closest_stats__(vl_pitcher_stats_for_players["stu"][player.throws], player.stu_vl), vl_projected_pitching_formulas.get_strikeouts_per_pa(player.throws, player.stu_vl))
    strikeouts_vr = __get_weighted_stat__(__get_closest_stats__(vr_pitcher_stats_for_players["stu"][player.throws], player.stu_vr), vr_projected_pitching_formulas.get_strikeouts_per_pa(player.throws, player.stu_vr))
    strikeouts = __get_weighted_formula__(strikeouts_vl, strikeouts_vr, vlhb_pct=vlhb_pct) * (bf - hbp - homeruns) * lwm.k_mod
    
    walks_vl = __get_weighted_stat__(__get_closest_stats__(vl_pitcher_stats_for_players["ctl"][player.throws], player.ctl_vl), vl_projected_pitching_formulas.get_walks_per_mod_pa(player.throws, player.ctl_vl))
    walks_vr = __get_weighted_stat__(__get_closest_stats__(vr_pitcher_stats_for_players["ctl"][player.throws], player.ctl_vr), vr_projected_pitching_formulas.get_walks_per_mod_pa(player.throws, player.ctl_vr))
    walks = __get_weighted_formula__(walks_vl, walks_vr, vlhb_pct=vlhb_pct) * (bf - hbp - homeruns - strikeouts) * lwm.bb_mod

    bip = bf - strikeouts - walks - homeruns - hbp

    hits = ovr_projected_pitching_formulas.get_babip_rate(player.gb_type, player.stu_ovr, player.mov_ovr, player.ctl_ovr) * bip * lwm.babip_mod
    singles, doubles, triples = pitcher_stats.get_hits_data(hits)

    stolen_base_attempts = __get_weighted_stat__(__get_closest_stats__(ovr_pitcher_stats_for_players["sba"], player.hold), ovr_projected_pitching_formulas.get_stolen_bases_attempted_per_hit(player.hold)) * (singles + walks + hbp)
    caught_stealing = __get_weighted_stat__(__get_closest_stats__(ovr_pitcher_stats_for_players["cs"], player.hold), ovr_projected_pitching_formulas.get_caught_stealing_per_steal(player.hold)) * stolen_base_attempts * lwm.cs_mod
    successful_steals = (stolen_base_attempts - caught_stealing) * lwm.sb_mod

    woba = linear_weights_formulas.woba_mult_by_pa_from_hits(walks, hbp, singles, doubles, triples, homeruns) / bf
    wraa = linear_weights_formulas.woba_to_wraa_per_pa(woba) * bf

    wsb = linear_weights_formulas.wsb_from_steal_stats(successful_steals, caught_stealing, singles, walks, hbp)

    gidp = __get_weighted_stat__(__get_closest_stats__(ovr_pitcher_stats_for_players["gidp"], player.gb_type), ovr_projected_pitching_formulas.get_gidp_per_bip(player.gb_type)) * bip
    gidp_val = gidp * linear_weights_formulas.run_value_bases_out

    ip = (bf - homeruns - singles - doubles - triples - walks - hbp + caught_stealing + gidp) / 3.0

    own_war = (wraa + wsb + gidp_val) / linear_weights_formulas.runs_per_win
    p_war = (-1 * (wraa + wsb) + gidp_val) / linear_weights_formulas.runs_per_win
    others_war = __get_other_pitchers_run_per_g__(9.0 - ip / games_played) * games_played / linear_weights_formulas.runs_per_win

    return ProjectedPitcher(
        cid=player.cid,
        card_player=player,
        bf=bf,
        k_per_9=strikeouts / ip * 9,
        bb_per_9=(walks + hbp) / ip * 9,
        hr_per_9=homeruns / ip * 9,
        ip_per_g=ip / games_played,
        fip=(13 * homeruns + 3 * (walks + hbp) - 2 * strikeouts) / ip + 3.1,
        only_pit_war_against=own_war,
        war_against=own_war + others_war,
        war=p_war,
        war_with_relief=p_war - others_war
    )

def generate_projected_pitchers_lg(
    players: List[BaseCardPlayer],
    linear_weights_formulas: LinearWeightsFormulas,
    pitcher_stats: PitcherStats,
    ovr_projected_pitching_formulas: PitchingPlayerFormulas,
    vl_projected_pitching_formulas: PitchingPlayerFormulas,
    vr_projected_pitching_formulas: PitchingPlayerFormulas,
    ovr_pitcher_stats_for_players: Dict[str, Dict[int, Tuple[int, int]]],
    vl_pitcher_stats_for_players: Dict[str, Dict[int, Tuple[int, int]]],
    vr_pitcher_stats_for_players: Dict[str, Dict[int, Tuple[int, int]]],
    platoon_splits: PlatoonSplits,
    lwm=LinearWeightsModifiers
) -> List[TotalProjectedPitcher]:
    projected_pitchers = []
    for player in players:
        projected_pitchers.append(
            TotalProjectedPitcher(
                ovr=__convert_stat_player_lg__(
                    player=player,
                    linear_weights_formulas=linear_weights_formulas,
                    pitcher_stats=pitcher_stats,
                    ovr_projected_pitching_formulas=ovr_projected_pitching_formulas,
                    vl_projected_pitching_formulas=vl_projected_pitching_formulas,
                    vr_projected_pitching_formulas=vr_projected_pitching_formulas,
                    ovr_pitcher_stats_for_players=ovr_pitcher_stats_for_players,
                    vl_pitcher_stats_for_players=vl_pitcher_stats_for_players,
                    vr_pitcher_stats_for_players=vr_pitcher_stats_for_players,
                    lwm=lwm,
                    vlhb_pct=platoon_splits.batter_vs_pitcher_starts.get_vlhb_pct(player.throws)
                ),
                vl=__convert_stat_player_lg__(
                    player=player,
                    linear_weights_formulas=linear_weights_formulas,
                    pitcher_stats=pitcher_stats,
                    ovr_projected_pitching_formulas=ovr_projected_pitching_formulas,
                    vl_projected_pitching_formulas=vl_projected_pitching_formulas,
                    vr_projected_pitching_formulas=vr_projected_pitching_formulas,
                    ovr_pitcher_stats_for_players=ovr_pitcher_stats_for_players,
                    vl_pitcher_stats_for_players=vl_pitcher_stats_for_players,
                    vr_pitcher_stats_for_players=vr_pitcher_stats_for_players,
                    lwm=lwm,
                    vlhb_pct=1
                ),
                vr=__convert_stat_player_lg__(
                    player=player,
                    linear_weights_formulas=linear_weights_formulas,
                    pitcher_stats=pitcher_stats,
                    ovr_projected_pitching_formulas=ovr_projected_pitching_formulas,
                    vl_projected_pitching_formulas=vl_projected_pitching_formulas,
                    vr_projected_pitching_formulas=vr_projected_pitching_formulas,
                    ovr_pitcher_stats_for_players=ovr_pitcher_stats_for_players,
                    vl_pitcher_stats_for_players=vl_pitcher_stats_for_players,
                    vr_pitcher_stats_for_players=vr_pitcher_stats_for_players,
                    lwm=lwm,
                    vlhb_pct=0
                ),
            )
        )
    return projected_pitchers
