from typing import Annotated
from fastapi import FastAPI, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import mysql.connector
from mysql.connector import Error

templates = Jinja2Templates(directory="templates")

app = FastAPI()

DB_USER = "todo"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_NAME = "todosdb"

def create_db_connection():
    try:
        connection = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)
        return connection
    except Error as e:
        print(f"Error: {e}")
        raise

def reset_auto_increment():
    connection = create_db_connection()
    cursor = connection.cursor()
    query = "ALTER TABLE todos AUTO_INCREMENT = 1"
    cursor.execute(query)
    connection.commit()

@app.get("/", response_class=HTMLResponse)
async def read_todos(request: Request):
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM todos;"
    cursor.execute(query)
    todos = cursor.fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

@app.post("/todos")
async def create_todo(todo: str = Form(...)):
    connection = create_db_connection()
    cursor = connection.cursor()
    query = "INSERT INTO todos (item, stat) VALUES (%s, %s)"
    data = (todo, "open")
    cursor.execute(query, data)
    connection.commit()
    return RedirectResponse(url="/?message=ToDo created successfully", status_code=302)

@app.post("/update_status/{todo_id}/{new_status}")
async def update_status(todo_id: int, new_status: str):
    connection = create_db_connection()
    cursor = connection.cursor()
    query = "UPDATE todos SET stat = %s WHERE id = %s"
    data = (new_status, todo_id)
    cursor.execute(query, data)
    connection.commit()
    return RedirectResponse(url=f"/?message=Status of ToDo {todo_id} updated to {new_status}", status_code=302)

@app.post("/delete_todo/{todo_id}")
async def delete_todo(todo_id: int):
    connection = create_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM todos WHERE id = %s"
    data = (todo_id,)
    cursor.execute(query, data)
    connection.commit()
    
    reset_auto_increment()  # Reset auto-increment after deleting a row
    
    return RedirectResponse(url=f"/?message=ToDo {todo_id} deleted successfully", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
