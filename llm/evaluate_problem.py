import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get('openai_apikey'),
)
f = open("./llm/prompt/evaluate_problem.txt", "r")
prompt = f.read()
f.close()

def evaluate_problem(data):
    s = "[Problem]\n{}\n\n{}\n\n".format(data["problem"], data["example"])
    for i in range(len(data["answer"])):
        t = data["answer"][i]
        s += "Question {}. {}({} pts.)\n\nModel answer: {}\n\nStudent's answer: {}\n\n".format(
            i + 1,
            t["problem"],
            t["score"],
            t["model_answer"],
            t["student_answer"]
        )

    result = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a master at evaluating given software related problems and student's answer."
            },
            {
                "role": "user",
                "content": prompt % (s)
            },
        ]
    )
    return json.loads(result.choices[0].message.content)