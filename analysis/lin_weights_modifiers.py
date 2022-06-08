from dataclasses import dataclass


@dataclass
class LinearWeightsModifiers:
    bb_mod: float = 1.0
    hbp_mod: float = 1.0
    xbh_mod: float = 1.0
    homeruns_mod: float = 1.0
    babip_mod: float = 1.0
    sb_mod: float = 1.0
    cs_mod: float = 1.0
    k_mod: float = 1.0
    zr_mod: float = 1.0
    frame_runs_mod: float = 1.0
    cabi_mod: float = 1.0
    arm_runs_mod: float = 1.0
    cs_against_c_mod: float = 1.0
    sba_against_c_mod: float = 1.0

@dataclass
class LeagueLWM:
    batting: LinearWeightsModifiers
    pitching: LinearWeightsModifiers