import random
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

URL = "https://www.bezruci.cz/program/2024/"
DESIRED_PLAY = "špinarka"
FOUND_DATES = []
MONTHS = ["leden", "únor", "březen", "duben", "květen", "červen", "červenec", "srpen", "září", "říjen", "listopad", "prosinec"]

def check_availability(month):
    result = []

    if (month in FOUND_DATES):
        return result
    
    response = requests.get(URL + str(month), timeout=5)
    if response.status_code != 200:
        return result
    
    soup = BeautifulSoup(response.content, "html.parser")

    program_list = soup.find("div", class_="program-list", recursive=True)

    if program_list is None:
        return result

    plays = program_list.findChildren("div", recursive=False, class_="program-item")

    for play in plays:
        name = play.find("div", class_="play-text").find("h3").find("a").text
        if name == DESIRED_PLAY and (play.find("div", class_="play-ticket-buy") is not None):
            day_of_month = play.find("div", class_="play-date").find("div", class_="day-no").text
            result.append(day_of_month)
            
    if len(plays) > 0:
        FOUND_DATES.append(month)

    return result

def send_email(availability, searched_month):
    user = 'play.cz.studiomp@gmail.com'
    with open('.env', 'r') as file:
        password = file.read().strip()

    msg = MIMEMultipart()
    msg.attach(MIMEText(f"Hraje se {DESIRED_PLAY}!\nPředstavení s možností koupit lístek se hraj{'í' if len(availability) > 1 else 'e'}: {', '.join(map(lambda a: a + '.', availability))} v měsíci {MONTHS[searched_month - 1]}\n{URL + str(searched_month)}", 'plain'))
    msg["Subject"] = f"Hraje se {DESIRED_PLAY}!"
    msg["From"] = "play.cz.studiomp@gmail.com"
    msg["To"] = "glos2001@seznam.cz,gym.helena@gmail.com"

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(user, password)
        server.send_message(msg)
        server.close()
    except Exception as e:
        print("Email se nepodařilo odeslat", e)


def main():
    while True:
        searched_month = FOUND_DATES[-1] + 1 if len(FOUND_DATES) else datetime.now().month + 1
        print("Kontroluju dostupnost hry", DESIRED_PLAY, "v měsíci", MONTHS[searched_month - 1])

        availability = check_availability(searched_month)
        
        if len(availability) > 0:
            send_email(availability, searched_month)
        else:
            print("Hra", DESIRED_PLAY, "není v měsíci", MONTHS[searched_month - 1], "k dispozici")

        time.sleep(60 * (60 + random.randint(-3, 13))) # 1 hour

if __name__ == "__main__":
    main()