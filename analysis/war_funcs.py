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

def get_pitcher_war_func(woba_constants: LinearWeightsFormulas, pitcher_stats: PitcherStats, num_bf: int, incorporate_others_war: bool) -> Callable[[SingleLineStatsPlayer], float]:
    def get_war_against(player: SingleLineStatsPlayer):
        bf = player.stats_pitcher.pitcher_bf
        games_played = player.stats_pitcher.pitcher_games / bf * num_bf
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
        wsb = woba_constants.wsb_from_steal_stats(stolen_bases_against, caught_stealing_against, singles_against, walks_against, hbp_against)
        gidp_val = woba_constants.run_value_bases_out * gidp

        ip = (bf - homeruns_against - singles_against - doubles_against - triples_against - walks_against - hbp_against + caught_stealing_against + gidp) / 3.0
        p_war = (-1 * (wraa + wsb) + gidp_val) / woba_constants.runs_per_win

        other_war = 0.0
        if incorporate_others_war:
            other_war = __get_other_pitchers_run_per_g__(9.0 - ip / games_played) * games_played / woba_constants.runs_per_win

        return p_war + other_war
    return get_war_against