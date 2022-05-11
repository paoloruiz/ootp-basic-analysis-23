from typing import Callable
from analysis.determine_linear_weights import LinearWeightsFormulas, get_positional_adjustment

from class_model.BaseStatsPlayer import SingleLineStatsPlayer
from class_model.global_stats.AllLeagueStats import LeagueStats
from class_model.global_stats.PitcherStats import PitcherStats


def get_batter_war_func(woba_constants: LinearWeightsFormulas, league_stats: LeagueStats) -> Callable[[SingleLineStatsPlayer], float]:
    def calculate_war(player: SingleLineStatsPlayer) -> float:
        batr = (player.stats_batter.batter_batting_runs / player.stats_batter.batter_pa) * player.get_assumed_pa()
        basr = (player.stats_batter.batter_base_running_runs / player.stats_batter.batter_pa) * player.get_assumed_pa()
        fielding_runs = player.get_prorated_zr() + player.get_prorated_arm_runs() + player.get_prorated_frame_runs()
        positional_adjustment = player.get_assumed_ip() / (9 * 162) * get_positional_adjustment(player.get_fielding_position())
        replacement_level_adjustment = league_stats.get_replacement_level_runs_per_pa() * player.get_assumed_pa()

        return (batr + basr + fielding_runs + positional_adjustment + replacement_level_adjustment) / woba_constants.runs_per_win
    return calculate_war

def get_pitcher_war_func(woba_constants: LinearWeightsFormulas, pitcher_stats: PitcherStats, num_bf: int) -> Callable[[SingleLineStatsPlayer], float]:
    def get_war_against(player: SingleLineStatsPlayer):
        bf = player.stats_pitcher.pitcher_bf
        singles_against = player.stats_pitcher.pitcher_singles / bf * num_bf
        doubles_against = player.stats_pitcher.pitcher_doubles / bf * num_bf
        triples_against = player.stats_pitcher.pitcher_triples / bf * num_bf
        homeruns_against = player.stats_pitcher.pitcher_homeruns / bf * num_bf
        walks_against = (player.stats_pitcher.pitcher_walks - player.stats_pitcher.pitcher_intentional_walks) / bf * num_bf
        hbp_against = pitcher_stats.get_hbp_rate(player.card_player) * num_bf

        stolen_bases_against = player.stats_pitcher.pitcher_stolen_bases / bf * num_bf
        caught_stealing_against = player.stats_pitcher.pitcher_caught_stealing / bf * num_bf

        gidp = player.stats_pitcher.pitcher_double_plays / bf * num_bf

        wraa = woba_constants.woba_to_wraa_per_pa(woba_constants.woba_mult_by_pa_from_hits(walks_against, hbp_against, singles_against, doubles_against, triples_against, homeruns_against) / num_bf) * num_bf
        wsb = woba_constants.wsb_from_steal_stats(stolen_bases_against, caught_stealing_against)
        gidp_val = woba_constants.run_value_bases_out * gidp

        return (wraa + wsb + gidp_val) / woba_constants.runs_per_win
    return get_war_against