from bs4 import BeautifulSoup
import csv
import os

filenames = os.listdir('import_data')
for filename in filenames:
    filetype = ''
    if 'Ovr' in filename:
        filetype = 'overall/'
    elif 'vL' in filename:
        filetype = 'vL/'
    elif filename.startswith('T'):
        filetype = 'tournament/'
    elif 'Starter' in filename:
        filetype = 'starter/'
    elif 'Reliever' in filename:
        filetype = 'reliever/'
    else:
        filetype = 'vR/'

    f = open("import_data/" + filename, 'r')
    html = f.read()
    f.close()

    soup = BeautifulSoup(html.replace('\n', ''), "lxml")
    table = soup.select_one("table.data.sortable")
    headers = [th.text for th in table.select("tr th")]
    if headers[0].strip() == '':
        headers = headers[1:]
    rows = [[td.text for td in row.find_all("td")] for row in table.select("tr + tr")]
    os.remove("import_data/" + filename)

    for i in range(len(rows)):
        if rows[i][0].strip() == '':
            rows[i] = rows[i][1:]

    rows = list(filter(lambda x: x[0].strip() != '', rows))


    o = open('./data/' + filetype + filename.replace('.html', '') + '.csv', 'w', newline='')
    wr = csv.writer(o)
    wr.writerow(headers)
    wr.writerows(rows)
    o.close()