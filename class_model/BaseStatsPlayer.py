from dataclasses import dataclass, field
from typing import Dict, List

from class_model.BaseCardPlayer import BaseCardPlayer
from class_model.stats_player.batter import StatsBatter, new_stats_batter
from class_model.stats_player.fielder import StatsFielder, new_stats_fielder
from class_model.stats_player.header_indices import StatsHeaderIndices
from class_model.stats_player.pitcher import StatsPitcher, new_stats_pitcher
from util.ip_math import ip_to_ip_w_remainder

@dataclass
class TotalStatsBatter:
    ovr: StatsBatter = None
    vl: StatsBatter = None
    vr: StatsBatter = None

@dataclass
class TotalStatsPitcher:
    all: StatsPitcher = None
    starter: StatsPitcher = None
    reliever: StatsPitcher = None


@dataclass
class BaseStatsPlayer:
    cid: str = ""
    cid_with_id: str = ""
    card_player: BaseCardPlayer = None
    position: str = ""
    stats_batter: TotalStatsBatter = None
    stats_pitcher: TotalStatsPitcher = None
    stats_fielder: Dict[int, StatsFielder] = field(default=dict)

@dataclass
class SingleLineStatsPlayer:
    cid: str = ""
    card_player: BaseCardPlayer = None
    position: str = ""
    stats_batter: StatsBatter = None
    stats_pitcher: StatsPitcher = None
    stats_fielder: StatsFielder = None

    def get_fielding_position(self) -> int:
        if self.stats_fielder != None:
            return self.stats_fielder.fielding_position
        return 0

    # TODO have the get_functions on this one?
    def get_cid_with_pos(self) -> str:
        return self.cid + "_" + str(self.get_fielding_position())

    def get_assumed_pa(self) -> float:
        pos = self.get_fielding_position()
        if pos == 2:
            return 720 * 0.78
        elif pos == 0:
            return 720
        else:
            return 720 * 0.92

    def get_assumed_ip(self) -> float:
        pos = self.get_fielding_position()
        if pos == 2:
            return 162 * 0.78 * 9.0
        elif pos == 0:
            return 162 * 9.0
        else:
            return 162 * 0.92 * 9.0

    def get_prorated_zr(self) -> float:
        if self.stats_fielder == None or self.stats_fielder.fielding_ip < 1.0:
            return 0.0
        return self.stats_fielder.fielding_zr / ip_to_ip_w_remainder(self.stats_fielder.fielding_ip) * self.get_assumed_ip()

    def get_prorated_frame_runs(self) -> float:
        if self.stats_fielder == None or self.stats_fielder.fielding_ip < 1.0:
            return 0.0
        return self.stats_fielder.fielding_framing_runs / ip_to_ip_w_remainder(self.stats_fielder.fielding_ip) * self.get_assumed_ip()

    def get_prorated_arm_runs(self) -> float:
        if self.stats_fielder == None or self.stats_fielder.fielding_ip < 1.0:
            return 0.0
        return self.stats_fielder.fielding_arm_runs / ip_to_ip_w_remainder(self.stats_fielder.fielding_ip) * self.get_assumed_ip()
        

def new_base_stats_player(header_indices: StatsHeaderIndices, play_line: List[str], base_card_players: Dict[str, BaseCardPlayer]) -> BaseStatsPlayer:
    return BaseStatsPlayer(
        cid=str(play_line[header_indices.main_header_indices["cid_index"]]),
        cid_with_id=play_line[header_indices.main_header_indices["cid_index"]] + "_" + play_line[header_indices.main_header_indices["id_index"]],
        card_player=base_card_players[play_line[header_indices.main_header_indices["cid_index"]]],
        position=str(play_line[header_indices.main_header_indices["pos_index"]]),
        stats_batter=StatsBatter(),
        stats_pitcher=StatsPitcher(),
        stats_fielder={}
    )

def read_in_ovr_info(header_indices: StatsHeaderIndices, play_line: List[str], existing_players: Dict[str, BaseStatsPlayer]):
    cid_with_id = play_line[header_indices.main_header_indices["cid_index"]] + "_" + play_line[header_indices.main_header_indices["id_index"]]
    if cid_with_id not in existing_players:
        raise Exception("No existing player for cid: " + cid_with_id)

    existing_players[cid_with_id].stats_batter.ovr = new_stats_batter(header_indices=header_indices.batter_header_indices, play_line=play_line)
    existing_players[cid_with_id].stats_pitcher.all = new_stats_pitcher(header_indices=header_indices.pitcher_header_indices, play_line=play_line)

# TODO vl and vr should affect pitcher data too
def read_in_vl_info(header_indices: StatsHeaderIndices, play_line: List[str], existing_players: Dict[str, BaseStatsPlayer]):
    cid_with_id = play_line[header_indices.main_header_indices["cid_index"]] + "_" + play_line[header_indices.main_header_indices["id_index"]]
    if cid_with_id not in existing_players:
        raise Exception("No existing player for cid: " + cid_with_id)

    existing_players[cid_with_id].stats_batter.vl = new_stats_pitcher(header_indices=header_indices.pitcher_header_indices, play_line=play_line)

def read_in_vr_info(header_indices: StatsHeaderIndices, play_line: List[str], existing_players: Dict[str, BaseStatsPlayer]):
    cid_with_id = play_line[header_indices.main_header_indices["cid_index"]] + "_" + play_line[header_indices.main_header_indices["id_index"]]
    if cid_with_id not in existing_players:
        raise Exception("No existing player for cid: " + cid_with_id)

    existing_players[cid_with_id].stats_batter.vr = new_stats_pitcher(header_indices=header_indices.pitcher_header_indices, play_line=play_line)

def read_in_starter_info(header_indices: StatsHeaderIndices, play_line: List[str], existing_players: Dict[str, BaseStatsPlayer]):

    cid_with_id = play_line[header_indices.main_header_indices["cid_index"]] + "_" + play_line[header_indices.main_header_indices["id_index"]]
    if cid_with_id not in existing_players:
        raise Exception("No existing player for cid: " + cid_with_id)

    existing_players[cid_with_id].stats_pitcher.starter = new_stats_pitcher(header_indices=header_indices.pitcher_header_indices, play_line=play_line)

def read_in_reliever_info(header_indices: StatsHeaderIndices, play_line: List[str], existing_players: Dict[str, BaseStatsPlayer]):
    cid_with_id = play_line[header_indices.main_header_indices["cid_index"]] + "_" + play_line[header_indices.main_header_indices["id_index"]]
    if cid_with_id not in existing_players:
        raise Exception("No existing player for cid: " + cid_with_id)

    existing_players[cid_with_id].stats_pitcher.reliever = new_stats_pitcher(header_indices=header_indices.pitcher_header_indices, play_line=play_line)

def read_in_fielder_info(header_indices: StatsHeaderIndices, play_line: List[str], position_number: int, existing_players: Dict[str, BaseStatsPlayer]):
    cid_with_id = play_line[header_indices.main_header_indices["cid_index"]] + "_" + play_line[header_indices.main_header_indices["id_index"]]
    if cid_with_id not in existing_players:
        raise Exception("No existing player for cid: " + cid_with_id)

    existing_players[cid_with_id].stats_fielder[position_number] = new_stats_fielder(header_indices=header_indices.fielding_header_indices, position_number=position_number, play_line=play_line)

def single_line_player_from_base_stats_player(player: BaseStatsPlayer, stats_batter: StatsBatter, stats_pitcher: StatsPitcher, stats_fielder: StatsFielder) -> SingleLineStatsPlayer:
    sl = SingleLineStatsPlayer()
    sl.cid = player.cid
    sl.card_player = player.card_player
    sl.position = player.position
    sl.stats_batter = stats_batter
    sl.stats_pitcher = stats_pitcher
    sl.stats_fielder = stats_fielder

    return sl 
