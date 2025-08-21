"""
Simple gRPC client to test the Books Service
"""

import asyncio
import grpc
from grpc import aio
import books_pb2
import books_pb2_grpc
from google.protobuf import empty_pb2


async def test_books_service():
    """Test all gRPC endpoints"""
    
    # Connect to server
    async with aio.insecure_channel('localhost:50052') as channel:
        # Create client stub
        client = books_pb2_grpc.BooksServiceStub(channel)
        
        print("=== Testing Books gRPC Service ===\n")
        
        # 1. List all existing books (seeded data)
        print("1. Getting all books:")
        response = await client.GetAllBooks(empty_pb2.Empty())
        for book in response.books:
            print(f"   ID: {book.id}, Title: {book.title}, Author: {book.author}")
        print()
        
        # 2. Get a specific book
        print("2. Getting book with ID 1:")
        response = await client.GetBook(books_pb2.BookId(id=1))
        if response.found:
            book = response.book
            print(f"   Found: {book.title} by {book.author} ({book.genre})")
        else:
            print("   Book not found")
        print()
        
        # 3. Create a new book
        print("3. Creating a new book:")
        create_request = books_pb2.CreateBookRequest(
            title="gRPC in Action",
            author="Tech Writer",
            isbn="978-1111111111",
            published_year=2024,
            genre="Technology",
            description="Learn gRPC with practical examples"
        )
        response = await client.CreateBook(create_request)
        if response.success:
            print(f"   Created: {response.book.title} with ID {response.book.id}")
        else:
            print(f"   Failed: {response.message}")
        print()
        
        # 4. Update the new book using field mask
        print("4. Updating the new book with field mask:")
        if response.success:
            book_id = response.book.id
            # Create field mask for partial update
            from google.protobuf.field_mask_pb2 import FieldMask
            
            # Only update description and genre
            field_mask = FieldMask()
            field_mask.paths.extend(["description", "genre"])
            
            # Create the book with updated values
            updated_book = books_pb2.Book()
            updated_book.description = "Updated: Learn gRPC with hands-on examples and best practices"
            updated_book.genre = "Programming"
            
            update_request = books_pb2.UpdateBookRequest(
                id=book_id,
                book=updated_book,
                update_mask=field_mask
            )
            response = await client.UpdateBook(update_request)
            if response.success:
                print(f"   Updated book {book_id}:")
                print(f"   - Description: {response.book.description}")
                print(f"   - Genre: {response.book.genre}")
                print(f"   - Title unchanged: {response.book.title}")
            else:
                print(f"   Update failed: {response.message}")
        print()
        
        # 5. List books with filter
        print("5. Listing Technology books:")
        list_request = books_pb2.ListBooksRequest(
            genre_filter="Technology",
            limit=10
        )
        response = await client.ListBooks(list_request)
        print(f"   Found {response.total_count} technology books:")
        for book in response.books:
            print(f"   - {book.title} by {book.author}")
        print()
        
        # 6. Test error case - get non-existent book
        print("6. Testing error case - get book ID 999:")
        response = await client.GetBook(books_pb2.BookId(id=999))
        if response.found:
            print(f"   Unexpected: Found book {response.book.title}")
        else:
            print("   Correctly returned 'not found'")
        print()
        
        print("=== All tests completed ===")


if __name__ == '__main__':
    asyncio.run(test_books_service())