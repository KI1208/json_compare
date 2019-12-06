from json2html import *
import json
import sys
from bs4 import BeautifulSoup

TAG_WARNING = 'class="tg-warning"'
TAG_DANGER = 'class="tg-danger"'

def check_list(cell_a, cell_b):
    item_cell_a = cell_a.find_all('li')
    item_cell_b = cell_b.find_all('li')
    for j in range(len(item_cell_a)):
        if item_cell_a[j] not in item_cell_b:
            item_cell_a[j].name = 'li ' + TAG_DANGER
    for j in range(len(item_cell_b)):
        if item_cell_b[j] not in item_cell_a:
            item_cell_b[j].name = 'li ' + TAG_DANGER

if len(sys.argv) != 3 or sys.argv[1].split('.')[-1] != 'json' or sys.argv[2].split('.')[-1] != 'json':
    print('''
    Usage: python compare.py <config json> <result json>
    file extension must be 'json'
    This exe generate 'result.html'. Please view this html with any browser.
    ''')
    exit(1)

configfile, resultfile = sys.argv[1], sys.argv[2]
ths = [[], []]
tds = [[], []]
for i, file in enumerate([configfile, resultfile]):
    with open(file, 'r', encoding='utf-8') as f:
        t = json.load(f)
        html = json2html.convert(json=t, table_attributes="class=\"tg\"")
        soup = BeautifulSoup(html, features="html.parser")
        tables = soup.findChildren('table')
        rows = tables[0].find_all('tr', recursive=False)
        ths[i] = [row.find_all('th', recursive=False) for row in rows]
        tds[i] = [row.find_all('td', recursive=False) for row in rows]

th1 = ths[0]
td1, td2 = tds[0], tds[1]

for i in range(len(th1)):
    # First, check top level key's value.
    if td1[i] != td2[i]:
        # If diff, mark header cell as yellow, then drill down
        th1[i][0].name = 'th ' + TAG_WARNING

        if len(td1[i][0].contents) != len(td2[i][0].contents):
            td1[i][0].name = 'td ' + TAG_DANGER
            td2[i][0].name = 'td ' + TAG_DANGER
            continue

        # Case that td content is list or str or dict
        elif len(td1[i][0].contents) == len(td2[i][0].contents) == 1:
            if td1[i][0].contents[0].name == 'table':
                td1_rows = td1[i][0].find_all('tr')
                td2_rows = td2[i][0].find_all('tr')
                if len(td1_rows) == len(td2_rows):
                    for j in range(len(td1_rows)):
                        columns1 = td1_rows[j].find_all('td')
                        columns2 = td2_rows[j].find_all('td')
                        for k in range(len(columns1)):
                            try:
                                if columns1[k].contents[0] != [] and columns2[k].contents[0] != []:
                                    if columns1[k].contents[0].name == 'ul':
                                        check_list(columns1[k], columns2[k])
                                        continue
                                elif columns1[k].contents[0] != [] or columns2[k].contents[0] != []:
                                    columns1[k].name = 'td ' + TAG_DANGER
                                    columns2[k].name = 'td ' + TAG_DANGER
                                    continue
                                if columns1[k] != columns2[k]:
                                    columns1[k].name = 'td ' + TAG_DANGER
                                    columns2[k].name = 'td ' + TAG_DANGER
                            except IndexError as e:
                                if columns1[k] != columns2[k]:
                                    columns1[k].name = 'td ' + TAG_DANGER
                                    columns2[k].name = 'td ' + TAG_DANGER
                else:
                    for j in range(len(td1_rows)):
                        if td1_rows[j] not in td2_rows:
                            td1_rows[j].name = 'tr ' + TAG_DANGER
                    for j in range(len(td2_rows)):
                        if td2_rows[j] not in td1_rows:
                            td2_rows[j].name = 'tr ' + TAG_DANGER
            elif td1[i][0].contents[0].name == 'ul':
                check_list(td1[i][0], td2[i][0])
            else:
                td1[i][0].name = 'td ' + TAG_DANGER
                td2[i][0].name = 'td ' + TAG_DANGER
        else:
            td1[i][0].name = 'td ' + TAG_DANGER
            td2[i][0].name = 'td ' + TAG_DANGER

html_header = '''
<!DOCTYPE html>
<html>
<head>
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;border-color:skyblue;font-family:Arial, sans-serif;font-size:12px;}
.tg td{padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:skyblue;color:black;vertical-align:top;}
.tg th{font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:skyblue;color:black;background-color:skyblue;vertical-align:top;}
.tg .tg-danger{background-color:orangered  !important;}
.tg .tg-warning{background-color:gold !important;}
ul {
  list-style: none;
}
</style>
</head>
<body>
<table class="tg">
<thead><tr><th>param</th><th>Before</th><th>After</th></tr></thead>
<tbody>
'''

result = ''
for i in range(len(th1)):
    result += '<tr>' + str(th1[i][0]) + str(td1[i][0]) + str(td2[i][0]) + '</tr>'

html_footer = '''
</tbody>
</table>
</body>
</html>
'''

with open('result.html', 'w', encoding='utf-8') as f:
    f.write(html_header + result + html_footer)
