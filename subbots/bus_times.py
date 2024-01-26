from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext.filters import MessageFilter

import requests
from bs4 import BeautifulSoup


from datetime import datetime, timedelta
import logging

async def give_next_busses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """request"""

    # URL and payload
    url = "https://www.reseau-astuce.fr/fr/horaires-a-larret/28/StopTimeTable/NextDeparture"
    payload = 'destinations=%7B%221%22%3A%22Plaine+de+la+Ronce+ISNEAUVILLE%22%7D&stopId=200668&lineId=227&sens=2'  # Replace with the actual payload

    # Headers
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'ASP.NET_SessionId=4nueckqijc1ira1cqf0paqlg; language=fr; cityWay.cookies.map.legend={"legend_poi_3":0,"legend_poi_201":0,"legend_poi_204":0,"legend_poi_207":0,"legend_poi_1":0,"legend_poi_10":0,"legend_poi_202":0,"legend_poi_205":0,"legend_poi_2":0,"legend_poi_200":0,"legend_poi_203":0,"legend_poi_206":0}; cityWay.cookies.map.rememberLayer=layer-osm-route',
        'Host': 'www.reseau-astuce.fr',
        'Origin': 'https://www.reseau-astuce.fr',
        'Referer': 'https://www.reseau-astuce.fr/fr/horaires-a-larret/28/StopTimeTable/dufay/222/plaine-de-la-ronce-stade-diochon/227/plaine-de-la-ronce-isneauville/2?KeywordsStop=Dufay%20-%20ROUEN',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Gpc': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }


    # Sending POST request
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        await update.message.reply_text("Error while fetching bus times. Error code: "+str(page.status_code))
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    next_buses_min = []
    next_buses_affluence = []


    """scrapping"""

    with open("soup.html", "w") as file:
        file.write(soup.prettify())
    #print(soup.find_all('div', class_='container'))

    for container in soup.find_all('span', class_='next-departure-features'):
        next_buses_affluence.append(container.find('span',class_="affluence-text hide-text-icon").text)

        if len(container.find_all('abbr', title="moins d'une minute")) > 0 :
            next_buses_min.append(0)
        else :
            minutes = int(container.find('span', class_="item-text bold").find('span')\
                        .text.split('<')[0].strip().replace('min',''))
            next_buses_min.append(minutes)


    """reply"""

    await update.message.reply_text(f"premier bus dans {next_buses_min[0]} min, {next_buses_affluence[0]}\n"\
        + f"deuxième bus dans {next_buses_min[1]} min, {next_buses_affluence[1]}\n"\
        + f"troisième bus dans {next_buses_min[2]} min, {next_buses_affluence[2]} 🚌")
    

handlers = [MessageHandler(filters.Text("F1") | filters.Text("f1"), give_next_busses)]
