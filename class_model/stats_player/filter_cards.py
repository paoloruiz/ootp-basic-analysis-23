
from typing import Dict, List

from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer, single_line_player_from_base_stats_player
from class_model.stats_player.merge_stats_players import merge_base_stats_players, merge_single_line_players

def flatten_player_ovr(player: BaseStatsPlayer) -> List[SingleLineStatsPlayer]:
    single_line_players = []
    gs = 0

    if player.stats_fielder != None:
        for stats_fielder in player.stats_fielder.values():
            single_line_players.append(single_line_player_from_base_stats_player(player=player, stats_batter=player.stats_batter.ovr, stats_pitcher=player.stats_pitcher.all, stats_fielder=stats_fielder, mod_gs=0))
            gs += stats_fielder.fielding_games_started
    single_line_players.append(single_line_player_from_base_stats_player(player=player, stats_batter=player.stats_batter.ovr, stats_pitcher=player.stats_pitcher.all, stats_fielder=None, mod_gs=gs))
    
    return single_line_players

def flatten_player_vl(player: BaseStatsPlayer) -> List[SingleLineStatsPlayer]:
    single_line_players = []
    gs = 0

    if player.stats_fielder != None:
        for stats_fielder in player.stats_fielder.values():
            single_line_players.append(single_line_player_from_base_stats_player(player=player, stats_batter=player.stats_batter.vl, stats_pitcher=player.stats_pitcher.vl, stats_fielder=stats_fielder, mod_gs=0))
            gs += stats_fielder.fielding_games_started
    single_line_players.append(single_line_player_from_base_stats_player(player=player, stats_batter=player.stats_batter.vl, stats_pitcher=player.stats_pitcher.vl, stats_fielder=None, mod_gs=gs))
    
    return single_line_players

def flatten_player_vr(player: BaseStatsPlayer) -> List[SingleLineStatsPlayer]:
    single_line_players = []
    gs = 0

    if player.stats_fielder != None:
        for stats_fielder in player.stats_fielder.values():
            single_line_players.append(single_line_player_from_base_stats_player(player=player, stats_batter=player.stats_batter.vr, stats_pitcher=player.stats_pitcher.vr, stats_fielder=stats_fielder, mod_gs=0))
            gs += stats_fielder.fielding_games_started
    single_line_players.append(single_line_player_from_base_stats_player(player=player, stats_batter=player.stats_batter.vr, stats_pitcher=player.stats_pitcher.vr, stats_fielder=None, mod_gs=gs))
    
    return single_line_players

def __flatten_player_starter__(player: BaseStatsPlayer) -> SingleLineStatsPlayer:
    return single_line_player_from_base_stats_player(player=player, stats_batter=None, stats_pitcher=player.stats_pitcher.all, stats_fielder=None, mod_gs=0)

def __flatten_player_reliever__(player: BaseStatsPlayer) -> SingleLineStatsPlayer:
    return single_line_player_from_base_stats_player(player=player, stats_batter=None, stats_pitcher=player.stats_pitcher.all, stats_fielder=None, mod_gs=0)


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
                single_line_players.extend(flatten_player_ovr(stats_player))
        batters_only = list(filter(lambda player: player.stats_batter.batter_pa > 0, single_line_players))

        bats_merged = __merge_all_players__(batters_only)
        return bats_merged
    elif player_type == "BATTER_VL":
        single_line_players: List[SingleLineStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                single_line_players.extend(flatten_player_vl(stats_player))
        batters_only = list(filter(lambda player: player.stats_batter.batter_pa > 0, single_line_players))

        bats_merged = __merge_all_players__(batters_only)
        return bats_merged
    elif player_type == "BATTER_VR":
        single_line_players: List[SingleLineStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                single_line_players.extend(flatten_player_vr(stats_player))
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
    elif player_type == "STARTER_VL":
        single_line_players: List[SingleLineStatsPlayer] = []
        eligible_starters: List[BaseStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                if stats_player.stats_pitcher != None and stats_player.stats_pitcher.all.pitcher_pitches_per_game > 55 and stats_player.stats_pitcher.all.pitcher_ip > 0.1:
                    eligible_starters.append(stats_player)
        for sp in eligible_starters:
            single_line_players.extend(flatten_player_vl(sp))

        return __merge_all_players__(single_line_players)
    elif player_type == "STARTER_VR":
        single_line_players: List[SingleLineStatsPlayer] = []
        eligible_starters: List[BaseStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                if stats_player.stats_pitcher != None and stats_player.stats_pitcher.all.pitcher_pitches_per_game > 55 and stats_player.stats_pitcher.all.pitcher_ip > 0.1:
                    eligible_starters.append(stats_player)
        for sp in eligible_starters:
            single_line_players.extend(flatten_player_vr(sp))

        return __merge_all_players__(single_line_players)
    elif player_type == "RELIEVER":
        single_line_players: List[SingleLineStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                single_line_players.append(__flatten_player_reliever__(stats_player))
        relievers_only = list(filter(lambda player: player.stats_pitcher.pitcher_pitches_per_game < 30 and player.stats_pitcher.pitcher_pitches_per_game > 3 and player.stats_pitcher.pitcher_ip > 0.1, single_line_players))

        return __merge_all_players__(relievers_only)
    elif player_type == "RELIEVER_VL":
        single_line_players: List[SingleLineStatsPlayer] = []
        eligible_relievers: List[BaseStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                if stats_player.stats_pitcher != None and stats_player.stats_pitcher.all.pitcher_pitches_per_game < 30 and stats_player.stats_pitcher.all.pitcher_pitches_per_game > 3 and stats_player.stats_pitcher.all.pitcher_ip > 0.1:
                    eligible_relievers.append(stats_player)
        for rp in eligible_relievers:
            single_line_players.extend(flatten_player_vl(rp))

        return __merge_all_players__(single_line_players)
    elif player_type == "RELIEVER_VR":
        single_line_players: List[SingleLineStatsPlayer] = []
        eligible_relievers: List[BaseStatsPlayer] = []
        for stats_players_league in stats_players:
            for stats_player in stats_players_league.values():
                if stats_player.stats_pitcher != None and stats_player.stats_pitcher.all.pitcher_pitches_per_game < 30 and stats_player.stats_pitcher.all.pitcher_pitches_per_game > 3 and stats_player.stats_pitcher.all.pitcher_ip > 0.1:
                    eligible_relievers.append(stats_player)
        for rp in eligible_relievers:
            single_line_players.extend(flatten_player_vr(rp))

        return __merge_all_players__(single_line_players)
    raise Exception("You passed a bad player type: " + player_type)