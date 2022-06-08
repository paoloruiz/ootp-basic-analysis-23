from dataclasses import dataclass, field, fields
import math
import numpy as np
from typing import Callable, Dict, List, Tuple
from class_model.league_stats.league_stats import IndividualLeague, Team
from output_utils.csvwriter import CsvWriter
from util.ip_math import add_ip, ip_to_ip_w_remainder

MY_TEAM_NAMES = ["Tokyo_TR", "Tokyo_", "Nowhere_", "Nowhere_NOW"]
TOP_PCT = 2/32

def __can_analyze_league__(league: IndividualLeague) -> bool:
    teams = league.get_valid_teams()
    if len(teams) < 0.9 * league.num_teams:
        return False
    
    pitchers = teams[0].get_starting_list()[1]
    if sum(map(lambda pi: pi.stats_pitcher.pitcher_wins + pi.stats_pitcher.pitcher_losses, pitchers)) == 0:
        return False

    return True

def __get_tot_games__(team: Team):
    return sum(map(lambda pi: pi.stats_pitcher.pitcher_games_start, team.get_starting_list()[1]))

@dataclass
class TeamTotalStats:
    games: int = 0
    off_pa: int = 0

    off_runs: int = 0
    off_singles: int = 0
    off_doubles: int = 0
    off_triples: int = 0
    off_homeruns: int = 0
    off_bb: int = 0
    off_hbp: int = 0
    off_sb: int = 0
    off_cs: int = 0
    off_k: int = 0
    off_sf: int = 0

    zr: float = 0
    frame_runs: float = 0
    cabi: float = 0
    arm_runs: float = 0

    def_bf: int = 0

    def_runs: int = 0
    def_k: int = 0
    def_bb: int = 0
    def_hbp: int = 0
    def_hr: int = 0
    def_non_hr_hits: int = 0
    def_sb: int = 0
    def_cs: int = 0

    def get_off_babip(self):
        return (self.off_singles + self.off_doubles + self.off_triples) / (self.off_pa - self.off_bb - self.off_hbp - self.off_k - self.off_homeruns - self.off_sf)

    def get_def_babip(self):
        return (self.def_non_hr_hits) / (self.def_bf - self.def_bb - self.def_hbp - self.def_k - self.def_hr)

@dataclass
class LeagueStat:
    num_teams: int
    stats: List[float] = field(default_factory=list)
    is_negative: bool = False

    def record_stat(self, stat: float):
        self.stats.append(stat)

    def rank(self, stat: float) -> float:
        self.stats.sort(reverse=not self.is_negative)
        return self.stats.index(stat) / self.num_teams * 32

    def z_score(self, stat: float) -> float:
        avg = sum(self.stats) / len(self.stats)
        std_dev = np.std(self.stats)

        return (stat - avg) / std_dev


@dataclass
class LeagueStats:
    off_runs: LeagueStat
    off_singles: LeagueStat
    off_doubles: LeagueStat
    off_triples: LeagueStat
    off_homeruns: LeagueStat
    off_babip: LeagueStat
    off_bb: LeagueStat
    off_hbp: LeagueStat
    off_sb: LeagueStat
    off_cs: LeagueStat
    off_k: LeagueStat

    zr: LeagueStat
    frame_runs: LeagueStat
    cabi: LeagueStat
    arm_runs: LeagueStat

    def_runs: LeagueStat
    def_k: LeagueStat
    def_bb: LeagueStat
    def_hbp: LeagueStat
    def_hr: LeagueStat
    def_babip: LeagueStat
    def_sb: LeagueStat
    def_cs: LeagueStat

    def record(self, team_stats: TeamTotalStats):
        self.off_runs.record_stat(team_stats.off_runs)
        self.off_singles.record_stat(team_stats.off_singles)
        self.off_doubles.record_stat(team_stats.off_doubles)
        self.off_triples.record_stat(team_stats.off_triples)
        self.off_homeruns.record_stat(team_stats.off_homeruns)
        self.off_babip.record_stat(team_stats.get_off_babip())
        self.off_bb.record_stat(team_stats.off_bb)
        self.off_hbp.record_stat(team_stats.off_hbp)
        self.off_sb.record_stat(team_stats.off_sb)
        self.off_cs.record_stat(team_stats.off_cs)
        self.off_k.record_stat(team_stats.off_k)
        self.zr.record_stat(team_stats.zr)
        self.frame_runs.record_stat(team_stats.frame_runs)
        self.arm_runs.record_stat(team_stats.arm_runs)
        self.cabi.record_stat(team_stats.cabi)
        self.def_runs.record_stat(team_stats.def_runs)
        self.def_k.record_stat(team_stats.def_k)
        self.def_bb.record_stat(team_stats.def_bb)
        self.def_hbp.record_stat(team_stats.def_hbp)
        self.def_hr.record_stat(team_stats.def_hr)
        self.def_babip.record_stat(team_stats.get_def_babip())
        self.def_sb.record_stat(team_stats.def_sb)
        self.def_cs.record_stat(team_stats.def_cs)

def __new_league_stats__(num_teams: int) -> LeagueStats:
    return LeagueStats(
        off_runs=LeagueStat(num_teams=num_teams),
        off_singles=LeagueStat(num_teams=num_teams),
        off_doubles=LeagueStat(num_teams=num_teams),
        off_triples=LeagueStat(num_teams=num_teams),
        off_homeruns=LeagueStat(num_teams=num_teams),
        off_babip=LeagueStat(num_teams=num_teams),
        off_bb=LeagueStat(num_teams=num_teams),
        off_hbp=LeagueStat(num_teams=num_teams),
        off_sb=LeagueStat(num_teams=num_teams),
        off_cs=LeagueStat(num_teams=num_teams),
        off_k=LeagueStat(num_teams=num_teams, is_negative=True),

        zr=LeagueStat(num_teams=num_teams),
        frame_runs=LeagueStat(num_teams=num_teams),
        cabi=LeagueStat(num_teams=num_teams),
        arm_runs=LeagueStat(num_teams=num_teams),

        def_runs=LeagueStat(num_teams=num_teams, is_negative=True),
        def_k=LeagueStat(num_teams=num_teams),
        def_bb=LeagueStat(num_teams=num_teams, is_negative=True),
        def_hbp=LeagueStat(num_teams=num_teams, is_negative=True),
        def_hr=LeagueStat(num_teams=num_teams, is_negative=True),
        def_babip=LeagueStat(num_teams=num_teams, is_negative=True),
        def_sb=LeagueStat(num_teams=num_teams, is_negative=True),
        def_cs=LeagueStat(num_teams=num_teams)
    )


def __team_total_stats__(team: Team) -> TeamTotalStats:
    players = team.players

    tot_ip = 0.0
    for pitcher in team.get_starting_list()[1]:
        tot_ip = add_ip(tot_ip, pitcher.stats_pitcher.pitcher_ip)
    team_stats = TeamTotalStats()
    for player in players:
        if player.stats_batter != None:
            team_stats.off_pa += player.stats_batter.ovr.batter_pa
            team_stats.off_runs += player.stats_batter.ovr.batter_runs_scored
            team_stats.off_singles += player.stats_batter.ovr.batter_singles
            team_stats.off_doubles += player.stats_batter.ovr.batter_doubles
            team_stats.off_triples += player.stats_batter.ovr.batter_triples
            team_stats.off_homeruns += player.stats_batter.ovr.batter_homeruns
            team_stats.off_bb += player.stats_batter.ovr.batter_walks
            team_stats.off_hbp += player.stats_batter.ovr.batter_hit_by_pitch
            team_stats.off_sb += player.stats_batter.ovr.batter_stolen_bases
            team_stats.off_cs += player.stats_batter.ovr.batter_caught_stealing
            team_stats.off_k += player.stats_batter.ovr.batter_strikeouts
            team_stats.off_sf += player.stats_batter.ovr.batter_sac_flies

        if len(player.stats_fielder.keys()) > 0:
            for sf in player.stats_fielder.values():
                team_stats.zr += sf.fielding_zr
                team_stats.frame_runs += sf.fielding_framing_runs
                if sf.fielding_position == 2:
                    team_stats.cabi += player.card_player.cabi * ip_to_ip_w_remainder(sf.fielding_ip) / ip_to_ip_w_remainder(tot_ip)
                team_stats.arm_runs += sf.fielding_arm_runs

        if player.stats_pitcher != None:
            team_stats.games += player.stats_pitcher.all.pitcher_games_start
            team_stats.def_bf += player.stats_pitcher.all.pitcher_bf
            team_stats.def_runs += player.stats_pitcher.all.pitcher_runs_against
            team_stats.def_k += player.stats_pitcher.all.pitcher_strikeouts
            team_stats.def_bb += player.stats_pitcher.all.pitcher_walks
            team_stats.def_hbp += player.stats_pitcher.all.pitcher_hit_by_pitch
            team_stats.def_hr += player.stats_pitcher.all.pitcher_homeruns
            team_stats.def_non_hr_hits += player.stats_pitcher.all.pitcher_singles + player.stats_pitcher.all.pitcher_doubles + player.stats_pitcher.all.pitcher_triples
            team_stats.def_sb += player.stats_pitcher.all.pitcher_stolen_bases
            team_stats.def_cs += player.stats_pitcher.all.pitcher_caught_stealing
    return team_stats

def __top_team_ranks_plus_my_team__(league: IndividualLeague) -> Tuple[List[TeamTotalStats], TeamTotalStats, LeagueStats]:
    teams = league.get_valid_teams()

    my_teams = list(filter(lambda tm: tm.name in MY_TEAM_NAMES, teams))

    my_team = None
    if len(my_teams) == 1:
        my_team = __team_total_stats__(my_teams[0])

    teams_by_wins = sorted(teams, key=lambda team: sum(map(lambda pi: pi.stats_pitcher.pitcher_wins, team.get_starting_list()[1])), reverse=True)

    team_stats_by_wins = list(map(lambda team: __team_total_stats__(team), teams_by_wins))

    top_teams = team_stats_by_wins[0:math.floor(league.num_teams * TOP_PCT)]

    league_stats = __new_league_stats__(num_teams=len(teams_by_wins))

    for tm in team_stats_by_wins:
        league_stats.record(tm)

    return (top_teams, my_team, league_stats)

@dataclass
class AnalyzedStat:
    name: str
    get_stat: Callable[[TeamTotalStats], float]
    rk: List[float] = field(default_factory=list)
    my_tm_rk: List[float] = field(default_factory=list)
    z_score: List[float] = field(default_factory=list)
    my_tm_z_score: List[float] = field(default_factory=list)

    def record_team(self, tm: TeamTotalStats, league_stats: LeagueStats):
        self.rk.append(getattr(league_stats, self.name).rank(self.get_stat(tm)))
        self.z_score.append(getattr(league_stats, self.name).z_score(self.get_stat(tm)))

    def record_my_team(self, tm: TeamTotalStats, league_stats: LeagueStats):
        self.my_tm_rk.append(getattr(league_stats, self.name).rank(self.get_stat(tm)))
        self.my_tm_z_score.append(getattr(league_stats, self.name).z_score(self.get_stat(tm)))

    def to_arr(self):
        return [self.name, np.average(self.rk), np.std(self.rk), "", np.average(self.my_tm_rk), np.std(self.my_tm_rk), "", "", np.average(self.z_score), np.std(self.z_score), "", np.average(self.my_tm_z_score), np.std(self.my_tm_z_score)]


def analyze_leagues(leagues: List[IndividualLeague], csv_writer: CsvWriter):
    stat_to_analysis: Dict[str, AnalyzedStat] = {}

    def get_stat_fn(fld: str) -> Callable[[TeamTotalStats], float]:
        if fld == "off_babip":
            return lambda tts: tts.get_off_babip()

        if fld == "def_babip":
            return lambda tts: tts.get_def_babip()

        return lambda tts: getattr(tts, fld)

    for fld in fields(LeagueStats):
        stat_to_analysis[fld] = AnalyzedStat(name=fld.name, get_stat=get_stat_fn(fld.name))

    valid_leagues = list(filter(lambda lg: __can_analyze_league__(lg), leagues))
    for league in valid_leagues:
        top_teams, my_team, league_stats = __top_team_ranks_plus_my_team__(league)

        if my_team == None:
            raise Exception(league.name + " contains no scipper team detectable")

        for fld in fields(LeagueStats):
            for team in top_teams:
                stat_to_analysis[fld].record_team(team, league_stats)
            stat_to_analysis[fld].record_my_team(my_team, league_stats)

    csv_writer.record(["Rank Type", "avg. rank top teams", "std. dev", "", "avg. rank my team", "std. dev", "", "", "avg. z_score top teams", "std. dev", "", "avg z score my team", "std. dev"])
    for analysis in stat_to_analysis.values():
        csv_writer.record(analysis.to_arr())