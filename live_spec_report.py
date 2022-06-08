from typing import Dict, List
from analysis.zips_projections import get_batter_projections, get_pitcher_projections
from class_model.load_players import load_card_players, load_card_players_file
from class_model.zips.CurProjectedBatter import CurProjectedBatter, headers_to_cur_projected_batter_header_indices, join_projected_batters, new_cur_projected_batter
from class_model.zips.CurProjectedPitcher import CurProjectedPitcher, headers_to_cur_projected_pitcher_header_indices, join_projected_pitcher, new_cur_projected_pitcher
from class_model.zips.MatchedZipsPlayer import MatchedCurProjPlayer, MatchedZipsPlayer
from class_model.zips.ZipsBatter import ZipsBatter, headers_to_zips_batter_header_indices, new_zips_batter
from output_utils.csvwriter import CsvWriter
from difflib import get_close_matches

from class_model.zips.ZipsPitcher import ZipsPitcher, headers_to_zips_pitcher_header_indices, new_zips_pitcher



def load_zips_batters() -> List[ZipsBatter]:
    f = open('data/zips/bzips.csv', 'r', encoding="utf-8", errors="replace")

    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').replace('\ufeff', '').strip())(h) for h in headers_split]
    header_indices = headers_to_zips_batter_header_indices(headers)
    players = []
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        players.append(new_zips_batter(header_indices, play_line))
    f.close()

    return players


def load_zips_pitchers() -> List[ZipsPitcher]:
    f = open('data/zips/pzips.csv', 'r', encoding="utf-8", errors="replace")

    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').replace('\ufeff', '').strip())(h) for h in headers_split]
    header_indices = headers_to_zips_pitcher_header_indices(headers)
    players = []
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        players.append(new_zips_pitcher(header_indices, play_line))
    f.close()

    return players


def load_cur_projected_batters() -> Dict[str, CurProjectedBatter]:
    f = open('data/zips/batter_cur_stats.csv', 'r', encoding="utf-8", errors="replace")

    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').replace('\ufeff', '').strip())(h) for h in headers_split]
    header_indices = headers_to_cur_projected_batter_header_indices(headers)
    players: Dict[str, CurProjectedBatter] = {}
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        cur_proj_batter = new_cur_projected_batter(header_indices, play_line)
        players[cur_proj_batter.playerid] = cur_proj_batter
    f.close()

    f = open('data/zips/batter_zips_ros.csv', 'r', encoding="utf-8", errors="replace")

    proj_batters = {}
    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').replace('\ufeff', '').strip())(h) for h in headers_split]
    header_indices = headers_to_cur_projected_batter_header_indices(headers)
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        cur_proj_batter = new_cur_projected_batter(header_indices, play_line)
        if cur_proj_batter.playerid not in players.keys():
            proj_batters[cur_proj_batter.playerid] = cur_proj_batter
        else:
            proj_batters[cur_proj_batter.playerid] = join_projected_batters(cur_proj_batter, players[cur_proj_batter.playerid])

    return proj_batters


def load_cur_projected_pitchers() -> Dict[str, CurProjectedPitcher]:
    f = open('data/zips/pitcher_cur_stats.csv', 'r', encoding="utf-8", errors="replace")

    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').replace('\ufeff', '').strip())(h) for h in headers_split]
    header_indices = headers_to_cur_projected_pitcher_header_indices(headers)
    players: Dict[str, CurProjectedPitcher] = {}
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        cur_proj_pitcher = new_cur_projected_pitcher(header_indices, play_line)
        players[cur_proj_pitcher.playerid] = cur_proj_pitcher
    f.close()

    f = open('data/zips/pitcher_zips_ros.csv', 'r', encoding="utf-8", errors="replace")

    proj_batters = {}
    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').replace('\ufeff', '').strip())(h) for h in headers_split]
    header_indices = headers_to_cur_projected_pitcher_header_indices(headers)
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        cur_proj_pitcher = new_cur_projected_pitcher(header_indices, play_line)
        if cur_proj_pitcher.playerid not in players.keys():
            proj_batters[cur_proj_pitcher.playerid] = cur_proj_pitcher
        else:
            proj_batters[cur_proj_pitcher.playerid] = join_projected_pitcher(cur_proj_pitcher, players[cur_proj_pitcher.playerid])

    return proj_batters

live_card_players = list(filter(lambda c_player: c_player.full_title.startswith("MLB 2022 Live"), load_card_players_file("zips/player_ratings_start.csv").values()))

# Filter out 2-way players
live_card_players = list(filter(lambda player: player.first_name != "Shohei", live_card_players))

# Batter
zips_batters = load_zips_batters()

zips_batter_names = list(map(lambda player: player.name, zips_batters))

live_card_batters = list(filter(lambda player: player.position != 1 and player.position < 10, live_card_players))

matched_batters: List[MatchedZipsPlayer] = []

for batter in live_card_batters:
    closest_match = get_close_matches(batter.name, zips_batter_names, n=1)[0]

    zips_batter_matches = list(filter(lambda player: player.name == closest_match, zips_batters))

    matched_batters.append(MatchedZipsPlayer(card_player=batter, zips_batter=zips_batter_matches[0]))

batter_projections = get_batter_projections(matched_batters)

# Pitcher
zips_pitchers = load_zips_pitchers()

zips_pitcher_names = list(map(lambda player: player.name, zips_pitchers))

live_card_pitchers = list(filter(lambda player: player.position == 1 or player.position > 9, live_card_players))

matched_pitchers: List[MatchedZipsPlayer] = []
no_zips_pitchers = ["Jeurys Familia"]

for pitcher in live_card_pitchers:
    if pitcher.name in no_zips_pitchers:
        continue
    closest_match = get_close_matches(pitcher.name, zips_pitcher_names, n=1)[0]

    zips_pitcher_matches = list(filter(lambda player: player.name == closest_match, zips_pitchers))

    matched_pitchers.append(MatchedZipsPlayer(card_player=pitcher, zips_pitcher=zips_pitcher_matches[0]))

matched_sp = list(filter(lambda player: " SP " in player.card_player.full_title, matched_pitchers))
matched_rp = list(filter(lambda player: " SP " not in player.card_player.full_title, matched_pitchers))

sp_predictions = get_pitcher_projections(matched_sp)
rp_predictions = get_pitcher_projections(matched_rp)

# Currently projected batters
proj_batters = load_cur_projected_batters()

card_proj_batters: List[MatchedCurProjPlayer] = []
for batter in matched_batters:
    if batter.zips_batter.playerid not in proj_batters.keys():
        continue
    

    card_proj_batters.append(MatchedCurProjPlayer(card_player=batter.card_player, curproj_batter=proj_batters[batter.zips_batter.playerid]))

proj_pitchers = load_cur_projected_pitchers()

card_proj_sp: List[MatchedCurProjPlayer] = []
for pitcher in matched_sp:
    if pitcher.zips_pitcher.playerid not in proj_pitchers.keys():
        continue
    
    card_proj_sp.append(MatchedCurProjPlayer(card_player=pitcher.card_player, curproj_pitcher=proj_pitchers[pitcher.zips_pitcher.playerid]))

card_proj_rp: List[MatchedCurProjPlayer] = []
for pitcher in matched_rp:
    if pitcher.zips_pitcher.playerid not in proj_pitchers.keys():
        continue
    
    card_proj_rp.append(MatchedCurProjPlayer(card_player=pitcher.card_player, curproj_pitcher=proj_pitchers[pitcher.zips_pitcher.playerid]))


cur_card_players = load_card_players()

bat_csv_writer = CsvWriter()
bat_csv_writer.record(["Title", "Current OVR", "Starting OVR", "Projected OVR", "Diff from current", "avk", "babip", "pow", "eye", "gap", 
    "proj_avk", "proj_babip", "proj_pow", "proj_eye", "proj_gap", "diff_avk", "diff_babip", "diff_pow", "diff_eye", "diff_gap"])

for batter in card_proj_batters:
    if batter.card_player.cid not in cur_card_players:
        continue
    cur_ovr = cur_card_players[batter.card_player.cid].ovr
    starting_ovr = batter.card_player.ovr
    avk = batter_projections.get_avk(batter.curproj_batter.get_k_rate())
    babip = batter_projections.get_babip(batter.curproj_batter.get_babip_rate())
    pow = batter_projections.get_pow(batter.curproj_batter.get_hr_rate())
    eye = batter_projections.get_eye(batter.curproj_batter.get_bb_rate())
    gap = batter_projections.get_gap(batter.curproj_batter.get_xbh_rate())
    # avk, babip, pow, eye, gap, card_player -> ovr rating
    proj_ovr = batter_projections.get_ovr(
        avk,
        babip,
        pow,
        eye,
        gap,
        batter.card_player
    )

    cur_avk = cur_card_players[batter.card_player.cid].avk_ovr
    cur_babip = cur_card_players[batter.card_player.cid].babip_ovr
    cur_pow = cur_card_players[batter.card_player.cid].pow_ovr
    cur_eye = cur_card_players[batter.card_player.cid].eye_ovr
    cur_gap = cur_card_players[batter.card_player.cid].gap_ovr

    bat_csv_writer.record([batter.card_player.full_title, cur_ovr, starting_ovr, proj_ovr, cur_ovr - proj_ovr, cur_avk, cur_babip, cur_pow, cur_eye, cur_gap, avk, babip, pow, eye, gap, cur_avk - avk, 
        cur_babip - babip, cur_pow - pow, cur_eye - eye, cur_gap - gap])

f = open("output/batlivespec.csv", "w")
f.write(bat_csv_writer.getCSV())
f.close()

pit_csv_writer = CsvWriter()
pit_csv_writer.record(["Title", "Current OVR", "Starting OVR", "Projected OVR", "Diff from current", "stu", "mov", "ctl", "proj_stu", "proj_mov", "proj_ctl", "diff_stu", "diff_mov", "diff_ctl"])
for pitcher in card_proj_sp:
    if pitcher.card_player.cid not in cur_card_players:
        continue
    cur_ovr = cur_card_players[pitcher.card_player.cid].ovr
    starting_ovr = pitcher.card_player.ovr
    stu = sp_predictions.get_stu(pitcher.curproj_pitcher.get_k_per_9())
    mov = sp_predictions.get_mov(pitcher.curproj_pitcher.get_hr_per_9(), pitcher.card_player)
    ctl = sp_predictions.get_ctl(pitcher.curproj_pitcher.get_bb_per_9())
    proj_ovr = sp_predictions.get_ovr(
        stu,
        mov,
        ctl,
        pitcher.card_player
    )

    cur_stu = cur_card_players[pitcher.card_player.cid].stu_ovr
    cur_mov = cur_card_players[pitcher.card_player.cid].mov_ovr
    cur_ctl = cur_card_players[pitcher.card_player.cid].ctl_ovr
    pit_csv_writer.record([pitcher.card_player.full_title, cur_ovr, starting_ovr, proj_ovr, cur_ovr - proj_ovr, cur_stu, cur_mov, cur_ctl, stu, mov, ctl, cur_stu - stu, cur_mov - mov, cur_ctl - ctl])

for pitcher in card_proj_rp:
    if pitcher.card_player.cid not in cur_card_players:
        continue
    cur_ovr = cur_card_players[pitcher.card_player.cid].ovr
    starting_ovr = pitcher.card_player.ovr
    stu = rp_predictions.get_stu(pitcher.curproj_pitcher.get_k_per_9())
    mov = rp_predictions.get_mov(pitcher.curproj_pitcher.get_hr_per_9(), pitcher.card_player)
    ctl = rp_predictions.get_ctl(pitcher.curproj_pitcher.get_bb_per_9())
    proj_ovr = rp_predictions.get_ovr(
        stu,
        mov,
        ctl,
        pitcher.card_player
    )

    cur_stu = cur_card_players[pitcher.card_player.cid].stu_ovr
    cur_mov = cur_card_players[pitcher.card_player.cid].mov_ovr
    cur_ctl = cur_card_players[pitcher.card_player.cid].ctl_ovr
    pit_csv_writer.record([pitcher.card_player.full_title, cur_ovr, starting_ovr, proj_ovr, cur_ovr - proj_ovr, cur_stu, cur_mov, cur_ctl, stu, mov, ctl, cur_stu - stu, cur_mov - mov, cur_ctl - ctl])

f = open("output/pitlivespec.csv", "w")
f.write(pit_csv_writer.getCSV())
f.close()