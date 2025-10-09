"""
Система управления библиотекой
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
import re


class BookNotAvailableError(Exception):
    """Исключение когда книга недоступна для выдачи"""
    pass


class ReaderNotFoundError(Exception):
    """Исключение когда читатель не найден в системе"""
    pass


class Book:
    """Класс представляющий книгу в библиотеке"""
    
    def __init__(self, isbn: str, title: str, author: str, year: int, 
                 total_copies: int, available_copies: int = None):
        """
        Инициализация книги
        
        Args:
            isbn: ISBN книги
            title: Название книги
            author: Автор книги
            year: Год издания
            total_copies: Общее количество копий
            available_copies: Доступные копии (по умолчанию равно total_copies)
        """
        if not isbn:
            raise ValueError("ISBN cannot be empty")
        if not title:
            raise ValueError("Title cannot be empty")
        if not author:
            raise ValueError("Author cannot be empty")
        if year < 1000 or year > datetime.now().year:
            raise ValueError("Invalid year")
        if total_copies < 0:
            raise ValueError("Copies cannot be negative")
        
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.total_copies = total_copies
        self.available_copies = available_copies if available_copies is not None else total_copies
        
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
    
    def is_available(self) -> bool:
        """Проверяет доступна ли книга для выдачи"""
        return self.available_copies > 0
    
    def borrow(self) -> bool:
        """
        Выдает книгу (уменьшает количество доступных копий)
        
        Returns:
            True если книга успешно выдана, False если нет доступных копий
        """
        if self.is_available():
            self.available_copies -= 1
            return True
        return False
    
    def return_book(self) -> bool:
        """
        Возвращает книгу (увеличивает количество доступных копий)
        
        Returns:
            True если книга успешно возвращена, False если все копии уже возвращены
        """
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False
    
    def __str__(self) -> str:
        return f"'{self.title}' by {self.author} ({self.year})"
    
    def __repr__(self) -> str:
        return f"Book(isbn='{self.isbn}', title='{self.title}', available={self.available_copies}/{self.total_copies})"


class Reader:
    """Класс представляющий читателя библиотеки"""
    
    MAX_BOOKS = 5  # Максимальное количество книг, которые можно взять одновременно
    
    def __init__(self, reader_id: str, name: str, email: str):
        """
        Инициализация читателя
        
        Args:
            reader_id: Уникальный идентификатор читателя
            name: Имя читателя
            email: Email читателя
        """
        if not reader_id:
            raise ValueError("Reader ID cannot be empty")
        if not name:
            raise ValueError("Name cannot be empty")
        # Улучшенная валидация email
        if not email or '@' not in email or '.' not in email or email.startswith('@') or email.endswith('.'):
            raise ValueError("Invalid email")
        
        # Дополнительная проверка: после @ должна быть точка и домен
        email_parts = email.split('@')
        if len(email_parts) != 2 or '.' not in email_parts[1] or email_parts[1].startswith('.') or email_parts[1].endswith('.'):
            raise ValueError("Invalid email")
        
        self.reader_id = reader_id
        self.name = name
        self.email = email
        self.borrowed_books: Set[str] = set()  # ISBN взятых книг
        self.history: List[Tuple[datetime, str]] = []  # История операций
    
    def can_borrow(self) -> bool:
        """Проверяет может ли читатель взять еще книгу"""
        return len(self.borrowed_books) < self.MAX_BOOKS
    
    def add_borrowed_book(self, isbn: str) -> bool:
        """
        Добавляет книгу в список взятых
        
        Args:
            isbn: ISBN книги
            
        Returns:
            True если книга успешно добавлена, False если достигнут лимит или книга уже взята
        """
        if not self.can_borrow():
            return False
        
        if isbn in self.borrowed_books:
            return False
        
        self.borrowed_books.add(isbn)
        self.history.append((datetime.now(), f"borrowed {isbn}"))
        return True
    
    def remove_borrowed_book(self, isbn: str) -> bool:
        """
        Удаляет книгу из списка взятых
        
        Args:
            isbn: ISBN книги
            
        Returns:
            True если книга успешно удалена, False если книги не было в списке
        """
        if isbn in self.borrowed_books:
            self.borrowed_books.remove(isbn)
            self.history.append((datetime.now(), f"returned {isbn}"))
            return True
        return False
    
    def __str__(self) -> str:
        return f"Reader {self.name} ({self.reader_id})"
    
    def __repr__(self) -> str:
        return f"Reader(reader_id='{self.reader_id}', name='{self.name}', borrowed={len(self.borrowed_books)})"


class Library:
    """Основной класс управления библиотекой"""
    
    LOAN_PERIOD_DAYS = 14  # Период выдачи книг в днях
    FINE_PER_DAY = 10.0    # Штраф за день просрочки
    
    def __init__(self, name: str):
        """
        Инициализация библиотеки
        
        Args:
            name: Название библиотеки
        """
        if not name:
            raise ValueError("Library name cannot be empty")
        
        self.name = name
        self.books: Dict[str, Book] = {}  # ISBN -> Book
        self.readers: Dict[str, Reader] = {}  # reader_id -> Reader
        self.active_loans: Dict[str, Dict[str, Dict]] = {}  # reader_id -> {isbn -> loan_info}
        self.borrow_history: List[Dict] = []  # История всех выдач
    
    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int) -> bool:
        """
        Добавляет книгу в библиотеку
        
        Args:
            isbn: ISBN книги
            title: Название книги
            author: Автор книги
            year: Год издания
            copies: Количество копий
            
        Returns:
            True если книга добавлена, False в случае ошибки
        """
        try:
            if isbn in self.books:
                # Увеличиваем количество копий существующей книги
                existing_book = self.books[isbn]
                existing_book.total_copies += copies
                existing_book.available_copies += copies
            else:
                # Создаем новую книгу
                self.books[isbn] = Book(isbn, title, author, year, copies, copies)
            return True
        except (ValueError, TypeError):
            return False
    
    def register_reader(self, reader_id: str, name: str, email: str) -> bool:
        """
        Регистрирует нового читателя
        
        Args:
            reader_id: Уникальный идентификатор читателя
            name: Имя читателя
            email: Email читателя
            
        Returns:
            True если читатель зарегистрирован, False если reader_id уже существует
        """
        if reader_id in self.readers:
            return False
        
        try:
            self.readers[reader_id] = Reader(reader_id, name, email)
            self.active_loans[reader_id] = {}
            return True
        except (ValueError, TypeError):
            return False
    
    def find_books_by_author(self, author: str) -> List[Book]:
        """
        Находит книги по автору (регистронезависимый поиск)
        
        Args:
            author: Имя автора для поиска
            
        Returns:
            Список найденных книг
        """
        author_lower = author.lower()
        return [book for book in self.books.values() 
                if author_lower in book.author.lower()]
    
    def find_books_by_title(self, title: str) -> List[Book]:
        """
        Находит книги по названию (регистронезависимый поиск)
        
        Args:
            title: Название для поиска
            
        Returns:
            Список найденных книг
        """
        title_lower = title.lower()
        return [book for book in self.books.values() 
                if title_lower == book.title.lower()]
    
    def get_available_books(self) -> List[Book]:
        """
        Возвращает список доступных книг
        
        Returns:
            Список доступных книг
        """
        return [book for book in self.books.values() if book.is_available()]
    
    def borrow_book(self, reader_id: str, isbn: str) -> Tuple[bool, str]:
        """
        Выдает книгу читателю
        
        Args:
            reader_id: ID читателя
            isbn: ISBN книги
            
        Returns:
            Кортеж (успех, сообщение)
        """
        # Проверяем существование читателя
        if reader_id not in self.readers:
            raise ReaderNotFoundError(f"Reader {reader_id} not found")
        
        reader = self.readers[reader_id]
        
        # Проверяем существование книги
        if isbn not in self.books:
            return False, f"Book with ISBN {isbn} not found"
        
        book = self.books[isbn]
        
        # Проверяем доступность книги
        if not book.is_available():
            raise BookNotAvailableError(f"Book {isbn} is not available")
        
        # Проверяем лимит книг у читателя
        if not reader.can_borrow():
            return False, f"Reader has reached the maximum limit of {reader.MAX_BOOKS} books"
        
        # Проверяем, не взял ли читатель уже эту книгу
        if isbn in reader.borrowed_books:
            return False, f"Reader has already borrowed this book"
        
        # Выдаем книгу
        if book.borrow() and reader.add_borrowed_book(isbn):
            # Записываем информацию о выдаче
            loan_info = {
                'borrow_date': datetime.now(),
                'return_date': datetime.now() + timedelta(days=self.LOAN_PERIOD_DAYS),
                'returned': False
            }
            self.active_loans[reader_id][isbn] = loan_info
            
            # Добавляем в историю
            self.borrow_history.append({
                'reader_id': reader_id,
                'isbn': isbn,
                'borrow_date': loan_info['borrow_date'],
                'return_date': loan_info['return_date']
            })
            
            return True, f"Book '{book.title}' successfully borrowed by {reader.name}"
        
        return False, "Failed to borrow book"
    
    def return_book(self, reader_id: str, isbn: str) -> Tuple[bool, float]:
        """
        Возвращает книгу в библиотеку
        
        Args:
            reader_id: ID читателя
            isbn: ISBN книги
            
        Returns:
            Кортеж (успех, штраф)
        """
        # Проверяем существование читателя
        if reader_id not in self.readers:
            raise ReaderNotFoundError(f"Reader {reader_id} not found")
        
        reader = self.readers[reader_id]
        
        # Проверяем существование книги
        if isbn not in self.books:
            return False, 0.0
        
        # Проверяем, брал ли читатель эту книгу
        if isbn not in reader.borrowed_books:
            return False, 0.0
        
        book = self.books[isbn]
        
        # Рассчитываем штраф перед возвратом
        fine = self.calculate_fine(reader_id, isbn)
        
        # Возвращаем книгу
        if book.return_book() and reader.remove_borrowed_book(isbn):
            # Удаляем запись из активных займов
            if reader_id in self.active_loans and isbn in self.active_loans[reader_id]:
                del self.active_loans[reader_id][isbn]
            
            return True, fine
        
        return False, 0.0
    
    def calculate_fine(self, reader_id: str, isbn: str) -> float:
        """
        Рассчитывает штраф за просрочку
        
        Args:
            reader_id: ID читателя
            isbn: ISBN книги
            
        Returns:
            Сумма штрафа
        """
        if (reader_id not in self.active_loans or 
            isbn not in self.active_loans[reader_id]):
            return 0.0
        
        loan_info = self.active_loans[reader_id][isbn]
        return_date = loan_info['return_date']
        current_date = datetime.now()
        
        if current_date <= return_date:
            return 0.0
        
        overdue_days = (current_date - return_date).days
        return overdue_days * self.FINE_PER_DAY
    
    def get_overdue_loans(self) -> List[Dict]:
        """
        Возвращает список просроченных займов
        
        Returns:
            Список информации о просроченных займах
        """
        overdue_loans = []
        current_date = datetime.now()
        
        for reader_id, loans in self.active_loans.items():
            for isbn, loan_info in loans.items():
                if not loan_info.get('returned', False) and current_date > loan_info['return_date']:
                    overdue_loans.append({
                        'reader_id': reader_id,
                        'book_isbn': isbn,
                        'reader_name': self.readers[reader_id].name,
                        'book_title': self.books[isbn].title,
                        'return_date': loan_info['return_date'],
                        'overdue_days': (current_date - loan_info['return_date']).days
                    })
        
        return overdue_loans
    
    def get_reader_stats(self, reader_id: str) -> Dict:
        """
        Возвращает статистику читателя
        
        Args:
            reader_id: ID читателя
            
        Returns:
            Словарь со статистикой
        """
        if reader_id not in self.readers:
            raise ReaderNotFoundError(f"Reader {reader_id} not found")
        
        reader = self.readers[reader_id]
        
        # Считаем общее количество взятых книг из истории
        total_borrowed = len([record for record in reader.history 
                             if 'borrowed' in record[1]])
        
        return {
            'reader_id': reader_id,
            'name': reader.name,
            'email': reader.email,
            'currently_borrowed': len(reader.borrowed_books),
            'total_borrowed': total_borrowed,
            'registration_date': min([record[0] for record in reader.history]) if reader.history else None
        }
    
    def get_popular_books(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Возвращает самые популярные книги
        
        Args:
            limit: Количество книг в рейтинге
            
        Returns:
            Список кортежей (ISBN, количество выдач)
        """
        borrow_count = {}
        
        for record in self.borrow_history:
            isbn = record['isbn']
            borrow_count[isbn] = borrow_count.get(isbn, 0) + 1
        
        # Сортируем по количеству выдач (по убыванию)
        sorted_books = sorted(borrow_count.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_books[:limit]
    
    def __str__(self) -> str:
        return f"Library '{self.name}' with {len(self.books)} books and {len(self.readers)} readers"