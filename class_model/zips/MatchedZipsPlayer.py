from dataclasses import dataclass
from class_model.zips.CurProjectedBatter import CurProjectedBatter
from class_model.zips.CurProjectedPitcher import CurProjectedPitcher
from class_model.zips.ZipsBatter import ZipsBatter
from class_model.zips.ZipsPitcher import ZipsPitcher
from class_model.BaseCardPlayer import BaseCardPlayer


@dataclass
class MatchedZipsPlayer:
    card_player: BaseCardPlayer
    zips_batter: ZipsBatter = None
    zips_pitcher: ZipsPitcher = None

@dataclass
class MatchedCurProjPlayer:
    card_player: BaseCardPlayer
    curproj_batter: CurProjectedBatter = None
    curproj_pitcher: CurProjectedPitcher = None