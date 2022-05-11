from dataclasses import dataclass
from typing import List
from analysis.determine_batting_player import BattingPlayerFormulas
from analysis.determine_linear_weights import LinearWeightsFormulas
from analysis.determine_pitching_player import PitchingPlayerFormulas

from class_model.BaseCardPlayer import BaseCardPlayer
from class_model.global_stats.PitcherStats import PitcherStats


@dataclass
class ProjectedPitcher:
    cid: str = ""
    card_player: BaseCardPlayer = None
    bf: float = 0.0
    k_per_9: float = 0.0
    bb_per_9: float = 0.0
    hr_per_9: float = 0.0
    fip: float = 0.0
    war_against: float = 0.0


def __convert_stat_player__(player: BaseCardPlayer, linear_weights_formulas: LinearWeightsFormulas, pitcher_stats: PitcherStats, projected_pitching_formulas: PitchingPlayerFormulas) -> ProjectedPitcher:
    bf = 500

    hbp = pitcher_stats.get_hbp_rate(player) * bf

    strikeouts = projected_pitching_formulas.get_strikeouts_per_pa(player.throws, player.stu_ovr) * (bf - hbp)
    walks = projected_pitching_formulas.get_walks_per_mod_pa(player.bats, player.eye_ovr) * (bf - strikeouts - hbp)
    homeruns = projected_pitching_formulas.get_homeruns_per_mod_pa(player.bats, player.pow_ovr) * (bf - strikeouts - hbp)

    bip = bf - strikeouts - walks - homeruns - hbp

    hits = projected_pitching_formulas.get_babip_rate(player.gb_type, player.stu_ovr, player.mov_ovr, player.ctl_ovr) * bip
    singles, doubles, triples = pitcher_stats.get_hits_data(hits)

    stolen_base_attempts = projected_pitching_formulas.get_stolen_bases_attempted_per_hit(player.hold) * (singles + walks + hbp)
    caught_stealing = projected_pitching_formulas.get_caught_stealing_per_steal(player.hold) * stolen_base_attempts
    successful_steals = stolen_base_attempts - caught_stealing

    woba = linear_weights_formulas.woba_mult_by_pa_from_hits(walks, hbp, singles, doubles, triples, homeruns) / bf
    wraa = linear_weights_formulas.woba_to_wraa_per_pa(woba) * bf

    wsb = linear_weights_formulas.wsb_from_steal_stats(successful_steals, caught_stealing)

    gidp = projected_pitching_formulas.get_gidp_per_bip(player.gb_type) * bip
    gidp_val = gidp * linear_weights_formulas.run_value_bases_out

    ip = (bf - homeruns - singles - doubles - triples - walks - hbp + caught_stealing + gidp) / 3.0

    return ProjectedPitcher(
        cid=player.cid,
        card_player=player,
        bf=bf,
        k_per_9=strikeouts / ip * 9,
        bb_per_9=(walks + hbp) / ip * 9,
        hr_per_9=homeruns / ip * 9,
        fip=(13 * homeruns + 3 * (walks + hbp) - 2 * strikeouts) / ip + 3.1,
        war_against=(wraa + wsb + gidp_val) / linear_weights_formulas.runs_per_win,
    )

def generate_projected_pitchers(players: List[BaseCardPlayer], linear_weights_formulas: LinearWeightsFormulas, pitcher_stats: PitcherStats, projected_pitching_formulas: PitchingPlayerFormulas) -> List[ProjectedPitcher]:
    projected_pitchers = []
    for player in players:
        projected_pitchers.append(__convert_stat_player__(player, linear_weights_formulas, pitcher_stats, projected_pitching_formulas))
    return projected_pitchers
