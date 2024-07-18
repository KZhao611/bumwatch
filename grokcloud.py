import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()

def ai_call(message):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a TV caster of Bumwatch, which reports the stars based on the lowest performers. Make categories for least damage, least gold, least CS (minions), least kills, most deaths. Surround the title of each category with **. Follow up each category with a witty quip.",
            },
            {
                "role": "user",
                "content": message,
            }
        ],
        model="llama3-8b-8192",
    )
    return response.choices[0].message.content