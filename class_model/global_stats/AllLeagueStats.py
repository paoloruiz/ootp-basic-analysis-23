from dataclasses import dataclass, field
from typing import Dict

from class_model.BaseStatsPlayer import BaseStatsPlayer
from util.ip_math import add_ip, ip_to_ip_w_remainder


@dataclass
class LeagueStats:
    tot_runs_scored: float = 0.0
    tot_ip: float = 0.0
    total_bf: int = 0

    def get_runs_per_win(self) -> float:
        return 9 * (self.tot_runs_scored / ip_to_ip_w_remainder(self.tot_ip)) * 1.5 + 3

    def get_runs_per_out():
        pass

    def get_replacement_level_runs_per_pa(self) -> float:
        rpw_per_bf = self.get_runs_per_win() / self.total_bf
        adj_games = round(self.tot_ip / 9.0)
        return 570 * (adj_games / 2430.0) * rpw_per_bf

    def capture_player_data(self, player: BaseStatsPlayer):
        if player.stats_pitcher.all == None:
            return

        self.tot_runs_scored += player.stats_pitcher.all.pitcher_runs_against
        self.tot_ip = add_ip(player.stats_pitcher.all.pitcher_ip, self.tot_ip)
        self.total_bf += player.stats_pitcher.all.pitcher_bf

@dataclass
class AllLeagueStats:
    league_stats: Dict[str, LeagueStats] = field(default_factory=dict)

    def capture_player_data(self, league: str, player: BaseStatsPlayer):
        if league not in self.league_stats:
            self.league_stats[league] = LeagueStats()
        self.league_stats[league].capture_player_data(player)