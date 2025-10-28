from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, conint, constr
from sqlalchemy.orm import Session

from . import crud, model
from .database import SessionLocal, engine

model.Base.metadata.create_all(bind=engine)

app = FastAPI()


# ======== Pydantic Schemas ========

class BookCreate(BaseModel):
    isbn: constr(min_length=13, max_length=13)
    title: str
    num: conint(ge=0) = 0


class BookUpdate(BaseModel):
    title: str | None = None
    num: conint(ge=0) | None = None


class StudentCreate(BaseModel):
    student_id: str
    fullname: str


class RentalRequest(BaseModel):
    student_id: str
    isbn: constr(min_length=13, max_length=13)


# ======== DB接続依存関数 ========

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======== BOOKS ========

@app.get("/books")
def read_books(db: Session = Depends(get_db)):
    return crud.get_books(db)


@app.post("/books", status_code=201)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_book(db, payload.isbn, payload.title, payload.num)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/books/{isbn}")
def update_book(isbn: str, payload: BookUpdate, db: Session = Depends(get_db)):
    try:
        book = crud.update_book(db, isbn, payload.title, payload.num)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.delete("/books/{isbn}", status_code=204)
def delete_book(isbn: str, db: Session = Depends(get_db)):
    book = crud.delete_book(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return None


# ======== STUDENTS ========

@app.get("/students")
def read_students(db: Session = Depends(get_db)):
    return crud.get_students(db)


@app.post("/students", status_code=201)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db, payload.student_id, payload.fullname)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ======== RENTAL ========

@app.post("/rentals/rent", status_code=201)
def rent_book(request: RentalRequest, db: Session = Depends(get_db)):
    try:
        return crud.rent_book(db, request.student_id, request.isbn)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rentals/return")
def return_book(request: RentalRequest, db: Session = Depends(get_db)):
    try:
        return crud.return_book(db, request.student_id, request.isbn)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
