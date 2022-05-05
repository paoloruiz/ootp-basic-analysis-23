from email.mime import base
from class_model.BaseCardPlayer import headers_to_header_indices, new_base_card_player


def load_card_players():
    f = open('data/cards/pt_card_list.csv', 'r')

    headers_unparsed = f.readline()
    headers_split = headers_unparsed.split(',')
    headers = [(lambda h: h.replace('/', '').strip())(h) for h in headers_split]
    header_indices = headers_to_header_indices(headers)
    players = {}
    for line_unparsed in f.readlines():
        line_split = line_unparsed.split(',')
        play_line = [(lambda x: x.strip())(x) for x in line_split]
        base_card_player = new_base_card_player(header_indices, play_line)
        players[base_card_player.cid] = base_card_player
    f.close()

    return players