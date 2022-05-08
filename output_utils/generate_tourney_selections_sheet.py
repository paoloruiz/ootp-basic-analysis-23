from output_utils.progress.progress_bar import ProgressBar



def generate_tourney_selections(worksheet, sheet_name: str):
    progress_bar = ProgressBar(1, "Writing " + sheet_name + " sheet")

    worksheet.write(0, 0, "MIN_PA")
    worksheet.write(0, 1, 1)
    worksheet.write(0, 2, "MIN_BF")
    worksheet.write(0, 3, 1)

    progress_bar.finish()