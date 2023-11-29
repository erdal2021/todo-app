from typing import Union, Annotated
from fastapi import FastAPI, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import mysql
import mysql.connector
from mysql.connector import Error

templates = Jinja2Templates(directory="templates")

app = FastAPI()

DB_USER = "todo"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_NAME = "todosdb"

def create_db_connection():
    connection = mysql.connector.connect(user=DB_USER,password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)
    return connection

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html",
                                        {"request": request})

@app.get("/todos", response_class=HTMLResponse)
def get_todos(request: Request, todo: Annotated[str, Form()]):
    connection = create_db_connection()
    cursor = connection.cursor()
    query = "SELECT item, stat FROM todos;"
    cursor.execute(query)
    todos = cursor.fetchall()    
    senderid = todo
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos, "senderid": senderid})


@app.post("/todos")
def post_todos(response: Response, todo: Annotated[str, Form()]):
    connection = create_db_connection()
    cursor = connection.cursor()
    query = "INSERT INTO todos (item, stat) VALUES (%s, %s)"
    data = (todo, "open")
    cursor.execute(query, data)
    connection.commit()
    response = RedirectResponse(url="http://localhost:8000/", status_code=302)
    return response

    print(todo)