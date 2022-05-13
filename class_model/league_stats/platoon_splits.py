
from dataclasses import dataclass

from class_model.BaseStatsPlayer import SingleLineStatsPlayer


@dataclass
class PlatoonStarts:
    platoon_nonc_vr_starts: int = 0
    platoon_nonc_vl_starts: int = 0
    platoon_c_vr_starts: int = 0
    platoon_c_vl_starts: int = 0

    def get_vlhp_pct(self, pos_num: int) -> float:
        if pos_num == 2:
            return float(self.platoon_c_vl_starts) / (self.platoon_c_vl_starts + self.platoon_c_vr_starts)
        return float(self.platoon_nonc_vl_starts) / (self.platoon_nonc_vl_starts + self.platoon_nonc_vr_starts)

@dataclass
class NonPlatoonStarts:
    all_starter_nonc_starts: int = 0
    all_backup_nonc_starts: int = 0
    all_starter_c_starts: int = 0
    all_backup_c_starts: int = 0

@dataclass
class BatterVPitcherStarts:
    exp_rhb_vrhp_starts: int = 0
    exp_lhb_vrhp_starts: int = 0
    exp_rhb_vlhp_starts: int = 0
    exp_lhb_vlhp_starts: int = 0

    def get_vlhb_pct(self, throws: str) -> float:
        if throws == "R":
            return float(self.exp_lhb_vrhp_starts) / (self.exp_lhb_vrhp_starts + self.exp_rhb_vrhp_starts)
        return float(self.exp_lhb_vlhp_starts) / (self.exp_lhb_vlhp_starts + self.exp_rhb_vlhp_starts)

def merge_platoon_starts(a: PlatoonStarts, b: PlatoonStarts) -> PlatoonStarts:
    c = PlatoonStarts()

    c.platoon_c_vl_starts = a.platoon_c_vl_starts + b.platoon_c_vl_starts
    c.platoon_c_vr_starts = a.platoon_c_vr_starts + b.platoon_c_vr_starts
    c.platoon_nonc_vl_starts = a.platoon_nonc_vl_starts + b.platoon_nonc_vl_starts
    c.platoon_nonc_vr_starts = a.platoon_nonc_vr_starts + b.platoon_nonc_vr_starts
    
    return c

def merge_non_platoon_starts(a: NonPlatoonStarts, b: NonPlatoonStarts) -> NonPlatoonStarts:
    c = NonPlatoonStarts()

    c.all_starter_c_starts = a.all_starter_c_starts + b.all_starter_c_starts
    c.all_backup_c_starts = a.all_backup_c_starts + b.all_backup_c_starts
    c.all_starter_nonc_starts = a.all_starter_nonc_starts + b.all_starter_nonc_starts
    c.all_backup_nonc_starts = a.all_backup_nonc_starts + b.all_backup_nonc_starts
    
    return c

def merge_bvp_starts(a: BatterVPitcherStarts, b: BatterVPitcherStarts) -> BatterVPitcherStarts:
    c = BatterVPitcherStarts()

    c.exp_lhb_vlhp_starts = a.exp_lhb_vlhp_starts + b.exp_lhb_vlhp_starts
    c.exp_lhb_vrhp_starts = a.exp_lhb_vrhp_starts + b.exp_lhb_vrhp_starts
    c.exp_rhb_vlhp_starts = a.exp_rhb_vlhp_starts + b.exp_rhb_vlhp_starts
    c.exp_rhb_vrhp_starts = a.exp_rhb_vrhp_starts + b.exp_rhb_vrhp_starts
    
    return c

@dataclass
class PlatoonSplits:
    platoon_starts: PlatoonStarts = PlatoonStarts()
    non_platoon_starts: NonPlatoonStarts = NonPlatoonStarts()
    batter_vs_pitcher_starts: BatterVPitcherStarts = BatterVPitcherStarts()

    def count_platoon_starts(self, ps: PlatoonStarts):
        self.platoon_starts = merge_platoon_starts(self.platoon_starts, ps)

    def count_non_platoon_starts(self, nps: NonPlatoonStarts):
        self.non_platoon_starts = merge_non_platoon_starts(self.non_platoon_starts, nps)

    def count_bvp_starts(self, bvp_starts: BatterVPitcherStarts):
        self.batter_vs_pitcher_starts = merge_bvp_starts(self.batter_vs_pitcher_starts, bvp_starts)

def get_platoon_starts(type: str, player: SingleLineStatsPlayer) -> PlatoonStarts:
    ps = PlatoonStarts()
    if type == "vL":
        if player.get_fielding_position() == 2:
            ps.platoon_c_vl_starts = player.stats_fielder.fielding_games_started
        else:
            ps.platoon_nonc_vl_starts = player.stats_fielder.fielding_games_started if player.get_fielding_position() > 0 else player.special_mod_bat_gs
    else:
        if player.get_fielding_position() == 2:
            ps.platoon_c_vr_starts = player.stats_fielder.fielding_games_started
        else:
            ps.platoon_nonc_vr_starts = player.stats_fielder.fielding_games_started if player.get_fielding_position() > 0 else player.special_mod_bat_gs
    return ps

def get_non_platoon_starts(type: str, player: SingleLineStatsPlayer) -> NonPlatoonStarts:
    nps = NonPlatoonStarts()
    if type == "starter":
        if player.get_fielding_position() == 2:
            nps.all_starter_c_starts = player.stats_fielder.fielding_games_started
        else:
            nps.all_starter_nonc_starts = player.stats_fielder.fielding_games_started if player.get_fielding_position() > 0 else player.special_mod_bat_gs
    else:
        if player.get_fielding_position() == 2:
            nps.all_backup_c_starts = player.stats_fielder.fielding_games_started
        else:
            nps.all_backup_nonc_starts = player.stats_fielder.fielding_games_started if player.get_fielding_position() > 0 else player.special_mod_bat_gs
    return nps

def get_batter_v_pitcher_starts(player: SingleLineStatsPlayer) -> BatterVPitcherStarts:
    bvp_st = BatterVPitcherStarts()
    if player.get_fielding_position() == 0:
        if player.card_player.bats == "R":
            bvp_st.exp_rhb_vlhp_starts = player.special_mod_bat_gs
            bvp_st.exp_rhb_vrhp_starts = player.special_mod_bat_gs
        elif player.card_player.bats == "L":
            bvp_st.exp_lhb_vlhp_starts = player.special_mod_bat_gs
            bvp_st.exp_lhb_vrhp_starts = player.special_mod_bat_gs
        else:
            bvp_st.exp_rhb_vlhp_starts = player.special_mod_bat_gs
            bvp_st.exp_lhb_vrhp_starts = player.special_mod_bat_gs
    else:
        if player.card_player.bats == "R":
            bvp_st.exp_rhb_vlhp_starts = player.stats_fielder.fielding_games_started
            bvp_st.exp_rhb_vrhp_starts = player.stats_fielder.fielding_games_started
        elif player.card_player.bats == "L":
            bvp_st.exp_lhb_vlhp_starts = player.stats_fielder.fielding_games_started
            bvp_st.exp_lhb_vrhp_starts = player.stats_fielder.fielding_games_started
        else:
            bvp_st.exp_rhb_vlhp_starts = player.stats_fielder.fielding_games_started
            bvp_st.exp_lhb_vrhp_starts = player.stats_fielder.fielding_games_started
    return bvp_st