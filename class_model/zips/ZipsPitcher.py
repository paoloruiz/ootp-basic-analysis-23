from dataclasses import dataclass
import math
from typing import Dict, List

def __search_with_reasonable_error__(headers, index_name):
    try:
        return headers.index(index_name)
    except ValueError:
        raise Exception(index_name + " not included in headers: " + str(headers))

def __get_ip__(ip: float) -> float:
    ip_int = math.floor(ip)
    ip_remainder = ip % 1
    if ip_remainder > 0 and ip_remainder < 0.5:
        return ip_int + 0.1

    if ip_remainder > 0.5 and ip_remainder < 0.9:
        return ip_int + 0.2
    
    return ip_int

def headers_to_zips_pitcher_header_indices(headers: List[str]) -> Dict[str, int]:
    header_indices = {}

    header_indices["name_index"] = __search_with_reasonable_error__(headers, "Name")
    header_indices["team_index"] = __search_with_reasonable_error__(headers, "Team")
    header_indices["games_index"] = __search_with_reasonable_error__(headers, "G")
    header_indices["games_started_index"] = __search_with_reasonable_error__(headers, "GS")
    header_indices["ip_index"] = __search_with_reasonable_error__(headers, "IP")
    header_indices["wins_index"] = __search_with_reasonable_error__(headers, "W")
    header_indices["losses_index"] = __search_with_reasonable_error__(headers, "L")
    header_indices["saves_index"] = __search_with_reasonable_error__(headers, "SV")
    header_indices["holds_index"] = __search_with_reasonable_error__(headers, "HLD")
    header_indices["hits_index"] = __search_with_reasonable_error__(headers, "H")
    header_indices["earned_runs_index"] = __search_with_reasonable_error__(headers, "ER")
    header_indices["homeruns_index"] = __search_with_reasonable_error__(headers, "HR")
    header_indices["strikeouts_index"] = __search_with_reasonable_error__(headers, "SO")
    header_indices["walks_index"] = __search_with_reasonable_error__(headers, "BB")
    header_indices["whip_index"] = __search_with_reasonable_error__(headers, "WHIP")
    header_indices["k9_index"] = __search_with_reasonable_error__(headers, "K9")
    header_indices["bb9_index"] = __search_with_reasonable_error__(headers, "BB9")
    header_indices["id_index"] = __search_with_reasonable_error__(headers, "playerid")

    return header_indices


@dataclass
class ZipsPitcher:
    name: str
    team: str
    games: int
    games_started: int
    ip: float
    wins: int
    losses: int
    saves: int
    holds: int
    hits: int
    earned_runs: int
    homeruns: int
    strikeouts: int
    walks: int
    whip: float
    k_per_9: float
    bb_per_9: float
    hr_per_9: float
    playerid: str

def new_zips_pitcher(header_indices: Dict[str, int], play_line: List[str]) -> ZipsPitcher:
    return ZipsPitcher(
        name=play_line[header_indices["name_index"]],
        team=play_line[header_indices["team_index"]],
        games=int(play_line[header_indices["games_index"]]),
        games_started=int(play_line[header_indices["games_started_index"]]),
        ip=__get_ip__(float(play_line[header_indices["ip_index"]])),
        wins=int(play_line[header_indices["wins_index"]]),
        losses=int(play_line[header_indices["losses_index"]]),
        saves=int(play_line[header_indices["saves_index"]]),
        holds=int(play_line[header_indices["holds_index"]]),
        hits=int(play_line[header_indices["hits_index"]]),
        earned_runs=int(play_line[header_indices["earned_runs_index"]]),
        homeruns=int(play_line[header_indices["homeruns_index"]]),
        strikeouts=int(play_line[header_indices["strikeouts_index"]]),
        walks=int(play_line[header_indices["walks_index"]]),
        whip=float(play_line[header_indices["whip_index"]]),
        k_per_9=float(play_line[header_indices["k9_index"]]),
        bb_per_9=float(play_line[header_indices["bb9_index"]]),
        hr_per_9=float(play_line[header_indices["k9_index"]]) / float(play_line[header_indices["strikeouts_index"]]) * int(play_line[header_indices["homeruns_index"]]),
        playerid=play_line[header_indices["id_index"]]
    )