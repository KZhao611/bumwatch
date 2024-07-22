from dotenv import load_dotenv
import os
import requests
import asyncio
from enum import Enum
from grokcloud import ai_call

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
    res = requests.get(f"https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={api_key}")
    if res.status_code == 404:
        return (False, False)
    data = res.json()
    for player in data['participants']:
        if(player['puuid'] == puuid):
            return (player['teamId'], data['gameId'])

async def match_data(matchID, region):
    router = ""
    if region in (Region.NA.value[0], Region.BR.value[0], Region.LAN.value[0], Region.LAS.value[0]):
        router = "americas"
    elif region in (Region.KR.value[0], Region.JP.value[0]):
        router = "asia"
    elif region in (Region.EUNE.value[0], Region.EUW.value[0], Region.ME.value[0], Region.TR.value[0], Region.RU.value[0]):
        router = "europe"
    else:
        router = "sea"
    while not (res := requests.get(f"https://{router}.api.riotgames.com/lol/match/v5/matches/{region}_{matchID}?api_key={api_key}")):
        print("Waiting for game to end")
        await asyncio.sleep(2 * 60)
    data = res.json()
    return data['info']['participants']

# Returns false if user hasn't entered a game in an hour
async def game_loop(puuid, region):
    teamID = 100
    for i in range(3):
        teamID, matchId = is_live(puuid, region)
        if(teamID):
            break
        await asyncio.sleep(20 * 60)
    if(not teamID):
        return False
    print("Game found!")
    members = await match_data(matchId, region)
    members = list(filter(lambda x: x['teamId'] == teamID, members))
    filtered_stats = ['riotIdGameName', 'totalDamageDealtToChampions', 'kills', 'assists', 'deaths', 'goldEarned', 'neutralMinionsKilled', 'totalMinionsKilled', 'teamPosition']
    members = [
        {attr: item[attr] for attr in filtered_stats}        
        for item in members if item['teamPosition'] != 'UTILITY'
    ]
    # print(members)
    # print("Stats grabbed, calling ai")
    return ai_call(members)


# unschedule is_live and schedule wait_for_end

async def last_game(puuid,region):
    router = ""
    if region in (Region.NA.value[0], Region.BR.value[0], Region.LAN.value[0], Region.LAS.value[0]):
        router = "americas"
    elif region in (Region.KR.value[0], Region.JP.value[0]):
        router = "asia"
    elif region in (Region.EUNE.value[0], Region.EUW.value[0], Region.ME.value[0], Region.TR.value[0], Region.RU.value[0]):
        router = "europe"
    else:
        router = "sea"
    res = requests.get(f"https://{router}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={api_key}")
    data = res.json()
    # print(data[0])
    res = requests.get(f"https://{router}.api.riotgames.com/lol/match/v5/matches/{data[0]}?api_key={api_key}")
    data = res.json()
    members = data['info']['participants']
    members_blue = list(filter(lambda x: x['teamId'] == 100, members))
    # for member in members_blue:
    #     print(member['riotIdGameName'])
    right_team = False
    for member in members_blue:
        if(member['puuid'] == puuid):
            right_team = True
    if not right_team:
        members = list(filter(lambda x: x['teamId'] == 200, members))
    else:
        members = members_blue
    filtered_stats = ['riotIdGameName', 'totalDamageDealtToChampions', 'kills', 'assists', 'deaths', 'goldEarned', 'neutralMinionsKilled', 'totalMinionsKilled', 'teamPosition']
    members = [
        {attr: item[attr] for attr in filtered_stats}        
        for item in members if item['teamPosition'] != 'UTILITY'
    ]
    # print(human_call(members))
    return ai_call(members)
