from dataclasses import dataclass
from typing import Dict, List

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

def headers_to_cur_projected_batter_header_indices(headers: List[str]) -> Dict[str, int]:
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
    header_indices["ibb_index"] = __search_with_no_error__(headers, "IBB")
    header_indices["k_index"] = __search_with_reasonable_error__(headers, "SO")
    header_indices["hbp_index"] = __search_with_reasonable_error__(headers, "HBP")
    header_indices["sb_index"] = __search_with_reasonable_error__(headers, "SB")
    header_indices["cs_index"] = __search_with_reasonable_error__(headers, "CS")
    header_indices["sf_index"] = __search_with_no_error__(headers, "SF")
    header_indices["id_index"] = __search_with_reasonable_error__(headers, "playerid")

    return header_indices


@dataclass
class CurProjectedBatter:
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

    def get_k_rate(self) -> float:
        return self.strikeouts / (self.pa - self.hbp - self.walks)

    def get_bb_rate(self) -> float:
        return self.walks / (self.pa - self.hbp)

    def get_hr_rate(self) -> float:
        return self.homeruns / (self.pa - self.hbp)

    def get_babip_rate(self) -> float:
        return (self.singles + self.doubles + self.triples) / (self.ab - self.homeruns - self.strikeouts)

    def get_xbh_rate(self) -> float:
        return (self.doubles + self.triples) / (self.singles + self.doubles + self.triples)

def new_cur_projected_batter(header_indices: Dict[str, int], play_line: List[str]) -> CurProjectedBatter:
    sf = int(play_line[header_indices["sf_index"]]) if header_indices["sf_index"] > -1 else 0
    ibb = int(play_line[header_indices["ibb_index"]]) if header_indices["ibb_index"] > -1 else 0
    return CurProjectedBatter(
        name=play_line[header_indices["name_index"]],
        team=play_line[header_indices["team_index"]],
        games=int(play_line[header_indices["games_index"]]),
        pa=int(play_line[header_indices["pa_index"]]) - sf,
        ab=int(play_line[header_indices["ab_index"]]),
        singles=int(play_line[header_indices["hits_index"]]) - int(play_line[header_indices["doubles_index"]]) - int(play_line[header_indices["triples_index"]]) - int(play_line[header_indices["homeruns_index"]]),
        doubles=int(play_line[header_indices["doubles_index"]]),
        triples=int(play_line[header_indices["triples_index"]]),
        homeruns=int(play_line[header_indices["homeruns_index"]]),
        runs=int(play_line[header_indices["runs_index"]]),
        walks=int(play_line[header_indices["walks_index"]]) - ibb,
        strikeouts=int(play_line[header_indices["k_index"]]),
        hbp=int(play_line[header_indices["hbp_index"]]),
        sb=int(play_line[header_indices["sb_index"]]),
        cs=int(play_line[header_indices["cs_index"]]),
        playerid=play_line[header_indices["id_index"]]
    )

def join_projected_batters(a: CurProjectedBatter, b: CurProjectedBatter) -> CurProjectedBatter:
    return CurProjectedBatter(
        name=a.name,
        team=a.team,
        games=a.games + b.games,
        pa=a.pa + b.pa,
        ab=a.ab + b.ab,
        singles=a.singles + b.singles,
        doubles=a.doubles + b.doubles,
        triples=a.triples + b.triples,
        homeruns=a.homeruns + b.homeruns,
        runs=a.runs + b.runs,
        walks=a.walks + b.walks,
        strikeouts=a.strikeouts + b.strikeouts,
        hbp=a.hbp + b.hbp,
        sb=a.sb + b.sb,
        cs=a.cs + b.cs,
        playerid=a.playerid
    )