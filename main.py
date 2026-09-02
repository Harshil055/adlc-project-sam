"""
Simple Todo API for testing ADLC platform
FastAPI application with CRUD operations
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Todo API", version="1.0.0")

# In-memory storage
todos_db = {}
todo_id_counter = 1

# Models
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None

class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"
    created_at: datetime
    updated_at: datetime

# Routes
@app.get("/")
def root():
    return {"message": "Todo API is running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    global todo_id_counter
    now = datetime.utcnow()
    new_todo = Todo(
        id=todo_id_counter,
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
        created_at=now,
        updated_at=now
    )
    todos_db[todo_id_counter] = new_todo
    todo_id_counter += 1
    return new_todo

@app.get("/todos", response_model=List[Todo])
def list_todos(completed: Optional[bool] = None):
    todos = list(todos_db.values())
    if completed is not None:
        todos = [t for t in todos if t.completed == completed]
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos_db[todo_id]

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo = todos_db[todo_id]
    if todo_update.title is not None:
        todo.title = todo_update.title
    if todo_update.description is not None:
        todo.description = todo_update.description
    if todo_update.completed is not None:
        todo.completed = todo_update.completed
    if todo_update.priority is not None:
        todo.priority = todo_update.priority
    todo.updated_at = datetime.utcnow()
    return todo

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos_db[todo_id]
