from database.repository import *
from llm.evaluate_problem import evaluate_problem
from llm.make_problem import make_problem
from llm.objection_problem import objection_problem
from fastapi import FastAPI
from fastapi import Request
import traceback
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

templates = Jinja2Templates(directory="templates") 
app = FastAPI()
app.mount("/font", StaticFiles(directory="font"), name="font") 
create_table()

@app.get("/problem/create", response_class=HTMLResponse)
def problem_make_page(request: Request):
    return templates.TemplateResponse("problem_make_page.html", {"request": request})

class Problem(BaseModel):
   topic: str

@app.post("/problem/create")
def problem_make(problem: Problem):
    try:
        SCORE = 20
        result = make_problem(problem.topic, SCORE)
        problem_id = insert_problem(result["problem"], result["example"], float(SCORE), result["sub_problem"])
        return {"problem_id": problem_id}
    except Exception as e:
        traceback.print_exc()

@app.get("/problem/{problem_id}")
def problem_page(request: Request, problem_id: int):
    res = find_problem_with_id(problem_id)
    return templates.TemplateResponse("problem_page.html", {"request": request, "data": res})

class Submit(BaseModel):
   answer: list
   problem_id: int

@app.post("/problem/submit")
def problem_submit(submit: Submit):
    try:
        res = find_problem_with_id(submit.problem_id)

        sp = []
        for i in res["sub_problem"]:
            sp.append({
                "problem": i["problem"],
                "score": i["score"],
                "model_answer": i["answer"],
                "student_answer": submit.answer[len(sp)]
            })

        result = evaluate_problem({
            "problem": res["problem"],
            "example": res["example"],
            "answer": sp
        })

        submit_id = insert_submit(result["result"], submit.answer, submit.problem_id)
        print(submit_id)
        return {"submit_id": submit_id}
        
        
    except Exception as e:
        traceback.print_exc()

@app.get("/submit/{submit_id}")
def submit_page(request: Request, submit_id: str):
    res = find_submit_with_submit_id(submit_id)
    return templates.TemplateResponse("submit_check_page.html", {"request": request, "data": res})

@app.get("/problem")
def problem_list_page(request: Request):
    res = find_all_problem()
    return templates.TemplateResponse("problem_list_page.html", {"request": request, "data": res})

@app.get("/submit")
def submit_list_page(request: Request):
    res = find_all_submit()
    return templates.TemplateResponse("submit_list_page.html", {"request": request, "data": res})

@app.get("/")
def main_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})