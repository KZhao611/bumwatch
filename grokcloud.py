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
                "content": "You are a TV caster of Bumwatch, which reports the stars based on the lowest performers. Make a funny quip for the star of each category, and crown a big winner for tonight.",
            },
            {
                "role": "user",
                "content": str(message),
            }
        ],
        model="llama3-8b-8192",
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
    min_cs = [member['totalMinionsKilled'] for member in message]
    max_deaths = [member['deaths'] for member in message]

    min_damage = [member['riotIdGameName'] for member in message if member['totalDamageDealtToChampions'] == min(min_damage)][0]
    min_kills = [member['riotIdGameName'] for member in message if member['kills'] == min(min_kills)][0]
    min_gold = [member['riotIdGameName'] for member in message if member['goldEarned'] == min(min_gold)][0]
    min_cs = [member['riotIdGameName'] for member in message if member['totalMinionsKilled'] == min(min_cs)][0]
    max_deaths = [member['riotIdGameName'] for member in message if member['deaths'] == max(max_deaths)][0]

    winner = most_frequent([min_damage, min_kills, min_gold, min_cs, max_deaths])

    message = stats_message = f"""
                                **Least Damage:** {min_damage}
                                **Least Kills:** {min_kills}
                                **Least Gold:** {min_gold}
                                **Least CS:** {min_cs}
                                **Most Deaths:** {max_deaths}
                                **Big Winner:** {winner}
                            """
    return message

