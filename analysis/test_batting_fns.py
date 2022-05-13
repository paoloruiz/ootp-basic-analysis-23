from typing import Callable, List
from analysis.regression_analysis import RegressionAnalysisModel, perform_bats_handedness_no_hl_regression, perform_bats_handedness_regression, perform_high_low_regression, perform_regression, perform_throws_handedness_no_hl_regression, perform_throws_handedness_regression

from class_model.BaseStatsPlayer import SingleLineStatsPlayer


def get_batter_formula(
    players: List[SingleLineStatsPlayer], 
    get_stat: Callable[[SingleLineStatsPlayer], int],
    ram: RegressionAnalysisModel
) -> Callable[[SingleLineStatsPlayer], float]:
    batting_only = list(filter(lambda player: player.get_fielding_position() == 0, players))
    analysis = perform_regression(batting_only, ram)

    return lambda player: get_stat(player) * analysis.slope + analysis.intercept


def get_batter_bats_no_hl_formula(
    players: List[SingleLineStatsPlayer], 
    get_stat: Callable[[SingleLineStatsPlayer], int],
    ram: RegressionAnalysisModel
) -> Callable[[SingleLineStatsPlayer], float]:
    batting_only = list(filter(lambda player: player.get_fielding_position() == 0, players))
    analysis = perform_bats_handedness_no_hl_regression(batting_only, ram)

    return lambda player: get_stat(player) * analysis[player.card_player.bats].slope + analysis[player.card_player.bats].intercept

def get_batter_hl_formula(
    players: List[SingleLineStatsPlayer], 
    get_stat: Callable[[SingleLineStatsPlayer], int],
    ram: RegressionAnalysisModel
) -> Callable[[SingleLineStatsPlayer], float]:
    batting_only = list(filter(lambda player: player.get_fielding_position() == 0, players))
    analysis = perform_high_low_regression(batting_only, ram)

    return lambda player: get_stat(player) * analysis["high" if get_stat(player) >= 50 else "low"].slope + analysis["high" if get_stat(player) >= 50 else "low"].intercept


def get_batter_bats_hl_formula(
    players: List[SingleLineStatsPlayer], 
    get_stat: Callable[[SingleLineStatsPlayer], int],
    ram: RegressionAnalysisModel
) -> Callable[[SingleLineStatsPlayer], float]:
    batting_only = list(filter(lambda player: player.get_fielding_position() == 0, players))
    analysis = perform_bats_handedness_regression(batting_only, ram)

    def get_player_formula(player: SingleLineStatsPlayer) -> float:
        stat = get_stat(player)
        hl = "high" if stat >= 50 else "low"
        bats = player.card_player.bats
        return stat * analysis[bats][hl].slope + analysis[bats][hl].intercept

    return get_player_formula

def get_pitcher_throws_hl_formula(
    players: List[SingleLineStatsPlayer], 
    get_stat: Callable[[SingleLineStatsPlayer], int],
    ram: RegressionAnalysisModel
) -> Callable[[SingleLineStatsPlayer], float]:
    analysis = perform_throws_handedness_regression(players, ram)

    def get_player_formula(player: SingleLineStatsPlayer) -> float:
        stat = get_stat(player)
        hl = "high" if stat >= 50 else "low"
        throws = player.card_player.throws
        if stat > 100:
            return ((stat * analysis[throws][hl].slope + analysis[throws][hl].intercept) + (100 * analysis[throws][hl].slope + analysis[throws][hl].intercept)) / 2
        return stat * analysis[throws][hl].slope + analysis[throws][hl].intercept

    return get_player_formula

def get_pitcher_throws_no_hl_formula(
    players: List[SingleLineStatsPlayer], 
    get_stat: Callable[[SingleLineStatsPlayer], int],
    ram: RegressionAnalysisModel
) -> Callable[[SingleLineStatsPlayer], float]:
    analysis = perform_throws_handedness_no_hl_regression(players, ram)

    def get_player_formula(player: SingleLineStatsPlayer) -> float:
        stat = get_stat(player)
        throws = player.card_player.throws
        if stat > 100:
            return ((stat * analysis[throws].slope + analysis[throws].intercept) + (100 * analysis[throws].slope + analysis[throws].intercept)) / 2
        return stat * analysis[throws].slope + analysis[throws].intercept

    return get_player_formula