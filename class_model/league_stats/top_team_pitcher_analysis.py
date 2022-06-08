from dataclasses import dataclass
import math
from typing import List, Tuple
from class_model.league_stats.league_stats import IndividualLeague, Team
from class_model.league_stats.top_team_stats_analysis import MY_TEAM_NAMES, TOP_PCT

@dataclass
class PitcherBreakdown:
    sp_lefty_pct: float
    rp_lefty_pct: float

def __can_analyze_league__(league: IndividualLeague) -> bool:
    teams = league.get_valid_teams()
    if len(teams) < 0.9 * league.num_teams:
        return False

    return True

def __identify_starting_pitchers__(team: Team):
    pitchers = team.get_starting_list()[1]

    sorted_pitcher = sorted(pitchers, key=lambda pl: pl.stats_pitcher.pitcher_pitches_per_game, reverse=True)
    starting_pitchers = list(filter(lambda pi: pi.stats_pitcher.pitcher_pitches_per_game > 50, pitchers))
    if len(starting_pitchers) > 6:
        starting_pitchers = sorted_pitcher[0:6]
    
    if len(starting_pitchers) < 4:
        starting_pitchers = sorted_pitcher[0:4]
        
    relievers = sorted_pitcher[len(starting_pitchers):]

    sp_lefty_count = sum(map(lambda pi: 1 if pi.card_player.throws == "L" else 0, starting_pitchers))
    rp_lefty_count = sum(map(lambda pi: 1 if pi.card_player.throws == "L" else 0, relievers))

    return PitcherBreakdown(
        sp_lefty_pct=float(sp_lefty_count) / len(starting_pitchers),
        rp_lefty_pct=float(rp_lefty_count) / len(relievers)
    )


def analyze_league_pitching(leagues: List[IndividualLeague]) -> Tuple[float, float, float]:
    valid_leagues = list(filter(lambda lg: __can_analyze_league__(lg), leagues))

    sp_lefty_pcts = []
    rp_lefty_pcts = []
    rp_lefty_pct_when_high_lefty = []

    for lg in valid_leagues:
        teams = lg.get_valid_teams()
        
        sorted_gs_teams = sorted(teams, key=lambda tm: tm.get_tot_gs(), reverse=True)
        top_teams = sorted_gs_teams[0:math.floor(TOP_PCT * len(sorted_gs_teams))]

        for tm in top_teams:
            # Ignore my own teams
            if tm.name in MY_TEAM_NAMES:
                continue

            p_analysis = __identify_starting_pitchers__(tm)
            sp_lefty_pcts.append(p_analysis.sp_lefty_pct)
            rp_lefty_pcts.append(p_analysis.rp_lefty_pct)

            if p_analysis.sp_lefty_pct >= 0.8:
                rp_lefty_pct_when_high_lefty.append(p_analysis.rp_lefty_pct)

    print("sp_left%", sum(sp_lefty_pcts) / len(sp_lefty_pcts))
    print("rp_left%", sum(rp_lefty_pcts) / len(rp_lefty_pcts))
    print("rp_left% when high lefty", sum(rp_lefty_pct_when_high_lefty) / len(rp_lefty_pct_when_high_lefty) if len(rp_lefty_pct_when_high_lefty) > 0 else -1)
