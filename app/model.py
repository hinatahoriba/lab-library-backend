from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Date, ForeignKey, CHAR
from sqlalchemy.orm import relationship

from .database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Book(Base):
    __tablename__ = "books"

    isbn = Column(CHAR(13), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    num = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    student_books = relationship("StudentBook", back_populates="book")


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(20), primary_key=True, index=True)
    fullname = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    student_books = relationship("StudentBook", back_populates="student")


class StudentBook(Base):
    __tablename__ = "student_books"

    student_id = Column(String(20), ForeignKey("students.student_id"), primary_key=True)
    isbn = Column(CHAR(13), ForeignKey("books.isbn"), primary_key=True)
    rent_date = Column(Date, primary_key=True)
    return_date = Column(Date)

    student = relationship("Student", back_populates="student_books")
    book = relationship("Book", back_populates="student_books")
