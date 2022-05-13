from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import numpy as np

from class_model.BaseStatsPlayer import SingleLineStatsPlayer


@dataclass
class RegressionAnalysisModel:
    get_x: Callable[[SingleLineStatsPlayer], int]
    get_y_numerator: Callable[[SingleLineStatsPlayer], int]
    get_y_denominator: Callable[[SingleLineStatsPlayer], int]
    min_y_denom: int
    should_use_cooks_distance: bool

@dataclass
class RegressionAnalysis:
    slope: float
    intercept: float
    r_squared: float
    len_x: int

@dataclass
class MultiRegressionAnalysis:
    slope: List[float]
    intercept: float
    r_squared: float

def __get_x_and_y__(
    players: List[SingleLineStatsPlayer],
    ram: RegressionAnalysisModel
) -> Tuple[List[int], List[int]]:
    x_to_y_info: Dict[int, Tuple[int, int]] = {}
    for player in players:
        x = ram.get_x(player)
        if x not in x_to_y_info:
            x_to_y_info[x] = [0, 0]
        y_info = x_to_y_info[x]
        x_to_y_info[x] = [y_info[0] + ram.get_y_numerator(player), y_info[1] + ram.get_y_denominator(player)]
    
    X: List[List[int]] = []
    y: List[int] = []
    for x in x_to_y_info.keys():
        y_info = x_to_y_info[x]
        if y_info[1] >= ram.min_y_denom and y_info[1] > 0:
            X.append([ x ])
            y.append(y_info[0] / y_info[1])
    return (X, y)

def perform_bats_handedness_no_hl_regression(
    players: List[SingleLineStatsPlayer],
    ram: RegressionAnalysisModel
) -> Dict[str, RegressionAnalysis]:
    right_hitters = list(filter(lambda x: x.card_player.bats == "R", players))
    left_hitters = list(filter(lambda x: x.card_player.bats == "L", players))
    switch_hitters = list(filter(lambda x: x.card_player.bats == "S", players))
    
    return {
        "R": perform_regression(right_hitters, ram),
        "L": perform_regression(left_hitters, ram),
        "S": perform_regression(switch_hitters, ram)
    }

def perform_bats_handedness_regression(
    players: List[SingleLineStatsPlayer],
    ram: RegressionAnalysisModel
) -> Dict[str, Dict[str, RegressionAnalysis]]:
    right_hitters = list(filter(lambda x: x.card_player.bats == "R", players))
    left_hitters = list(filter(lambda x: x.card_player.bats == "L", players))
    switch_hitters = list(filter(lambda x: x.card_player.bats == "S", players))
    
    return {
        "R": perform_high_low_regression(right_hitters, ram),
        "L": perform_high_low_regression(left_hitters, ram),
        # Just not enough switch hitters to split along high/low
        "S": perform_regression(switch_hitters, ram)
    }

def perform_throws_handedness_no_hl_regression(
    players: List[SingleLineStatsPlayer],
    ram: RegressionAnalysisModel
) -> Dict[str, RegressionAnalysis]:
    right_throwers = list(filter(lambda x: x.card_player.throws == "R", players))
    left_throwers = list(filter(lambda x: x.card_player.throws == "L", players))
    
    return {
        "R": perform_regression(right_throwers, ram),
        "L": perform_regression(left_throwers, ram)
    }

def perform_throws_handedness_regression(
    players: List[SingleLineStatsPlayer],
    ram: RegressionAnalysisModel
) -> Dict[str, Dict[str, RegressionAnalysis]]:
    right_throwers = list(filter(lambda x: x.card_player.throws == "R", players))
    left_throwers = list(filter(lambda x: x.card_player.throws == "L", players))
    
    return {
        "R": perform_high_low_regression(right_throwers, ram),
        "L": perform_high_low_regression(left_throwers, ram)
    }

def perform_high_low_regression(
    players: List[SingleLineStatsPlayer],
    ram: RegressionAnalysisModel
) -> Dict[str, RegressionAnalysis]:
    high_throwers = list(filter(lambda player: ram.get_x(player) >= 50, players))
    low_throwers = list(filter(lambda player: ram.get_x(player) < 50, players))
    
    return {
        "high": perform_regression(high_throwers, ram),
        "low": perform_regression(low_throwers, ram)
    }

def perform_regression(
    players: List[SingleLineStatsPlayer],
    ram: RegressionAnalysisModel
) -> RegressionAnalysis:
    x, y = __get_x_and_y__(players, ram)

    shouldPlot = False
    for player in players:
        if player.cid == "40055" and ram.get_x(player) == 94:
            shouldPlot = True

    results = sm.OLS(y, sm.add_constant(x)).fit()

    if shouldPlot and False:
        plt.scatter(x, y)
        z = np.linspace(0, 110, num=110)
        plt.plot(z, results.params[1] * z + results.params[0])
        plt.show()
    
    if ram.should_use_cooks_distance and len(x) > 2:
        x_2 = []
        y_2 = []

        cooks_distance = results.get_influence().cooks_distance[0]
        cutoff = 4.0 / (len(x) - 2)
        for i in range(len(x)):
            if cooks_distance[i] < cutoff:
                x_2.append(x[i])
                y_2.append(y[i])
        
        x = x_2
        y = y_2
        if len(x) > 2 and len(y) > 2:
            results = sm.OLS(y, sm.add_constant(x)).fit()

    return RegressionAnalysis(slope=results.params[1], intercept=results.params[0], r_squared=results.rsquared, len_x=len(x))


def perform_multi_regression(
    x: List[List[int]],
    y: List[int]
) -> MultiRegressionAnalysis:
    model = sm.OLS(y, sm.add_constant(x))
    results = model.fit()
    
    x_real = []
    y_real = []

    cooks_distance = results.get_influence().cooks_distance[0]
    cutoff = 4.0 / (len(x) - 2)
    for i in range(len(x)):
        if cooks_distance[i] < cutoff:
            x_real.append(x[i])
            y_real.append(y[i])
    model = sm.OLS(y, sm.add_constant(x))
    results = model.fit()

    return MultiRegressionAnalysis(slope=results.params[1:], intercept=results.params[0], r_squared=results.rsquared)
