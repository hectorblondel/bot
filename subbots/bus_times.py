from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext.filters import MessageFilter

import datetime

import requests
from bs4 import BeautifulSoup


from datetime import datetime, timedelta
import logging


number_bus_displayed  = 3


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
    next_buses_times = []


    """scrapping"""



    with open("soup.html", "w") as file:
        file.write(soup.prettify())
    #print(soup.find_all('div', class_='container'))

    i = 0

    for container in soup.find_all('span', class_='next-departure-features'):
        
        if i < number_bus_displayed :

            affluence_span = container.find_all('span',class_="affluence-text hide-text-icon")
            if len(affluence_span) > 0 :
                next_buses_affluence.append(", "+affluence_span[0].text.strip().lower())
            else :
                next_buses_affluence.append("")


            if len(container.find_all('abbr', title="moins d'une minute")) > 0 :
                next_buses_min.append(0)
                next_buses_times.append(datetime.now().strftime("%Hh%M"))

            elif len(container.find_all('abbr', title="heure")) > 0 :
                subcontainer = container.find('span', class_="item-text bold")
                numbers = [num.strip() for num in container.get_text().split() if num.strip().isdigit()]

                #the hour this bus will arrive
                hours = numbers[0]
                minutes = numbers[1]
                bus_time = datetime.now().replace(hour=int(hours), minute=int(minutes))
                next_buses_times.append(bus_time.strftime("%Hh%M"))
                next_buses_min.append((bus_time - datetime.now()).seconds//60)

            else :
                minutes = int(container.find('span', class_="item-text bold").find('span')\
                            .text.split('<')[0].strip().replace('min',''))
                next_buses_min.append(minutes)
                next_buses_times.append((datetime.now() + timedelta(minutes=minutes)).strftime("%Hh%M"))

            i += 1


    """reply"""

    if len(next_buses_min) == 0:
        await update.message.reply_text("🌑 Service F1 terminé pour aujourd'hui 🌑")

    else :
        reply_message = f"📢 Prochains départs F1 : Dufay ➡️ Isnauville :"
        for i in range(number_bus_displayed):
            reply_message += f"\n{i+1} - {next_buses_min[i]} min à {next_buses_times[i]}{next_buses_affluence[i]}"
        reply_message += " 🚌"

        await update.message.reply_text(reply_message, parse_mode="HTML")
    

handlers = [MessageHandler(filters.Text("F1") | filters.Text("f1"), give_next_busses)]
