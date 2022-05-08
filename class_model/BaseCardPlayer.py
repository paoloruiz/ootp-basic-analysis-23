from dataclasses import dataclass
from wsgiref import headers

def __search_with_reasonable_error__(headers, index_name):
    try:
        return headers.index(index_name)
    except ValueError:
        raise Exception(index_name + " not included in headers: " + str(headers))

def headers_to_header_indices(headers):
    header_indices = {}

    header_indices["cid_index"] = __search_with_reasonable_error__(headers, "Card ID")
    header_indices["full_title_index"] = __search_with_reasonable_error__(headers, "Card Title")
    header_indices["first_name_index"] = __search_with_reasonable_error__(headers, "FirstName")
    header_indices["last_name_index"] = __search_with_reasonable_error__(headers, "LastName")
    header_indices["team_index"] = __search_with_reasonable_error__(headers, "Team")
    header_indices["year_index"] = __search_with_reasonable_error__(headers, "Year")
    header_indices["ovr_index"] = __search_with_reasonable_error__(headers, "Card Value")
    header_indices["bats_index"] = __search_with_reasonable_error__(headers, "Bats")
    header_indices["throws_index"] = __search_with_reasonable_error__(headers, "Throws")
    header_indices["con_ovr_index"] = __search_with_reasonable_error__(headers, "Contact")
    header_indices["gap_ovr_index"] = __search_with_reasonable_error__(headers, "Gap")
    header_indices["pow_ovr_index"] = __search_with_reasonable_error__(headers, "Power")
    header_indices["eye_ovr_index"] = __search_with_reasonable_error__(headers, "Eye")
    header_indices["avk_ovr_index"] = __search_with_reasonable_error__(headers, "Avoid Ks")
    header_indices["babip_ovr_index"] = __search_with_reasonable_error__(headers, "BABIP")
    header_indices["con_vl_index"] = __search_with_reasonable_error__(headers, "Contact vL")
    header_indices["gap_vl_index"] = __search_with_reasonable_error__(headers, "Gap vL")
    header_indices["pow_vl_index"] = __search_with_reasonable_error__(headers, "Power vL")
    header_indices["eye_vl_index"] = __search_with_reasonable_error__(headers, "Eye vL")
    header_indices["avk_vl_index"] = __search_with_reasonable_error__(headers, "Avoid K vL")
    header_indices["babip_vl_index"] = __search_with_reasonable_error__(headers, "BABIP vL")
    header_indices["con_vr_index"] = __search_with_reasonable_error__(headers, "Contact vR")
    header_indices["gap_vr_index"] = __search_with_reasonable_error__(headers, "Gap vR")
    header_indices["pow_vr_index"] = __search_with_reasonable_error__(headers, "Power vR")
    header_indices["eye_vr_index"] = __search_with_reasonable_error__(headers, "Eye vR")
    header_indices["avk_vr_index"] = __search_with_reasonable_error__(headers, "Ks vR")
    header_indices["babip_vr_index"] = __search_with_reasonable_error__(headers, "BABIP vR")
    header_indices["stu_ovr_index"] = __search_with_reasonable_error__(headers, "Stuff")
    header_indices["mov_ovr_index"] = __search_with_reasonable_error__(headers, "Movement")
    header_indices["ctl_ovr_index"] = __search_with_reasonable_error__(headers, "Control")
    header_indices["stu_vl_index"] = __search_with_reasonable_error__(headers, "Stuff vL")
    header_indices["mov_vl_index"] = __search_with_reasonable_error__(headers, "Movement vL")
    header_indices["ctl_vl_index"] = __search_with_reasonable_error__(headers, "Control vL")
    header_indices["stu_vr_index"] = __search_with_reasonable_error__(headers, "Stuff vR")
    header_indices["mov_vr_index"] = __search_with_reasonable_error__(headers, "Movement vR")
    header_indices["ctl_vr_index"] = __search_with_reasonable_error__(headers, "Control vR")
    header_indices["gb_type_index"] = __search_with_reasonable_error__(headers, "GB")
    header_indices["stamina_index"] = __search_with_reasonable_error__(headers, "Stamina")
    header_indices["hold_index"] = __search_with_reasonable_error__(headers, "Hold")
    header_indices["speed_index"] = __search_with_reasonable_error__(headers, "Speed")
    header_indices["steal_index"] = __search_with_reasonable_error__(headers, "Stealing")
    header_indices["baserunning_index"] = __search_with_reasonable_error__(headers, "Baserunning")
    header_indices["defense_c_index"] = __search_with_reasonable_error__(headers, "Pos Rating C")
    header_indices["defense_1b_index"] = __search_with_reasonable_error__(headers, "Pos Rating 1B")
    header_indices["defense_2b_index"] = __search_with_reasonable_error__(headers, "Pos Rating 2B")
    header_indices["defense_3b_index"] = __search_with_reasonable_error__(headers, "Pos Rating 3B")
    header_indices["defense_ss_index"] = __search_with_reasonable_error__(headers, "Pos Rating SS")
    header_indices["defense_lf_index"] = __search_with_reasonable_error__(headers, "Pos Rating LF")
    header_indices["defense_cf_index"] = __search_with_reasonable_error__(headers, "Pos Rating CF")
    header_indices["defense_rf_index"] = __search_with_reasonable_error__(headers, "Pos Rating RF")
    header_indices["defense_p_index"] = __search_with_reasonable_error__(headers, "Pos Rating P")
    header_indices["ifrange_index"] = __search_with_reasonable_error__(headers, "Infield Range")
    header_indices["ifarm_index"] = __search_with_reasonable_error__(headers, "Infield Arm")
    header_indices["turndp_index"] = __search_with_reasonable_error__(headers, "DP")
    header_indices["iferr_index"] = __search_with_reasonable_error__(headers, "Infield Error")
    header_indices["ofrange_index"] = __search_with_reasonable_error__(headers, "OF Range")
    header_indices["ofarm_index"] = __search_with_reasonable_error__(headers, "OF Arm")
    header_indices["oferr_index"] = __search_with_reasonable_error__(headers, "OF Error")
    header_indices["cabi_index"] = __search_with_reasonable_error__(headers, "CatcherAbil")
    header_indices["carm_index"] = __search_with_reasonable_error__(headers, "Catcher Arm")
    header_indices["highest_buy_order_index"] = __search_with_reasonable_error__(headers, "Buy Order High")
    header_indices["lowest_sell_order_index"] = __search_with_reasonable_error__(headers, "Sell Order Low")
    header_indices["last_10_price_index"] = __search_with_reasonable_error__(headers, "Last 10 Price")

    return header_indices

def new_base_card_player(header_indices, play_line):
    return BaseCardPlayer(
        cid=str(play_line[header_indices["cid_index"]]),
        full_title=str(play_line[header_indices["full_title_index"]]),
        name=str(play_line[header_indices["first_name_index"]] + " " + play_line[header_indices["last_name_index"]]),
        first_name=str(play_line[header_indices["first_name_index"]]),
        last_name=str(play_line[header_indices["last_name_index"]]),
        team=str(play_line[header_indices["team_index"]]),
        year=int(play_line[header_indices["year_index"]]),
        ovr=int(play_line[header_indices["ovr_index"]]),
        bats="R" if int(play_line[header_indices["bats_index"]]) == 1 else ("L" if int(play_line[header_indices["bats_index"]]) == 2 else "S"),
        throws="R" if int(play_line[header_indices["throws_index"]]) == 1 else "L",
        con_ovr=int(play_line[header_indices["con_ovr_index"]]),
        gap_ovr=int(play_line[header_indices["gap_ovr_index"]]),
        pow_ovr=int(play_line[header_indices["pow_ovr_index"]]),
        eye_ovr=int(play_line[header_indices["eye_ovr_index"]]),
        avk_ovr=int(play_line[header_indices["avk_ovr_index"]]),
        babip_ovr=int(play_line[header_indices["babip_ovr_index"]]),
        con_vl=int(play_line[header_indices["con_vl_index"]]),
        gap_vl=int(play_line[header_indices["gap_vl_index"]]),
        pow_vl=int(play_line[header_indices["pow_vl_index"]]),
        eye_vl=int(play_line[header_indices["eye_vl_index"]]),
        avk_vl=int(play_line[header_indices["avk_vl_index"]]),
        babip_vl=int(play_line[header_indices["babip_vl_index"]]),
        con_vr=int(play_line[header_indices["con_vr_index"]]),
        gap_vr=int(play_line[header_indices["gap_vr_index"]]),
        pow_vr=int(play_line[header_indices["pow_vr_index"]]),
        eye_vr=int(play_line[header_indices["eye_vr_index"]]),
        avk_vr=int(play_line[header_indices["avk_vr_index"]]),
        babip_vr=int(play_line[header_indices["babip_vr_index"]]),
        stu_ovr=int(play_line[header_indices["stu_ovr_index"]]),
        mov_ovr=int(play_line[header_indices["mov_ovr_index"]]),
        ctl_ovr=int(play_line[header_indices["ctl_ovr_index"]]),
        stu_vl=int(play_line[header_indices["stu_vl_index"]]),
        mov_vl=int(play_line[header_indices["mov_vl_index"]]),
        ctl_vl=int(play_line[header_indices["ctl_vl_index"]]),
        stu_vr=int(play_line[header_indices["con_vr_index"]]),
        mov_vr=int(play_line[header_indices["mov_vr_index"]]),
        ctl_vr=int(play_line[header_indices["ctl_vr_index"]]),
        gb_type=int(play_line[header_indices["gb_type_index"]]),
        stamina=int(play_line[header_indices["stamina_index"]]),
        hold=int(play_line[header_indices["hold_index"]]),
        speed=int(play_line[header_indices["speed_index"]]),
        steal=int(play_line[header_indices["steal_index"]]),
        baserunning=int(play_line[header_indices["baserunning_index"]]),
        defensec=int(play_line[header_indices["defense_c_index"]]),
        defense1b=int(play_line[header_indices["defense_1b_index"]]),
        defense2b=int(play_line[header_indices["defense_2b_index"]]),
        defense3b=int(play_line[header_indices["defense_3b_index"]]),
        defensess=int(play_line[header_indices["defense_ss_index"]]),
        defenself=int(play_line[header_indices["defense_lf_index"]]),
        defensecf=int(play_line[header_indices["defense_cf_index"]]),
        defenserf=int(play_line[header_indices["defense_rf_index"]]),
        defensep=int(play_line[header_indices["defense_p_index"]]),
        ifrange=int(play_line[header_indices["ifrange_index"]]),
        ifarm=int(play_line[header_indices["ifarm_index"]]),
        turndp=int(play_line[header_indices["turndp_index"]]),
        iferr=int(play_line[header_indices["iferr_index"]]),
        ofrange=int(play_line[header_indices["ofrange_index"]]),
        ofarm=int(play_line[header_indices["ofarm_index"]]),
        oferr=int(play_line[header_indices["oferr_index"]]),
        cabi=int(play_line[header_indices["cabi_index"]]),
        carm=int(play_line[header_indices["carm_index"]]),
        highest_buy_order=int(play_line[header_indices["highest_buy_order_index"]]),
        lowest_sell_order=int(play_line[header_indices["lowest_sell_order_index"]]),
        last_10_price=int(play_line[header_indices["last_10_price_index"]])
    )

@dataclass
class BaseCardPlayer:
    cid: str
    full_title: str
    team: str
    year: int
    name: str
    first_name: str
    last_name: str
    ovr: int
    bats: str
    throws: str
    con_ovr: int
    gap_ovr: int
    pow_ovr: int
    eye_ovr: int
    avk_ovr: int
    babip_ovr: int
    con_vl: int
    gap_vl: int
    pow_vl: int
    eye_vl: int
    avk_vl: int
    babip_vl: int
    con_vr: int
    gap_vr: int
    pow_vr: int
    eye_vr: int
    avk_vr: int
    babip_vr: int
    stu_ovr: int
    mov_ovr: int
    ctl_ovr: int
    stu_vl: int
    mov_vl: int
    ctl_vl: int
    stu_vr: int
    mov_vr: int
    ctl_vr: int
    gb_type: int
    stamina: int
    hold: int
    speed: int
    steal: int
    baserunning: int
    defensec: int
    defense1b: int
    defense2b: int
    defense3b: int
    defensess: int
    defenself: int
    defensecf: int
    defenserf: int
    defensep: int
    ifrange: int
    ifarm: int
    turndp: int
    iferr: int
    ofrange: int
    ofarm: int
    oferr: int
    cabi: int
    carm: int
    highest_buy_order: int
    lowest_sell_order: int
    last_10_price: int
