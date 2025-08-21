"""
Books Service gRPC Server
Implements async gRPC server with in-memory data storage
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import grpc
from grpc import aio

# Import generated protobuf classes
import books_pb2
import books_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BooksServicer(books_pb2_grpc.BooksServiceServicer):
    """
    Async gRPC servicer for Books Service
    Uses in-memory storage for Day 2 (we'll add DB on Day 3)
    """
    
    def __init__(self):
        # In-memory storage: book_id -> Book
        self.books: Dict[int, books_pb2.Book] = {}
        self.next_id = 1
        
        # Seed with sample data
        self._seed_data()
    
    def _seed_data(self):
        """Add some sample books for testing"""
        sample_books = [
            {
                "title": "The Python Handbook",
                "author": "Jane Doe",
                "isbn": "978-1234567890",
                "published_year": 2023,
                "genre": "Technology",
                "description": "A comprehensive guide to Python programming"
            },
            {
                "title": "Microservices Architecture",
                "author": "John Smith",
                "isbn": "978-0987654321",
                "published_year": 2022,
                "genre": "Technology",
                "description": "Building scalable distributed systems"
            },
            {
                "title": "The Great Adventure",
                "author": "Alice Johnson",
                "isbn": "978-1122334455",
                "published_year": 2021,
                "genre": "Fiction",
                "description": "An epic tale of discovery"
            }
        ]
        
        for book_data in sample_books:
            self._create_book_internal(**book_data)
    
    def _create_book_internal(self, title: str, author: str, isbn: str, 
                            published_year: int, genre: str, description: str) -> books_pb2.Book:
        """Internal method to create a book with proper timestamps"""
        now = Timestamp()
        now.GetCurrentTime()
        
        book = books_pb2.Book(
            id=self.next_id,
            title=title,
            author=author,
            isbn=isbn,
            published_year=published_year,
            genre=genre,
            description=description,
            created_at=now,
            updated_at=now
        )
        
        self.books[self.next_id] = book
        self.next_id += 1
        return book
    
    async def CreateBook(self, request: books_pb2.CreateBookRequest, 
                        context: grpc.aio.ServicerContext) -> books_pb2.CreateBookResponse:
        """Create a new book"""
        try:
            logger.info(f"Creating book: {request.title} by {request.author}")
            
            # Validate required fields
            if not request.title or not request.author:
                return books_pb2.CreateBookResponse(
                    success=False,
                    message="Title and author are required"
                )
            
            # Check for duplicate ISBN
            if request.isbn:
                for book in self.books.values():
                    if book.isbn == request.isbn:
                        return books_pb2.CreateBookResponse(
                            success=False,
                            message=f"Book with ISBN {request.isbn} already exists"
                        )
            
            # Create the book
            book = self._create_book_internal(
                title=request.title,
                author=request.author,
                isbn=request.isbn,
                published_year=request.published_year,
                genre=request.genre,
                description=request.description
            )
            
            logger.info(f"Book created with ID: {book.id}")
            return books_pb2.CreateBookResponse(
                book=book,
                success=True,
                message="Book created successfully"
            )
            
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            return books_pb2.CreateBookResponse(
                success=False,
                message=f"Internal error: {str(e)}"
            )
    
    async def GetBook(self, request: books_pb2.BookId, 
                     context: grpc.aio.ServicerContext) -> books_pb2.GetBookResponse:
        """Get a book by ID"""
        try:
            logger.info(f"Getting book with ID: {request.id}")
            
            book = self.books.get(request.id)
            if book:
                return books_pb2.GetBookResponse(book=book, found=True)
            else:
                return books_pb2.GetBookResponse(found=False)
                
        except Exception as e:
            logger.error(f"Error getting book: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def UpdateBook(self, request: books_pb2.UpdateBookRequest, 
                        context: grpc.aio.ServicerContext) -> books_pb2.UpdateBookResponse:
        """Update an existing book using field masks"""
        try:
            logger.info(f"Updating book with ID: {request.id}")
            
            book = self.books.get(request.id)
            if not book:
                return books_pb2.UpdateBookResponse(
                    success=False,
                    message=f"Book with ID {request.id} not found"
                )
            
            # If no field mask provided, update all non-empty fields (backward compatibility)
            if not request.update_mask.paths:
                logger.warning("No field mask provided, falling back to non-empty field updates")
                if request.book.title:
                    book.title = request.book.title
                if request.book.author:
                    book.author = request.book.author
                if request.book.isbn:
                    # Check for duplicate ISBN
                    if self._check_isbn_conflict(request.book.isbn, request.id):
                        return books_pb2.UpdateBookResponse(
                            success=False,
                            message=f"Book with ISBN {request.book.isbn} already exists"
                        )
                    book.isbn = request.book.isbn
                if request.book.published_year:
                    book.published_year = request.book.published_year
                if request.book.genre:
                    book.genre = request.book.genre
                if request.book.description:
                    book.description = request.book.description
            else:
                # Use field mask to update only specified fields
                for path in request.update_mask.paths:
                    if path == "title":
                        book.title = request.book.title
                    elif path == "author":
                        book.author = request.book.author
                    elif path == "isbn":
                        # Check for duplicate ISBN
                        if self._check_isbn_conflict(request.book.isbn, request.id):
                            return books_pb2.UpdateBookResponse(
                                success=False,
                                message=f"Book with ISBN {request.book.isbn} already exists"
                            )
                        book.isbn = request.book.isbn
                    elif path == "published_year":
                        book.published_year = request.book.published_year
                    elif path == "genre":
                        book.genre = request.book.genre
                    elif path == "description":
                        book.description = request.book.description
                    else:
                        logger.warning(f"Ignoring unknown field path: {path}")
            
            # Always update the timestamp when any field changes
            book.updated_at.GetCurrentTime()
            
            logger.info(f"Book {request.id} updated successfully")
            return books_pb2.UpdateBookResponse(
                book=book,
                success=True,
                message="Book updated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error updating book: {str(e)}")
            return books_pb2.UpdateBookResponse(
                success=False,
                message=f"Internal error: {str(e)}"
            )
    
    def _check_isbn_conflict(self, isbn: str, exclude_id: int) -> bool:
        """Check if ISBN already exists (excluding the book being updated)"""
        if not isbn:
            return False
        for book_id, book in self.books.items():
            if book_id != exclude_id and book.isbn == isbn:
                return True
        return False
    
    async def DeleteBook(self, request: books_pb2.BookId, 
                        context: grpc.aio.ServicerContext) -> books_pb2.DeleteBookResponse:
        """Delete a book by ID"""
        try:
            logger.info(f"Deleting book with ID: {request.id}")
            
            if request.id in self.books:
                del self.books[request.id]
                return books_pb2.DeleteBookResponse(
                    success=True,
                    message="Book deleted successfully"
                )
            else:
                return books_pb2.DeleteBookResponse(
                    success=False,
                    message=f"Book with ID {request.id} not found"
                )
                
        except Exception as e:
            logger.error(f"Error deleting book: {str(e)}")
            return books_pb2.DeleteBookResponse(
                success=False,
                message=f"Internal error: {str(e)}"
            )
    
    async def ListBooks(self, request: books_pb2.ListBooksRequest, 
                       context: grpc.aio.ServicerContext) -> books_pb2.ListBooksResponse:
        """List books with optional filtering and pagination"""
        try:
            logger.info(f"Listing books - limit: {request.limit}, offset: {request.offset}")
            
            # Start with all books
            books_list = list(self.books.values())
            
            # Apply filters
            if request.genre_filter:
                books_list = [b for b in books_list if request.genre_filter.lower() in b.genre.lower()]
            
            if request.author_filter:
                books_list = [b for b in books_list if request.author_filter.lower() in b.author.lower()]
            
            total_count = len(books_list)
            
            # Apply pagination
            start = request.offset if request.offset > 0 else 0
            end = start + request.limit if request.limit > 0 else len(books_list)
            paginated_books = books_list[start:end]
            
            return books_pb2.ListBooksResponse(
                books=paginated_books,
                total_count=total_count
            )
            
        except Exception as e:
            logger.error(f"Error listing books: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def GetAllBooks(self, request, context: grpc.aio.ServicerContext) -> books_pb2.ListBooksResponse:
        """Get all books without pagination"""
        try:
            logger.info("Getting all books")
            books_list = list(self.books.values())
            return books_pb2.ListBooksResponse(
                books=books_list,
                total_count=len(books_list)
            )
        except Exception as e:
            logger.error(f"Error getting all books: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")


async def serve():
    """Start the gRPC server"""
    # Create server
    server = aio.server()
    
    # Add our servicer
    books_pb2_grpc.add_BooksServiceServicer_to_server(BooksServicer(), server)
    
    # Configure server address
    listen_addr = '[::]:50052'
    server.add_insecure_port(listen_addr)
    
    # Start server
    logger.info(f"Starting Books gRPC server on {listen_addr}")
    await server.start()
    
    # Keep server running
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        await server.stop(grace=5)


if __name__ == '__main__':
    # Run the server
    asyncio.run(serve())