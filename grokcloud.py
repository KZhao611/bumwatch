import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()

def helper_ai_call(message):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are the tv caster of a gameshow called bumwatch which takes league games and announces who the losers are (worst stats). Make separate quips for least damage, least kills, least gold, least cs, most deaths, and the biggest bum. Include no stage cues.",
            },
            {
                "role": "user",
                "content": str(message),
            }
        ],
        model="llama3-8b-8192",
        max_tokens=400,
    )
    return response.choices[0].message.content

# sourced from gfg hehe
def most_frequent(List):
    dict = {}
    count, itm = 0, ''
    for item in reversed(List):
        dict[item] = dict.get(item, 0) + 1
        if dict[item] >= count :
            count, itm = dict[item], item
    return(itm)

def ai_call(message):
    min_damage = [member['totalDamageDealtToChampions'] for member in message]
    min_kills = [member['kills'] for member in message]
    min_gold = [member['goldEarned'] for member in message]
    min_cs = [member['neutralMinionsKilled'] + member['totalMinionsKilled'] for member in message]
    max_deaths = [member['deaths'] for member in message]

    min_damage = [(member['riotIdGameName'], member['totalDamageDealtToChampions']) for member in message if member['totalDamageDealtToChampions'] == min(min_damage)][0]
    min_kills = [(member['riotIdGameName'], member['kills']) for member in message if member['kills'] == min(min_kills)][0]
    min_gold = [(member['riotIdGameName'], member['goldEarned']) for member in message if member['goldEarned'] == min(min_gold)][0]
    min_cs = [(member['riotIdGameName'], member['neutralMinionsKilled'] + member['totalMinionsKilled']) for member in message if member['neutralMinionsKilled'] + member['totalMinionsKilled'] == min(min_cs)][0]
    max_deaths = [(member['riotIdGameName'], member['deaths']) for member in message if member['deaths'] == max(max_deaths)][0]

    winner = most_frequent([min_damage[0], min_kills[0], min_gold[0], min_cs[0], max_deaths[0]])

    message = f"""
Least Damage: {min_damage[0]} with {min_damage[1]} damage
Least Kills: {min_kills[0]} with {min_kills[1]} kills
Least Gold: {min_gold[0]} with {min_gold[1]} gold
Least CS: {min_cs[0]} with {min_cs[1]} cs
Most Deaths: {max_deaths[0]} with {max_deaths[1]} deaths
Biggest Bum: {winner}
                            """
    print(message)
    return helper_ai_call(message)

