from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from .model import Book, Student, StudentBook

# ======== BOOKS ========

def get_books(db: Session):
    return db.query(Book).all()

def get_book(db: Session, isbn: str):
    return db.query(Book).filter(Book.isbn == isbn).first()

def create_book(db: Session, isbn: str, title: str, num: int = 0):
    if num < 0:
        raise ValueError("Initial inventory cannot be negative.")

    if get_book(db, isbn):
        raise ValueError("Book already exists.")

    db_book = Book(isbn=isbn, title=title, num=num)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, isbn: str, title: str = None, num: int = None):
    db_book = db.query(Book).filter(Book.isbn == isbn).first()
    if not db_book:
        return None
    if title:
        db_book.title = title
    if num is not None:
        if num < 0:
            raise ValueError("Inventory cannot be negative.")
        db_book.num = num
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, isbn: str):
    db_book = db.query(Book).filter(Book.isbn == isbn).first()
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book


# ======== STUDENTS ========

def get_students(db: Session):
    return db.query(Student).all()

def create_student(db: Session, student_id: str, fullname: str):
    if db.query(Student).filter(Student.student_id == student_id).first():
        raise ValueError("Student already exists.")

    db_student = Student(student_id=student_id, fullname=fullname)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


# ======== STUDENT_BOOKS ========

def rent_book(db: Session, student_id: str, isbn: str):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student not found.")

    book = db.query(Book).filter(Book.isbn == isbn).first()
    if not book:
        raise ValueError("Book not found.")
    if book.num <= 0:
        raise ValueError("Book is not available for rent.")

    existing_rental: Optional[StudentBook] = (
        db.query(StudentBook)
        .filter(
            StudentBook.student_id == student_id,
            StudentBook.isbn == isbn,
            StudentBook.return_date.is_(None),
        )
        .first()
    )
    if existing_rental:
        raise ValueError("Student already has an active rental for this book.")

    rental = StudentBook(
        student_id=student_id,
        isbn=isbn,
        rent_date=date.today(),
        return_date=None,
    )
    book.num -= 1

    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental

def return_book(db: Session, student_id: str, isbn: str):
    rental: Optional[StudentBook] = (
        db.query(StudentBook)
        .filter(
            StudentBook.student_id == student_id,
            StudentBook.isbn == isbn,
            StudentBook.return_date.is_(None),
        )
        .first()
    )
    if not rental:
        raise ValueError("Active rental record not found.")

    book = db.query(Book).filter(Book.isbn == isbn).first()
    if book:
        book.num += 1

    rental.return_date = date.today()
    db.commit()
    db.refresh(rental)
    return rental
