import datetime
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, Session,relationship
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List
from jose import JWTError,JWSError
from mysql.connector import Error
import mysql.connector

# Database URL - replace with your MySQL details
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
host_name = "localhost"
db_name = "fastapi_login"
user_name = "root"
user_password = "Dcb@4129"


connection = create_db_connection(host_name, db_name, user_name, user_password)

# Create the SQLAlchemy engine
engine = sqlalchemy.engine.create.create_engine(connection)

# Session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the ORM models
Base = declarative_base()

# FastAPI instance
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAlchemy model for the user form
class Event_create(Base):
    __tablename__="event"
    event_id=Column(Integer,primary_key=True)
class User_Form(Base):
    __tablename__ = "userform"

    event_id = relationship("Event_create",backref="userform",cascade="all, delete")
    event_name = Column(String, nullable=False)
    event_venue_address = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    attendee_typee = Column(String, nullable=False)  # Store as comma-separated string

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Pydantic model for request validation
class Create_form(BaseModel):
    event_name: str
    event_venue: str
    event_date: datetime.date
    attendee_typee: List[str]

    class Config:
        orm_mode = True

# API endpoint to create a new form entry
@app.post("/userforms/", response_model=Create_form)
def create_form(form: Create_form, db: Session = Depends(get_db)):
    db_form = User_Form(
        event_name=form.event_name,
        event_venue_address=form.event_venue,
        event_date=form.event_date,
        attendee_typee=",".join(form.attendee_typee)
    )
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return form