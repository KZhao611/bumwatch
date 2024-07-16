from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")

def search_riot_id(str):
    gameName, tagLine = str.split("#")
    res = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={api_key}")
    if res.status_code != 200:
        raise Exception("Unable to get PUUID")
    data = res.json()
    return(data["puuid"])

# def is_live(puuid, region):
