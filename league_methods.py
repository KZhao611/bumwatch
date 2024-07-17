from dotenv import load_dotenv
import os
import requests
import asyncio
from enum import Enum

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")

class Region(Enum):
    BR = "BR1",
    EUNE = "EUN1",
    EUW = "EUW1",
    LAN = "LA1",
    LAS = "LA2",
    NA = "NA1",
    OCE = "OC1",
    TR = "TR1",
    RU = "RU",
    ME = "ME1",
    JP = "JP1",
    KR = "KR",
    PH = "PH2",
    TH = "TH2",
    TW2 = "TW2",
    VN = "VN2",
    SG2 = "SG2"

#return PUUID
def search_riot_id(str):
    gameName, tagLine = str.split("#")
    res = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={api_key}")
    if res.status_code != 200:
        raise Exception("Unable to get PUUID")
    data = res.json()
    return(data["puuid"])

# returns false if not in game, teamID if in live game
# works for not in live game
def is_live(puuid, region):
    res = requests.get(f"https://{region.value[0]}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={api_key}")
    print(f"https://{region.value[0]}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={api_key}")
    if res.status_code == 404:
        return False
    print(res.status_code)
    data = res.json()
    for player in data['participants']:
        if(player['puuid'] == puuid):
            return (player['teamId'], data["game_Id"])

async def match_data(matchID, region):
    router = ""
    if region in (Region.NA, Region.BR, Region.LAN, Region.LAS):
        router = "americas"
    elif region in (Region.KR, Region.JP):
        router = "asia"
    elif region in (Region.EUNE, Region.EUW, Region.ME, Region.TR, Region.RU):
        router = "europe"
    else:
        router = "sea"
    while res := requests.get(f"https://{router}.api.riotgames.com/lol/match/v5/matches/{region.value[0]}_{matchID}?api_key={api_key}"):
        if res.status_code == 200:
            break
        await asyncio.sleep(2 * 60)
    data = res.json()
    return data["info"]['participants']

# Returns false if user hasn't entered a game in an hour
async def game_loop(puuid, region):
    teamID = 200
    for i in range(3):
        await asyncio.sleep(20 * 60)
        teamID, matchId = is_live(puuid, region)
        if(teamID):
            break
    if(not teamID):
        return False
    members = await match_data(matchId, region)
    members = list(filter(lambda x: x['teamId'] == teamID, members))
    for member in members:
        print(member['riotIdGameName'])



# when /start is called, set an interval to call is_live 
# if is_live returns an integer within 3 runs, then move into the wait_for_end loop

# unschedule is_live and schedule wait_for_end
async def main():
    x = await match_data(5037352216, Region.NA)
    print(x)

asyncio.run(game_loop(1,1))