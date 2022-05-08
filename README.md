# ootp-stats-analysis-2023

## Importing new cards
Perform an import from the game called `pt_card_list.csv` in the `data/cards` folder.

## Importing new data
Drop data in `import_data/` and run `python import_data.py`.
Folder structure should be:
folder name is: (if tourney) Topeniron_32_16
* openiron is the tourney type
* 32 is the number of teams in league
* 16 is an id of tourney

In each folder, there are multiple files that can be there:
ovr.csv
vl.csv
vr.csv
starter.csv
reliever.csv
def2.csv
...
def9.csv

These correspond to different pulls

## Running analysis
You can analyze tourney info by running `python generate_tournament_report.py`