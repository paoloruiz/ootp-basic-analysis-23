from dataclasses import dataclass
from typing import List
from analysis.determine_batting_player import BattingPlayerFormulas
from analysis.determine_linear_weights import LinearWeightsFormulas

from class_model.BaseCardPlayer import BaseCardPlayer


@dataclass
class BaseProjectedBatter:
    cid: str = ""
    card_player: BaseCardPlayer = None
    position: int = 0
    pa: float = 0.0
    woba: float = 0.0
    batr: float = 0.0
    wsb: float = 0.0
    ubr: float = 0.0
    bsr: float = 0.0
    fielding_runs: float = 0.0
    war: float = 0.0


def __convert_stat_player__(player: BaseCardPlayer, linear_weights_formulas: LinearWeightsFormulas, batting_player_formulas: BattingPlayerFormulas) -> List[BattingPlayerFormulas]:
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
        pa = 720 * 0.92 if pos_num != 2 else 720 * 0.78
        games_started = 162 * 0.92 if pos_num != 2 else 162 * 0.78

        strikeouts = batting_player_formulas.get_strikeouts_per_pa(player.bats, player.avk_ovr) * pa
        walks = batting_player_formulas.get_walks_per_mod_pa(player.bats, player.eye_ovr) * (pa - strikeouts)
        homeruns = batting_player_formulas.get_homeruns_per_mod_pa(player.bats, player.pow_ovr) * (pa - strikeouts)
        non_hr_hits = batting_player_formulas.get_non_hr_hits_per_mod_pa(player.bats, player.babip_ovr) * (pa - strikeouts - homeruns - walks)
        xbh = batting_player_formulas.get_xbh_per_hit(player.bats, player.gap_ovr) * non_hr_hits
        singles = non_hr_hits - xbh
        triples = batting_player_formulas.get_triple_rate_per_xbh(player.speed) * xbh
        doubles = xbh - triples

        stolen_base_attempts = batting_player_formulas.get_stolen_base_attempt_per_1b(player.speed) * (singles + walks)
        successful_steals = batting_player_formulas.get_successful_steal_rate(player.steal) * stolen_base_attempts
        caught_stealing = stolen_base_attempts - successful_steals

        def_formulas = batting_player_formulas.defense_formulas[pos_num] if pos_num > 0 else None
        correct_arm_stat = player.ofarm if pos_num >= 7 else player.ifarm if pos_num >= 3 else player.carm
        arm_runs = def_formulas.get_arm_runs(correct_arm_stat) * games_started * 9.0 if def_formulas != None else 0.0
        zr = def_formulas.get_zr(def_rating) * games_started * 9.0 if def_formulas != None else 0.0
        frame_runs = 0.0 if pos_num != 2 else def_formulas.get_frame_runs(player.cabi) * games_started * 9.0

        woba = linear_weights_formulas.woba_mult_by_pa_from_hits(walks, 0, singles, doubles, triples, homeruns) / pa
        wraa = linear_weights_formulas.woba_to_wraa_per_pa(woba) * pa

        wsb = linear_weights_formulas.wsb_from_steal_stats(successful_steals, caught_stealing)
        ubr = linear_weights_formulas.ubr_per_chance_from_baserunning(player.baserunning) * non_hr_hits


        players.append(
            BaseProjectedBatter(
                cid=player.cid + "_" + str(pos_num),
                card_player=player,
                position=pos_num,
                pa=pa,
                woba=woba,
                batr=wraa,
                wsb=wsb,
                ubr=ubr,
                bsr=wsb + ubr,
                fielding_runs=arm_runs + zr + frame_runs,
                war=(wraa + wsb + ubr + arm_runs + zr + frame_runs) / linear_weights_formulas.runs_per_win
            )
        )
    return players

def generate_projected_batters(players: List[BaseCardPlayer], linear_weights_formulas: LinearWeightsFormulas, batting_player_formulas: BattingPlayerFormulas) -> List[BaseProjectedBatter]:
    projected_batters = []
    for player in players:
        projected_batters.extend(__convert_stat_player__(player, linear_weights_formulas, batting_player_formulas))
    return projected_batters
