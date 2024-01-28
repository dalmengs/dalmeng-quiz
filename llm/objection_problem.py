import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get('openai_apikey'),
)
f = open("./llm/prompt/objection_problem.txt", "r")
prompt = f.read()
f.close()

def objection_problem(data):
    p = "{}\n\n{}\n\n{} ({}점)\n".format(data["problem"], data["example"], data["sub_problem"], data["score"])
    result = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a bot responsible for handling appeals from students who have solved this problem."
            },
            {
                "role": "user",
                "content": prompt % (p, data["model_answer"], data["student_answer"], data["evaluation"], data["student_score"],
                   data["appeal_details"])
            },
        ]
    )
    return json.loads(result.choices[0].message.content)