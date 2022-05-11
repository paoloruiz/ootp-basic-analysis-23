import os
from typing import Dict
from class_model.BaseCardPlayer import BaseCardPlayer, new_base_card_player, headers_to_header_indices
from class_model.BaseStatsPlayer import BaseStatsPlayer, new_base_stats_player, read_in_fielder_info, read_in_ovr_info, read_in_reliever_info, read_in_starter_info, read_in_vl_info, read_in_vr_info
from class_model.global_stats.AllLeagueStats import AllLeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from class_model.stats_player.header_indices import stats_headers_to_header_indices


def load_card_players():
    f = open('data/cards/pt_card_list.csv', 'r')

    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').strip())(h) for h in headers_split]
    header_indices = headers_to_header_indices(headers)
    players = {}
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        base_card_player = new_base_card_player(header_indices, play_line)
        players[base_card_player.cid] = base_card_player
    f.close()

    return players


def load_stats_players(
    directory: str,
    league_type: str,
    card_players: Dict[str, BaseCardPlayer],
    all_league_stats: AllLeagueStats,
    all_pitcher_stats: PitcherStats
):
    filenames = list(os.listdir(directory))
    if not "ovr.csv" in filenames:
        raise Exception(directory + " has no ovr file")

    f = open(directory + "/ovr.csv", "r")
    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').strip())(h) for h in headers_split]
    header_indices = stats_headers_to_header_indices(headers)

    players: Dict[str, BaseStatsPlayer] = {}
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        base_stats_player = new_base_stats_player(header_indices, play_line, card_players)
        players[base_stats_player.cid_with_id] = base_stats_player
        read_in_ovr_info(header_indices=header_indices, play_line=play_line, existing_players=players)
        all_league_stats.capture_player_data(league_type, players[base_stats_player.cid_with_id])
        all_pitcher_stats.capture_player_data(players[base_stats_player.cid_with_id])
    f.close()

    if "vl.csv" in filenames:
        f = open(directory + "/vl.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_vl_info(header_indices=header_indices, play_line=play_line, existing_players=players)
        f.close()

    if "vr.csv" in filenames:
        f = open(directory + "/vr.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_vr_info(header_indices=header_indices, play_line=play_line, existing_players=players)
        f.close()

    if "starter.csv" in filenames:
        f = open(directory + "/starter.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_starter_info(header_indices=header_indices, play_line=play_line, existing_players=players)
        f.close()

    if "reliever.csv" in filenames:
        f = open(directory + "/reliever.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_reliever_info(header_indices=header_indices, play_line=play_line, existing_players=players)
        f.close()

    if "def2.csv" in filenames:
        f = open(directory + "/def2.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_fielder_info(header_indices=header_indices, play_line=play_line, position_number=2, existing_players=players)
        f.close()

    if "def3.csv" in filenames:
        f = open(directory + "/def3.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_fielder_info(header_indices=header_indices, play_line=play_line, position_number=3, existing_players=players)
        f.close()

    if "def4.csv" in filenames:
        f = open(directory + "/def4.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_fielder_info(header_indices=header_indices, play_line=play_line, position_number=4, existing_players=players)
        f.close()

    if "def5.csv" in filenames:
        f = open(directory + "/def5.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_fielder_info(header_indices=header_indices, play_line=play_line, position_number=5, existing_players=players)
        f.close()

    if "def6.csv" in filenames:
        f = open(directory + "/def6.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_fielder_info(header_indices=header_indices, play_line=play_line, position_number=6, existing_players=players)
        f.close()

    if "def7.csv" in filenames:
        f = open(directory + "/def7.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_fielder_info(header_indices=header_indices, play_line=play_line, position_number=7, existing_players=players)
        f.close()

    if "def8.csv" in filenames:
        f = open(directory + "/def8.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_fielder_info(header_indices=header_indices, play_line=play_line, position_number=8, existing_players=players)
        f.close()

    if "def9.csv" in filenames:
        f = open(directory + "/def9.csv", "r")
        # read headers line
        f.readline()
        for line_unparsed in f.readlines():
            line_split = line_unparsed.split(',')
            play_line = [(lambda x: x.strip())(x) for x in line_split]
            read_in_fielder_info(header_indices=header_indices, play_line=play_line, position_number=9, existing_players=players)
        f.close()

    return players
