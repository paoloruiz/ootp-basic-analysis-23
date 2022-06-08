from dataclasses import dataclass, field
import math
from typing import Dict, List, Tuple

from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer
from class_model.league_stats.platoon_splits import PlatoonSplits, get_batter_v_pitcher_starts, get_non_platoon_starts, get_platoon_starts
from class_model.stats_player.filter_cards import flatten_player_ovr

def __get_field_gs__(player: SingleLineStatsPlayer) -> int:
    return player.stats_fielder.fielding_games_started if player.get_fielding_position() > 0 else player.special_mod_bat_gs


def __is_platoon__(players: List[SingleLineStatsPlayer], is_catcher: bool) -> Tuple[str, Tuple[int, int, int, int], Tuple[int, int, int, int]]:
    if len(players) == 1:
        return False

    tot_gs = sum(map(lambda player: __get_field_gs__(player), players))

    if __get_field_gs__(players[0]) / tot_gs > 0.8 or (is_catcher and float(__get_field_gs__(players[0])) / tot_gs > 0.75):
        return False

    if len(players) == 2:
        return True

    possible_platoon_starts = __get_field_gs__(players[0]) + __get_field_gs__(players[1])

    extra_backup_starts = sum(map(lambda player: __get_field_gs__(player), players[2:]))

    return float(possible_platoon_starts) / (possible_platoon_starts + extra_backup_starts) > 0.9


@dataclass
class Team:
    name: str
    players: List[BaseStatsPlayer] = field(default_factory=list)

    def add_player(self, player: BaseStatsPlayer):
        self.players.append(player)

    def is_valid_and_has_data(self):
        if len(self.players) > 26 or len(self.players) < 22:
            return False

        fielding_positions = set()
        gs = 0
        for player in self.players:
            if player.stats_fielder != None:
                for pos in player.stats_fielder.keys():
                    fielding_positions.add(pos)
            if player.stats_pitcher != None:
                gs += player.stats_pitcher.all.pitcher_games_start

        return gs > 0 and len(fielding_positions) == 8

    def get_tot_gs(self):
        gs = 0
        for player in self.players:
            if player.stats_pitcher != None:
                gs += player.stats_pitcher.all.pitcher_games_start
        return gs

    def get_starting_list(self) -> Dict[int, List[SingleLineStatsPlayer]]:
        flattened_players: List[SingleLineStatsPlayer] = []
        for player in self.players:
            flattened_players.extend(flatten_player_ovr(player))
        positions = {
            0: [],
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
            8: [],
            9: [],
        }

        for player in flattened_players:
            if player.get_fielding_position() >= 2:
                positions[player.get_fielding_position()].append(player)
            else:
                # Either pitcher and/or DH
                if player.stats_pitcher.pitcher_bf > 0:
                    positions[1].append(player)
                if player.stats_batter.batter_pa > 0:
                    positions[0].append(player)

        for position in positions:
            positions[position].sort(key=lambda p: __get_field_gs__(p), reverse=True)

        return positions

@dataclass
class IndividualLeague:
    num_teams: int
    name: str

    teams: Dict[str, Team] = field(default_factory=dict)

    def record_players(self, players: Dict[str, BaseStatsPlayer]):
        for player in players.values():
            if player.team not in self.teams:
                self.teams[player.team] = Team(name=player.team)
            
            self.teams[player.team].add_player(player)

    def get_valid_teams(self):
        t: List[Team] = []

        for team in self.teams.values():
            if team.is_valid_and_has_data():
                t.append(team)
        
        return t

    def get_all_teams(self):
        t: List[Team] = []

        for team in self.teams.values():
            t.append(team)
        
        return t

positions_to_check = [0, 2, 3, 4, 5, 6, 7, 8, 9]

@dataclass
class IndividualLeagueStats:
    ils_d: Dict[str, List[IndividualLeague]] = field(default_factory=dict)

    def record(self, tourney_type: str, num_teams: int, players: Dict[str, BaseStatsPlayer], lg_nm: str = None):
        if tourney_type not in self.ils_d:
            self.ils_d[tourney_type] = []

        new_league = IndividualLeague(num_teams=num_teams, name=lg_nm)
        new_league.record_players(players=players)

        self.ils_d[tourney_type].append(new_league)

    def get_platoon_splits(self, tourney_type: str, ignore_validity: bool = False) -> PlatoonSplits:
        if tourney_type not in self.ils_d:
            raise Exception(tourney_type + " is not a valid tourney type of: " + ", ".join(self.ils_d.keys()))
        
        platoon_splits = PlatoonSplits()
        for league in self.ils_d[tourney_type]:
            valid_teams = league.get_valid_teams() if not ignore_validity else league.get_all_teams()
            sorted_valid_teams = sorted(valid_teams, key=lambda tm: tm.get_tot_gs(), reverse=True)
            teams_to_look_at = sorted_valid_teams[0:math.floor(len(sorted_valid_teams) / 4)]
            for team in teams_to_look_at:
                player_list = team.get_starting_list()
                for pos_num in positions_to_check:
                    position_group = sorted(player_list[pos_num], key=lambda player: __get_field_gs__(player), reverse=True)

                    if __is_platoon__(position_group, pos_num == 2):
                        plat_1 = position_group[0]
                        plat_2 = position_group[1]
                        platoon_splits.count_bvp_starts(get_batter_v_pitcher_starts(plat_1))
                        platoon_splits.count_bvp_starts(get_batter_v_pitcher_starts(plat_2))
                        vl = None
                        vr = None
                        if plat_1.card_player.bats == "R" and plat_2.card_player.bats == "L":
                            vl = plat_1
                            vr = plat_2
                        elif plat_1.card_player.bats == "R" and plat_2.card_player.bats == "S":
                            vl = plat_1
                            vr = plat_2
                        elif plat_1.card_player.bats == "L" and plat_2.card_player.bats == "R":
                            vl = plat_2
                            vr = plat_1
                        elif plat_1.card_player.bats == "L" and plat_2.card_player.bats == "S":
                            vl = plat_2
                            vr = plat_1
                        elif plat_1.card_player.bats == "S" and plat_2.card_player.bats == "R":
                            vl = plat_2
                            vr = plat_1
                        elif plat_1.card_player.bats == "S" and plat_2.card_player.bats == "L":
                            vl = plat_1
                            vr = plat_2
                        
                        if vl == None:
                            continue

                        platoon_splits.count_platoon_starts(get_platoon_starts("vL", vl))
                        platoon_splits.count_platoon_starts(get_platoon_starts("vR", vr))
                    else:
                        platoon_splits.count_bvp_starts(get_batter_v_pitcher_starts(position_group[0]))
                        starter = position_group[0]
                        backups = position_group[1:]
                        platoon_splits.count_non_platoon_starts(get_non_platoon_starts("starter", starter))
                        for backup in backups:
                            platoon_splits.count_non_platoon_starts(get_non_platoon_starts("backup", backup))

        return platoon_splits
