import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI()

# ---------------------------------------------------------------------------
# Auth configuration
# ---------------------------------------------------------------------------

SECRET_KEY = "test-secret-key-do-not-use-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------------------------------------------------------------------
# In-memory stores
# ---------------------------------------------------------------------------

users_db: dict = {}  # key: username, value: {username, hashed_password, user_id}
todos_db: dict = {}  # key: todo id,  value: {id, title, completed, user_id}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class UserRegister(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    username: str
    user_id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class Todo(BaseModel):
    id: str
    title: str
    completed: bool = False
    user_id: str


class TodoCreate(BaseModel):
    title: str


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------


@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    user_id = str(uuid.uuid4())
    users_db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "user_id": user_id,
    }
    return {"username": user.username, "user_id": user_id}


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Todo endpoints (all protected)
# ---------------------------------------------------------------------------


@app.get("/todos")
def get_todos(current_user: dict = Depends(get_current_user)):
    return [t for t in todos_db.values() if t["user_id"] == current_user["user_id"]]


@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate, current_user: dict = Depends(get_current_user)):
    todo_id = str(uuid.uuid4())
    new_todo = {
        "id": todo_id,
        "title": todo.title,
        "completed": False,
        "user_id": current_user["user_id"],
    }
    todos_db[todo_id] = new_todo
    return new_todo


@app.get("/todos/{todo_id}")
def get_todo(todo_id: str, current_user: dict = Depends(get_current_user)):
    todo = todos_db.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorised to access this todo")
    return todo


@app.put("/todos/{todo_id}")
def update_todo(todo_id: str, updates: TodoUpdate, current_user: dict = Depends(get_current_user)):
    todo = todos_db.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorised to update this todo")
    if updates.title is not None:
        todo["title"] = updates.title
    if updates.completed is not None:
        todo["completed"] = updates.completed
    todos_db[todo_id] = todo
    return todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str, current_user: dict = Depends(get_current_user)):
    todo = todos_db.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorised to delete this todo")
    del todos_db[todo_id]
