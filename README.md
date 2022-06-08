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
def2.csv
...
def9.csv

These correspond to different pulls
Basically, for a pull
1. check all fields in all the stats folders
2. In "General" the checked ones are: ID, Position, Name, Team, Team (Short)
3. In Misc. Info, the checked ones are: PT Card ID

when you download, download "only html" for each position of catcher through RF naming them "def2" for catcher, "def3" for first base and so on.
If it's not a tournament you can download the vl.html and vr.html
Always download the ovr.csv


## Running analysis
You can analyze tourney info by running `python generate_tournament_report.py`
This will generate several files in the output folder that you can look through - anything not marked PROJ- is purely stats based, anything marked PROJ- is based on projections generated
You can also generate league and tournament reports. Just message me if you have major problems.