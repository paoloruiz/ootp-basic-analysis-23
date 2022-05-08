from typing import Dict
import copy
from class_model.BaseStatsPlayer import BaseStatsPlayer, SingleLineStatsPlayer, TotalStatsBatter, TotalStatsPitcher
from class_model.stats_player.batter import merge_stats_batter
from class_model.stats_player.fielder import StatsFielder, merge_stats_fielder
from class_model.stats_player.pitcher import merge_stats_pitchers


def __merge_total_stats_batter__(a: TotalStatsBatter, b: TotalStatsBatter) -> TotalStatsBatter:
    c = TotalStatsBatter()

    if a.ovr != None and b.ovr != None:
        c.ovr = merge_stats_batter(a.ovr, b.ovr)
    elif a.ovr != None:
        c.ovr = copy.deepcopy(a.ovr)
    elif b.ovr != None:
        c.ovr = copy.deepcopy(b.ovr)

    if a.vl != None and b.vl != None:
        c.vl = merge_stats_batter(a.vl, b.vl)
    elif a.vl != None:
        c.vl = copy.deepcopy(a.vl)
    elif b.vl != None:
        c.vl = copy.deepcopy(b.vl)

    if a.vr != None and b.vr != None:
        c.vr = merge_stats_batter(a.vr, b.vr)
    elif a.vr != None:
        c.vr = copy.deepcopy(a.vr)
    elif b.vr != None:
        c.vr = copy.deepcopy(b.vr)

    return c

def __merge_stats_pitchers__(a: TotalStatsPitcher, b: TotalStatsPitcher) -> TotalStatsPitcher:
    c: TotalStatsPitcher = TotalStatsPitcher()

    if a.all != None and b.all != None:
        c.all = merge_stats_pitchers(a.all, b.all)
    elif a.all != None:
        c.all = copy.deepcopy(a.all)
    elif b.ovr != None:
        c.all = copy.deepcopy(b.all)

    if a.starter != None and b.starter != None:
        c.starter = merge_stats_pitchers(a.starter, b.starter)
    elif a.starter != None:
        c.starter = copy.deepcopy(a.starter)
    elif b.starter != None:
        c.starter = copy.deepcopy(b.starter)

    if a.reliever != None and b.reliever != None:
        c.reliever = merge_stats_pitchers(a.reliever, b.reliever)
    elif a.reliever != None:
        c.reliever = copy.deepcopy(a.reliever)
    elif b.reliever != None:
        c.reliever = copy.deepcopy(b.reliever)

    return c

def __merge_stats_fielders__(a: Dict[int, StatsFielder], b: Dict[int, StatsFielder]) -> Dict[int, StatsFielder]:
    c: Dict[int, StatsFielder] = {}

    for pos_num in a.keys():
        if pos_num in b:
            c[pos_num] = merge_stats_fielder(a[pos_num], b[pos_num])
        else:
            c[pos_num] = copy.deepcopy(a[pos_num])

    for pos_num in b.keys():
        if pos_num not in c:
            c[pos_num] = copy.deepcopy(b[pos_num])

    return c

def merge_base_stats_players(a: BaseStatsPlayer, b: BaseStatsPlayer):
    c = BaseStatsPlayer()
    c.cid = a.cid
    c.cid_with_id = a.cid + "_"
    c.card_player = a.card_player
    c.position = a.position
    c.stats_batter = __merge_total_stats_batter__(a.stats_batter, b.stats_batter)

    c.stats_pitcher = __merge_stats_pitchers__(a.stats_pitcher, b.stats_pitcher)

    c.stats_fielder = __merge_stats_fielders__(a.stats_fielder, b.stats_fielder)
    
    return c

def merge_single_line_players(a: SingleLineStatsPlayer, b: SingleLineStatsPlayer) -> SingleLineStatsPlayer:
    c = SingleLineStatsPlayer()
    c.cid = a.cid
    c.card_player = copy.deepcopy(a.card_player)
    c.position = a.position
    c.stats_batter = merge_stats_batter(a.stats_batter, b.stats_batter)

    c.stats_pitcher = merge_stats_pitchers(a.stats_pitcher, b.stats_pitcher)

    if a.stats_fielder != None and b.stats_fielder != None:
        c.stats_fielder = merge_stats_fielder(a.stats_fielder, b.stats_fielder)
    elif a.stats_fielder != None:
        c.stats_fielder = copy.deepcopy(a.stats_fielder)
    elif b.stats_fielder != None:
        c.stats_fielder = copy.deepcopy(b.stats_fielder)
    
    return c