import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get('openai_apikey'),
)
f = open("./llm/prompt/make_problem.txt", "r")
prompt = f.read()
f.close()

def make_problem(intention: str, score: int):
    result = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a master at creating software related problems with the best quality in the world!"
            },
            {
                "role": "user",
                "content": prompt % (intention, score, score, score // 2)
            },
        ]
    )
    return json.loads(result.choices[0].message.content)