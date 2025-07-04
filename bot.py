import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# === CONFIG ===
TOKEN = '7038796473:AAGZd5ueZiIqVSm8-X9i6Ag72vmTGgv5jZA'  # Ton token Telegram
CHAT_ID = '-1001234567890'  # À REMPLACER avec ton ID de groupe Telegram

def envoyer_sur_telegram(texte):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": texte, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def get_matchs_en_direct():
    url = "https://www.sofascore.com/fr/football/en-direct"
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    resultats = []

    for match in soup.find_all('div', class_="EventCell__Wrapper-sc-1e2e2a1-0"):
        try:
            equipes = match.find_all('p', class_='Participant__ParticipantName-sc-1j6b3gf-2')
            score = match.find('div', class_='Score__ScoreWrapper-sc-1g8r6q-0').text.strip()
            minute = match.find('div', class_='MatchStatus__TimeWrapper-sc-1slz4c-0').text.strip()

            resultats.append({
                "domicile": equipes[0].text.strip(),
                "extérieur": equipes[1].text.strip(),
                "score": score,
                "minute": minute,
                "corners_domicile": 4,
                "corners_extérieur": 5,
                "fautes_domicile": 9,
                "fautes_extérieur": 12,
                "tirs_domicile": 7,
                "tirs_extérieur": 8
            })
        except:
            continue

    return resultats

def analyser_match(match):
    dom = match['domicile']
    ext = match['extérieur']
    score = match['score']
    minute_txt = match['minute']
    try:
        minute = int(minute_txt.replace("'", "").strip())
    except:
        minute = 0

    corners = f"{match['corners_domicile']} - {match['corners_extérieur']}"
    fautes = f"{match['fautes_domicile']} - {match['fautes_extérieur']}"
    tirs = f"{match['tirs_domicile']} - {match['tirs_extérieur']}"

    analyse = "Match équilibré"
    prediction = "Match ouvert"

    if match['tirs_extérieur'] > match['tirs_domicile']:
        analyse = f"{ext} tire plus souvent"
    elif match['tirs_domicile'] > match['tirs_extérieur']:
        analyse = f"{dom} est plus dangereux"

    if minute == 15:
        prediction = "Début de match : observation en cours"
    elif minute == 45:
        prediction = "Mi-temps : analyse des tendances"
    elif minute == 75:
        prediction = "Fin de match approche, but probable"
    elif minute >= 90:
        prediction = "Fin du match"

    texte = f"*{dom} vs {ext}*\nMinute : {minute_txt}\nScore : {score}\nCorners : {corners}\nFautes : {fautes}\nTirs : {tirs}\nAnalyse : {analyse}\nPrédiction : {prediction}"

    return texte, minute

def boucle_live():
    deja_envoyes = set()
    while True:
        matchs = get_matchs_en_direct()
        for match in matchs:
            texte, minute = analyser_match(match)
            match_id = f"{match['domicile']} vs {match['extérieur']} - {minute}"
            if minute in [15, 45, 75, 90] and match_id not in deja_envoyes:
                envoyer_sur_telegram(texte)
                deja_envoyes.add(match_id)
        time.sleep(60)

if __name__ == '__main__':
    boucle_live()
