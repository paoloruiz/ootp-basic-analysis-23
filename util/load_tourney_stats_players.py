import os
from typing import Dict, List
from class_model.BaseCardPlayer import BaseCardPlayer
from class_model.BaseStatsPlayer import BaseStatsPlayer
from class_model.global_stats.AllLeagueStats import AllLeagueStats
from class_model.global_stats.PitcherStats import PitcherStats
from class_model.league_stats.league_stats import IndividualLeagueStats
from output_utils.progress.progress_bar import ProgressBar
from class_model.load_players import load_stats_players

def load_tourney_stats_players_flat(
    base_card_players: Dict[str, BaseCardPlayer],
    all_league_stats: AllLeagueStats,
    all_pitcher_stats: PitcherStats,
    individual_league_stats: IndividualLeagueStats,
    ttype: str
) -> Dict[str, List[Dict[str, BaseStatsPlayer]]]:
    tourney_files = os.listdir('data/tournament/')

    tourney_types: Dict[str, List[Dict[str, BaseStatsPlayer]]] = {}

    progress_bar = ProgressBar(len(tourney_files), "Reading tourney files")
    for tourney in tourney_files:
        tourney_type = tourney.split('_')[0][1:]
        if ttype != None and tourney_type != ttype:
            continue
        num_teams = int(tourney.split('_')[1])

        if tourney_type not in tourney_types:
            tourney_types[tourney_type] = []

        stats_players = load_stats_players('data/tournament/' + tourney, tourney_type, base_card_players, all_league_stats, all_pitcher_stats)

        individual_league_stats.record(tourney_type=tourney_type, num_teams=num_teams, players=stats_players, lg_nm=tourney)

        tourney_types[tourney_type].append(stats_players)
        progress_bar.increment()
    progress_bar.finish()

    return tourney_types

def load_league_stats_players_flat(
    base_card_players: Dict[str, BaseCardPlayer],
    all_league_stats: AllLeagueStats,
    all_pitcher_stats: PitcherStats,
    individual_league_stats: IndividualLeagueStats
) -> List[Dict[str, BaseStatsPlayer]]:
    league_files = os.listdir('data/league/')

    leagues: List[Dict[str, BaseStatsPlayer]] = []

    progress_bar = ProgressBar(len(league_files), "Reading leauge files")
    for league in league_files:

        stats_players = load_stats_players('data/league/' + league, "lg", base_card_players, all_league_stats, all_pitcher_stats)

        individual_league_stats.record(tourney_type="lg", num_teams=30, players=stats_players, lg_nm=league)

        leagues.append(stats_players)
        progress_bar.increment()
    progress_bar.finish()

    return leagues

def load_tourney_stats_players_by_tourney(base_card_players: Dict[str, BaseCardPlayer], all_league_stats: AllLeagueStats, all_pitcher_stats: PitcherStats) -> Dict[str, Dict[str, List[Dict[str, BaseStatsPlayer]]]]:
    tourney_files = os.listdir('data/tournament/')

    # openiron -> 32_147 -> cid -> player
    tourney_types: Dict[str, Dict[str, Dict[str, BaseStatsPlayer]]] = {}

    progress_bar = ProgressBar(len(tourney_files), "Reading tourney files")
    for tourney in tourney_files:
        tourney_type = tourney.split('_')[0][1:]

        if tourney_type not in tourney_types:
            tourney_types[tourney_type] = {}

        tourney_id = tourney[len(tourney_type) + 2:]
        tourney_types[tourney_type][tourney_id] = []

        stats_players = load_stats_players('data/tournament/' + tourney, tourney_type, base_card_players, all_league_stats, all_pitcher_stats)

        tourney_types[tourney_type][tourney_id] = stats_players
        progress_bar.increment()
    progress_bar.finish()

    return tourney_types