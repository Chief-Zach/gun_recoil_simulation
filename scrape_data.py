from datetime import datetime
import pandas as pd
import nodriver as uc


from bs4 import BeautifulSoup, element
import re
def get_soup_object(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_table_headers(table):
    headers = []
    for th in table.find("tr").find_all("th"):
        headers.append(th.text.strip())
    return headers

def get_table_rows(table: element.Tag):
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = []
        tds = tr.find_all("td")
        if len(tds) == 0:
            ths = tr.find_all("th")
            for th in ths:
                cells.append(th.text.strip())
        else:
            for td in tds:
                cell_text = td.text.strip()
                if "$" in cell_text:
                    stripped_text = re.sub("\D", "", cell_text)
                    cell_text = int(stripped_text)

                cells.append(cell_text)
        rows.append(cells)
    return rows

async def main():
    browser = await uc.start()

    page = await browser.get("https://www.chuckhawks.com/rifle_ballistics_table.htm")
    table = await page.find("table[bgcolor='#d3d3d3']")

    table_html = await table.get_html()

    table = get_soup_object(table_html)

    headers = ["Cartridge (Wb + type)", "MV (fps)",	"V @ 200 yds", "ME (ft lb)", "E @ 200 yds"]
    rows = get_table_rows(table)
    df = pd.DataFrame(rows, columns=headers)

    df.to_csv("muzzle_velocity_statistics.csv", index=False)

if __name__ == '__main__':
    uc.loop().run_until_complete(main())