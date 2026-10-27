from datetime import datetime, date

class Book:
    """Represents a book in the library system."""
    def __init__(self, title, author, isbn, total_copies=1, available_copies=1, book_id=None):
        self.id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.total_copies = int(total_copies)
        self.available_copies = int(available_copies)

    def is_available(self):
        """Checks if there are copies available for borrowing."""
        return self.available_copies > 0

    def borrow_copy(self):
        """Decrements available copies when a book is loaned."""
        if not self.is_available():
            raise ValueError(f"No available copies left for '{self.title}'.")
        self.available_copies -= 1

    def return_copy(self):
        """Increments available copies when a book is returned."""
        if self.available_copies >= self.total_copies:
            raise ValueError(f"Available copies cannot exceed total copies.")
        self.available_copies += 1

    def to_dict(self):
        """Serializes the object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "is_available": self.is_available()
        }


class Member:
    """Represents a library user (Student/Member or Librarian)."""
    def __init__(self, name, email, role="member", member_id=None):
        self.id = member_id
        self.name = name
        self.email = email
        self.role = role  # 'member' or 'librarian'

    def is_librarian(self):
        """Checks if the user has librarian administrative privileges."""
        return self.role == "librarian"

    def to_dict(self):
        """Serializes the member object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_librarian": self.is_librarian()
        }


class Loan:
    """Manages loan transactions and overdue tracking."""
    def __init__(self, member_id, book_id, loan_date, due_date, return_date=None, status="active", loan_id=None):
        self.id = loan_id
        self.member_id = member_id
        self.book_id = book_id
        self.loan_date = loan_date
        self.due_date = due_date
        self.return_date = return_date
        self.status = status  # 'active', 'returned', 'overdue'

    def is_overdue(self, current_date=None):
        """Checks if the loan is past due date and not yet returned."""
        if self.status == "returned":
            return False
        
        check_date = current_date or date.today()
        if isinstance(self.due_date, str):
            due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
        else:
            due = self.due_date

        return check_date > due


class Notification:
    """Represents simulated e-mail notification logs."""
    def __init__(self, loan_id, member_id, book_id, due_date, message_text, date_created, status="simulated_sent", notification_id=None):
        self.id = notification_id
        self.loan_id = loan_id
        self.member_id = member_id
        self.book_id = book_id
        self.due_date = due_date
        self.message_text = message_text
        self.date_created = date_created
        self.status = status  # 'simulated_sent'

    def to_dict(self):
        """Serializes notification log data."""
        return {
            "id": self.id,
            "loan_id": self.loan_id,
            "member_id": self.member_id,
            "book_id": self.book_id,
            "due_date": str(self.due_date),
            "message_text": self.message_text,
            "date_created": str(self.date_created),
            "status": self.status
        }