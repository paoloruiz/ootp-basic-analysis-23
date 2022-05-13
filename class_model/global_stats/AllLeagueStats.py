from dataclasses import dataclass, field
from typing import Dict

from class_model.BaseStatsPlayer import BaseStatsPlayer
from util.ip_math import add_ip, ip_to_ip_w_remainder


@dataclass
class LeagueStats:
    tot_runs_scored: float = 0.0
    tot_ip: float = 0.0
    total_bf: int = 0

    total_left_handed_batter_pa: float = 0
    total_right_handed_batter_pa: float = 0
    total_switch_handed_batter_pa: float = 0

    total_left_handed_pitcher_bf: int = 0
    total_right_handed_pitcher_bf: int = 0

    def get_runs_per_win(self) -> float:
        return 9 * (self.tot_runs_scored / ip_to_ip_w_remainder(self.tot_ip)) * 1.5 + 3

    def get_replacement_level_runs_per_pa(self) -> float:
        rpw_per_bf = self.get_runs_per_win() / self.total_bf
        adj_games = round(self.tot_ip / 9.0)
        return 570 * (adj_games / 2430.0) * rpw_per_bf

    def get_left_pitcher_pct(self) -> float:
        lhp_bf = self.total_left_handed_pitcher_bf
        rhp_bf = self.total_right_handed_pitcher_bf

        return lhp_bf / float(lhp_bf + rhp_bf)

    def get_left_batter_pct(self) -> float:
        left_pitch_pct = self.get_left_pitcher_pct()

        lhb_pa = self.total_left_handed_batter_pa
        rhb_pa = self.total_right_handed_batter_pa
        shb_pa = self.total_switch_handed_batter_pa

        return (lhb_pa + (1.0 - left_pitch_pct) * shb_pa) / (lhb_pa + rhb_pa + shb_pa)

    def capture_player_data(self, player: BaseStatsPlayer):
        if player.stats_batter.ovr != None:
            if player.card_player.bats == "R":
                self.total_right_handed_batter_pa += player.stats_batter.ovr.batter_pa
            elif player.card_player.bats == "L":
                self.total_left_handed_batter_pa += player.stats_batter.ovr.batter_pa
            else:
                self.total_switch_handed_batter_pa += player.stats_batter.ovr.batter_pa

        if player.stats_pitcher.all == None:
            return

        self.tot_runs_scored += player.stats_pitcher.all.pitcher_runs_against
        self.tot_ip = add_ip(player.stats_pitcher.all.pitcher_ip, self.tot_ip)
        self.total_bf += player.stats_pitcher.all.pitcher_bf

        if player.card_player.throws == "R":
            self.total_right_handed_pitcher_bf += player.stats_pitcher.all.pitcher_bf
        else:
            self.total_left_handed_pitcher_bf += player.stats_pitcher.all.pitcher_bf

@dataclass
class AllLeagueStats:
    league_stats: Dict[str, LeagueStats] = field(default_factory=dict)

    def capture_player_data(self, league: str, player: BaseStatsPlayer):
        if league not in self.league_stats:
            self.league_stats[league] = LeagueStats()
        self.league_stats[league].capture_player_data(player)