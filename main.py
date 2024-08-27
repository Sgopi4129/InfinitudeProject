from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import mysql.connector
from mysql.connector import Error

# MySQL Database Connection
def create_db_connection(host_name, db_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            database=db_name,
            user=user_name,
            password=user_password
        )
        print("MySQL Database connection was successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

# FastAPI App
app = FastAPI()

# Security Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# MySQL Connection Parameters
host_name = "localhost"
db_name = "fastapi_login"
user_name = "root"
user_password = "Dcb@4129"

# Connect to MySQL
connection = create_db_connection(host_name, db_name, user_name, user_password)

# JWT Secret Key
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic Models
class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Utility Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# FastAPI Routes
@app.post("/register")
async def register(user: User):
    cursor = connection.cursor()
    query = "INSERT INTO users (email, password) VALUES (%s, %s)"
    cursor.execute(query, (user.email, user.password))
    connection.commit()
    cursor.close()
    return {"message": "User created successfully"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor.execute(query, (form_data.username, form_data.password))
    user = cursor.fetchone()
    cursor.close()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise "credentials_exception"
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return {"message": f"Hello, {email}"}

# Run the application
if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)