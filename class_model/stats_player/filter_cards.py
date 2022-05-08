
from typing import Dict, List

from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer, single_line_player_from_base_stats_player
from class_model.stats_player.merge_stats_players import merge_base_stats_players, merge_single_line_players

def __flatten_player_ovr__(player: BaseStatsPlayer) -> List[SingleLineStatsPlayer]:
    single_line_players = []
    single_line_players.append(single_line_player_from_base_stats_player(player=player, stats_batter=player.stats_batter.ovr, stats_pitcher=player.stats_pitcher.all, stats_fielder=None))

    if player.stats_fielder != None:
        for stats_fielder in player.stats_fielder.values():
            single_line_players.append(single_line_player_from_base_stats_player(player=player, stats_batter=player.stats_batter.ovr, stats_pitcher=player.stats_pitcher.all, stats_fielder=stats_fielder))
    
    return single_line_players

def __flatten_player_starter__(player: BaseStatsPlayer) -> SingleLineStatsPlayer:
    return single_line_player_from_base_stats_player(player=player, stats_batter=None, stats_pitcher=player.stats_pitcher.all, stats_fielder=None)

def __flatten_player_reliever__(player: BaseStatsPlayer) -> SingleLineStatsPlayer:
    return single_line_player_from_base_stats_player(player=player, stats_batter=None, stats_pitcher=player.stats_pitcher.all, stats_fielder=None)


def __merge_all_players__(stats_players: List[SingleLineStatsPlayer]) -> List[SingleLineStatsPlayer]:
    cid_dict: Dict[str, SingleLineStatsPlayer] = {}
    for player in stats_players:
        if player.get_cid_with_pos() not in cid_dict:
            cid_dict[player.get_cid_with_pos()] = player
        else:
            cid_dict[player.get_cid_with_pos()] = merge_single_line_players(player, cid_dict[player.get_cid_with_pos()])

    all_players = []
    for player_id in cid_dict.keys():
        all_players.append(cid_dict[player_id])
    return all_players

def filter_cards_for_tourney(stats_players: List[Dict[str, BaseStatsPlayer]], player_type: str) -> List[SingleLineStatsPlayer]:
    if player_type == "BATTER":
        single_line_players: List[SingleLineStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                single_line_players.extend(__flatten_player_ovr__(stats_player))
        batters_only = list(filter(lambda player: player.stats_batter.batter_pa > 0, single_line_players))

        bats_merged = __merge_all_players__(batters_only)
        return bats_merged
    elif player_type == "STARTER":
        single_line_players: List[SingleLineStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                single_line_players.append(__flatten_player_starter__(stats_player))
        starters_only = list(filter(lambda player: player.stats_pitcher.pitcher_pitches_per_game > 55 and player.stats_pitcher.pitcher_ip > 0.1, single_line_players))

        return __merge_all_players__(starters_only)
    elif player_type == "RELIEVER":
        single_line_players: List[SingleLineStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                single_line_players.append(__flatten_player_reliever__(stats_player))
        relievers_only = list(filter(lambda player: player.stats_pitcher.pitcher_pitches_per_game < 30 and player.stats_pitcher.pitcher_pitches_per_game > 3 and player.stats_pitcher.pitcher_ip > 0.1, single_line_players))

        return __merge_all_players__(relievers_only)
    raise Exception("You passed a bad player type: " + player_type)