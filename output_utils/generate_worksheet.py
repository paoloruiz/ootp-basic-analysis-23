from typing import Callable, List, Tuple
from output_utils.progress.progress_bar import ProgressBar
from class_model.BaseStatsPlayer import BaseStatsPlayer

def generate_worksheet(cards: List[BaseStatsPlayer], worksheet, columns: List[Tuple[str, Callable[[BaseStatsPlayer], any]]], freeze_col: str, hidden_columns: List[str], sheet_name: str):
    progress_bar = ProgressBar(len(columns) + len(cards) + len(hidden_columns), "Writing " + sheet_name + " sheet")

    # Write headers
    for i in range(len(columns)):
        worksheet.write(0, i, columns[i][0])
        
        progress_bar.increment("Writing " + sheet_name + " headers")
    # Headers are first row
    i = 1
    for card in cards:
        # Read parameters off player array
        player_arr = []
        for header in columns:
            player_arr.append(header[1](card))

        # Write to worksheet
        for j in range(len(player_arr)):
            worksheet.write(i, j, player_arr[j])
        i += 1

        progress_bar.increment("Writing " + sheet_name + " players")

    freeze_index = 1
    for i in range(len(columns)):
        if columns[i][0] == freeze_col:
            freeze_index = i
            break
    # Freeze correct panes
    worksheet.freeze_panes(1, freeze_index)

    # Hide some columns
    for hidden_col in hidden_columns:
        hidden_idx = -1
        for i in range(len(columns)):
            if columns[i][0] == hidden_col:
                hidden_idx = i
                break
        if hidden_idx > -1:
            worksheet.set_column(hidden_idx, hidden_idx, None, None, { "hidden": 1 })

        progress_bar.increment("Hiding " + sheet_name + " columns")

    progress_bar.finish()
