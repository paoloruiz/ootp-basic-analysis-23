from dataclasses import dataclass
from typing import Dict, List

def __search_with_reasonable_error__(headers, index_name):
    try:
        return headers.index(index_name)
    except ValueError:
        raise Exception(index_name + " not included in headers: " + str(headers))

def headers_to_zips_batter_header_indices(headers: List[str]) -> Dict[str, int]:
    header_indices = {}

    header_indices["name_index"] = __search_with_reasonable_error__(headers, "Name")
    header_indices["team_index"] = __search_with_reasonable_error__(headers, "Team")
    header_indices["games_index"] = __search_with_reasonable_error__(headers, "G")
    header_indices["pa_index"] = __search_with_reasonable_error__(headers, "PA")
    header_indices["ab_index"] = __search_with_reasonable_error__(headers, "AB")
    header_indices["hits_index"] = __search_with_reasonable_error__(headers, "H")
    header_indices["doubles_index"] = __search_with_reasonable_error__(headers, "2B")
    header_indices["triples_index"] = __search_with_reasonable_error__(headers, "3B")
    header_indices["homeruns_index"] = __search_with_reasonable_error__(headers, "HR")
    header_indices["runs_index"] = __search_with_reasonable_error__(headers, "R")
    header_indices["walks_index"] = __search_with_reasonable_error__(headers, "BB")
    header_indices["k_index"] = __search_with_reasonable_error__(headers, "SO")
    header_indices["hbp_index"] = __search_with_reasonable_error__(headers, "HBP")
    header_indices["sb_index"] = __search_with_reasonable_error__(headers, "SB")
    header_indices["cs_index"] = __search_with_reasonable_error__(headers, "CS")
    header_indices["id_index"] = __search_with_reasonable_error__(headers, "playerid")

    return header_indices


@dataclass
class ZipsBatter:
    name: str
    team: str
    games: int
    pa: int
    ab: int
    singles: int
    doubles: int
    triples: int
    homeruns: int
    runs: int
    walks: int
    strikeouts: int
    hbp: int
    sb: int
    cs: int
    playerid: str

def new_zips_batter(header_indices: Dict[str, int], play_line: List[str]) -> ZipsBatter:
    return ZipsBatter(
        name=play_line[header_indices["name_index"]],
        team=play_line[header_indices["team_index"]],
        games=int(play_line[header_indices["games_index"]]),
        pa=int(play_line[header_indices["pa_index"]]),
        ab=int(play_line[header_indices["ab_index"]]),
        singles=int(play_line[header_indices["hits_index"]]) - int(play_line[header_indices["doubles_index"]]) - int(play_line[header_indices["triples_index"]]) - int(play_line[header_indices["homeruns_index"]]),
        doubles=int(play_line[header_indices["doubles_index"]]),
        triples=int(play_line[header_indices["triples_index"]]),
        homeruns=int(play_line[header_indices["homeruns_index"]]),
        runs=int(play_line[header_indices["runs_index"]]),
        walks=int(play_line[header_indices["walks_index"]]),
        strikeouts=int(play_line[header_indices["k_index"]]),
        hbp=int(play_line[header_indices["hbp_index"]]),
        sb=int(play_line[header_indices["sb_index"]]),
        cs=int(play_line[header_indices["cs_index"]]),
        playerid=play_line[header_indices["id_index"]]
    )