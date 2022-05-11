from dataclasses import dataclass, field
from typing import Dict, Tuple
from class_model.BaseCardPlayer import BaseCardPlayer

from class_model.BaseStatsPlayer import BaseStatsPlayer


@dataclass
class GBRate:
    gbs: int = 0
    fbs: int = 0

@dataclass
class HBPRate:
    hbp: int = 0
    bf: int = 0

@dataclass
class PitcherStats:
    gb_rate: Dict[str, GBRate] = field(default_factory=dict)
    hbp_rate: Dict[str, HBPRate] = field(default_factory=dict)
    world_gb_rate: Dict[int, GBRate] = field(default_factory=dict)
    world_hbp_rate: HBPRate = HBPRate()
    bip: int = 0
    singles: int = 0
    doubles: int = 0
    triples: int = 0

    def get_hits_data(self, hits: int) -> Tuple[float, float, float]:
        singles = self.singles / (self.singles + self.doubles + self.triples) * hits
        doubles = self.doubles / (self.singles + self.doubles + self.triples) * hits
        triples = self.triples / (self.singles + self.doubles + self.triples) * hits

        return [ singles, doubles, triples ]

    def get_gb_rate(self, player: BaseCardPlayer) -> float:
        world_gb_rate = float(self.world_gb_rate[player.gb_type].gbs) / (self.world_gb_rate[player.gb_type].gbs + self.world_gb_rate[player.gb_type].fbs)
        if player.cid not in self.gb_rate:
            return world_gb_rate
        
        tot_biz = self.gb_rate[player.cid].gbs + self.gb_rate[player.cid].fbs

        if tot_biz == 0:
            return world_gb_rate

        local_gb_rate = float(self.gb_rate[player.cid].gbs) / tot_biz

        if tot_biz < 200:
            return world_gb_rate * (200 - tot_biz) / 200 + local_gb_rate * tot_biz / 200

        return local_gb_rate

    def get_hbp_rate(self, player: BaseCardPlayer) -> float:
        world_hbp_rate = float(self.world_hbp_rate.hbp) / self.world_hbp_rate.bf
        if player.cid not in self.hbp_rate:
            return world_hbp_rate

        tot_bf = self.hbp_rate[player.cid].bf

        if tot_bf == 0:
            return world_hbp_rate

        local_hbp_rate = float(self.hbp_rate[player.cid].hbp) / tot_bf

        if tot_bf < 200:
            return world_hbp_rate * (200 - tot_bf) / 200 + local_hbp_rate * tot_bf / 200

        return local_hbp_rate

    def capture_player_data(self, player: BaseStatsPlayer):
        if player.stats_pitcher.all == None:
            return
        cid = player.cid
        
        if cid not in self.gb_rate:
            self.gb_rate[cid] = GBRate()
            self.hbp_rate[cid] = HBPRate()
        
        gb_tendency = player.card_player.gb_type

        if gb_tendency not in self.world_gb_rate:
            self.world_gb_rate[gb_tendency] = GBRate()

        self.gb_rate[cid].gbs += player.stats_pitcher.all.pitcher_groundballs
        self.gb_rate[cid].fbs += player.stats_pitcher.all.pitcher_flyballs
        self.hbp_rate[cid].hbp += player.stats_pitcher.all.pitcher_hit_by_pitch
        self.hbp_rate[cid].bf += player.stats_pitcher.all.pitcher_bf
        self.world_gb_rate[gb_tendency].gbs += player.stats_pitcher.all.pitcher_groundballs
        self.world_gb_rate[gb_tendency].fbs += player.stats_pitcher.all.pitcher_flyballs
        self.world_hbp_rate.hbp += player.stats_pitcher.all.pitcher_hit_by_pitch
        self.world_hbp_rate.bf += player.stats_pitcher.all.pitcher_bf

        self.bip += player.stats_pitcher.all.pitcher_ab - player.stats_pitcher.all.pitcher_homeruns - player.stats_pitcher.all.pitcher_strikeouts
        self.singles += player.stats_pitcher.all.pitcher_singles
        self.doubles += player.stats_pitcher.all.pitcher_doubles
        self.triples += player.stats_pitcher.all.pitcher_triples
        