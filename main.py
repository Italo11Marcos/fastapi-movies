from typing import Optional, List

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, Integer, String


app = FastAPI()

#SQLAlchemy
SQLALCHAMY_DATABASE_URL = 'sqlite:///./movie.db'

engine = create_engine(SQLALCHAMY_DATABASE_URL, connect_args={
                        "check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

#Será executado quando precisar de acesso ao BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A SQLAlchemny ORM Movie
class DBMovie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    sinopse = Column(String, nullable=True)
    year = Column(Integer)

Base.metadata.create_all(bind=engine)

#Pydantic
class Movie(BaseModel):
    id: int
    title: str
    sinopse: Optional[str] = None
    year: int

    class Config:
        orm_mode = True

# Methods for interacting with the database
def get_movie(db: Session, movie_id: int):
    return db.query(DBMovie).where(DBMovie.id == movie_id).first()

def get_movies(db: Session):
    return db.query(DBMovie).all()

def create_movie(db: Session, movie: Movie):
    db_movie = DBMovie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    return db_movie

def delete_movie(db: Session, movie_id: int):
    movie = db.query(DBMovie).where(DBMovie.id == movie_id).first()
    db.delete(movie)
    db.commit()
    return {'message':'Deleted'}


# Routes for interacting with the API
@app.post('/movies/', response_model=Movie)
def create_movies_view(movie: Movie, db: Session = Depends(get_db)):
    db_movie = create_movie(db, movie)
    return db_movie

@app.get('/movies/', response_model=List[Movie])
def get_movies_view(db: Session = Depends(get_db)):
    return get_movies(db)

@app.get('/movie/{movie_id}')
def get_movie_view(movie_id: int, db: Session = Depends(get_db)):
    return get_movie(db, movie_id)

@app.delete('/movie/{movie_id}')
def delete_movie_view(movie_id: int, db: Session = Depends(get_db)):
    return delete_movie(db, movie_id)