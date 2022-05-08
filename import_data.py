from bs4 import BeautifulSoup
import csv
import os
import shutil

directories = os.listdir('import_data')
for directory in directories:
    filetype = ''
    if 'Ovr' in directory:
        filetype = 'overall/'
    elif 'vL' in directory:
        filetype = 'vL/'
    elif directory.startswith('T'):
        filetype = 'tournament/'
    elif 'Starter' in directory:
        filetype = 'starter/'
    elif 'Reliever' in directory:
        filetype = 'reliever/'
    else:
        filetype = 'vR/'

    os.mkdir("data/" + filetype + directory)
    filenames = os.listdir("import_data/" + directory)
    for filename in filenames:
        f = open("import_data/" + directory + "/" + filename, 'r')
        html = f.read()
        f.close()

        soup = BeautifulSoup(html.replace('\n', ''), "lxml")
        table = soup.select_one("table.data.sortable")
        headers = [th.text for th in table.select("tr th")]
        if headers[0].strip() == '':
            headers = headers[1:]
        rows = [[td.text for td in row.find_all("td")] for row in table.select("tr + tr")]

        for i in range(len(rows)):
            if rows[i][0].strip() == '':
                rows[i] = rows[i][1:]

        rows = list(filter(lambda x: x[0].strip() != '', rows))


        o = open('./data/' + filetype + directory + "/" + filename.replace('.html', '') + '.csv', 'w', newline='')
        wr = csv.writer(o)
        wr.writerow(headers)
        wr.writerows(rows)
        o.close()
    shutil.rmtree("import_data/" + directory)