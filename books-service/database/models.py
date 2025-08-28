from datetime import datetime
from sqlalchemy import Column,Integer,String,DateTime, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Book(Base):

    '''
    Book model for database
    '''

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String(200), nullable=False, index=True)
    title = Column(String(200), nullable=False, index=True)
    isbn = Column(String(17), nullable=True, index=True)
    published_year = Column(Integer, nullable=True, index=True)
    genre = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now, nullable=False)

    __table_args__ = (
        Index('ix_books_title_author', 'title', 'author'),
        Index('ix_books-genre_year', 'genre', 'published_year'),
        Index('ix_books_search', 'title', 'author', 'genre'),
    )

def __repr__(self) :
    return f"<Book(id={self.id}, title='{self.title}', author ='{self.author}')>"


        
    
