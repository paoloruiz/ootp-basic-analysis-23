from dataclasses import dataclass
from typing import Dict, List
from util.ip_math import add_ip, ip_to_ip_w_remainder

def __search_with_reasonable_error__(headers, index_name):
    try:
        return headers.index(index_name)
    except ValueError:
        raise Exception(index_name + " not included in headers: " + str(headers))

def __search_with_no_error__(headers, index_name):
    try:
        return headers.index(index_name)
    except ValueError:
        return -1

def __safe_int__(possible_int: str):
    try: 
        return int(possible_int)
    except:
        return 0

def headers_to_cur_projected_pitcher_header_indices(headers: List[str]) -> Dict[str, int]:
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
    header_indices["ibb_index"] = __search_with_no_error__(headers, "IBB")
    header_indices["id_index"] = __search_with_reasonable_error__(headers, "playerid")

    return header_indices


@dataclass
class CurProjectedPitcher:
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
    playerid: str

    def get_k_per_9(self):
        return self.strikeouts / ip_to_ip_w_remainder(self.ip) * 9

    def get_bb_per_9(self):
        return self.walks / ip_to_ip_w_remainder(self.ip) * 9

    def get_hr_per_9(self):
        return self.homeruns / ip_to_ip_w_remainder(self.ip) * 9

def new_cur_projected_pitcher(header_indices: Dict[str, int], play_line: List[str]) -> CurProjectedPitcher:
    ibb = int(play_line[header_indices["ibb_index"]]) if header_indices["ibb_index"] > -1 else 0
    return CurProjectedPitcher(
        name=play_line[header_indices["name_index"]],
        team=play_line[header_indices["team_index"]],
        games=int(play_line[header_indices["games_index"]]),
        games_started=int(play_line[header_indices["games_started_index"]]),
        ip=float(play_line[header_indices["ip_index"]]),
        wins=int(play_line[header_indices["wins_index"]]),
        losses=int(play_line[header_indices["losses_index"]]),
        saves=__safe_int__(play_line[header_indices["saves_index"]]),
        holds=__safe_int__(play_line[header_indices["holds_index"]]),
        hits=int(play_line[header_indices["hits_index"]]),
        earned_runs=int(play_line[header_indices["earned_runs_index"]]),
        homeruns=int(play_line[header_indices["homeruns_index"]]),
        strikeouts=int(play_line[header_indices["strikeouts_index"]]),
        walks=int(play_line[header_indices["walks_index"]]) - ibb,
        playerid=play_line[header_indices["id_index"]]
    )

def join_projected_pitcher(a: CurProjectedPitcher, b: CurProjectedPitcher) -> CurProjectedPitcher:
    return CurProjectedPitcher(
        name=a.name,
        team=a.team,
        games=a.games + b.games,
        games_started=a.games_started + b.games_started,
        ip=add_ip(a.ip, b.ip),
        wins=a.wins + b.wins,
        losses=a.losses + b.losses,
        saves=a.saves + b.saves,
        holds=a.holds + b.holds,
        hits=a.hits + b.hits,
        earned_runs=a.earned_runs + b.earned_runs,
        homeruns=a.homeruns + b.homeruns,
        strikeouts=a.strikeouts + b.strikeouts,
        walks=a.walks + b.walks,
        playerid=a.playerid
    )