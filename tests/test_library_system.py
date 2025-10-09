"""
Тесты для системы управления библиотекой
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Добавляем путь к src для импорта
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from library_system import (
    Book, Reader, Library,
    BookNotAvailableError, ReaderNotFoundError
)

@pytest.fixture
def sample_book():
    """Фикстура для создания тестовой книги"""
    return Book("978-0-13-475759-9", "Clean Code", "Robert Martin", 2008, 5, 5)

@pytest.fixture
def sample_reader():
    """Фикстура для создания тестового читателя"""
    return Reader("R001", "John Doe", "john.doe@email.com")

@pytest.fixture
def empty_library():
    """Фикстура для создания пустой библиотеки"""
    return Library("City Library")

@pytest.fixture
def library_with_data():
    """Фикстура для создания библиотеки с предзаполненными данными"""
    library = Library("City Library")
    
    # Добавляем книги
    library.add_book("978-0-13-475759-9", "Clean Code", "Robert Martin", 2008, 3)
    library.add_book("978-0-13-595705-9", "The Clean Coder", "Robert Martin", 2011, 2)
    library.add_book("978-0-321-71289-1", "Design Patterns", "Erich Gamma", 1994, 4)
    library.add_book("978-1-491-90387-4", "Python Crash Course", "Eric Matthes", 2015, 5)
    
    # Регистрируем читателей
    library.register_reader("R001", "Alice Smith", "alice@email.com")
    library.register_reader("R002", "Bob Johnson", "bob@email.com")
    
    return library


# ============= ТЕСТЫ КЛАССА BOOK =============

class TestBook:
    """Тесты для класса Book"""
    
    def test_should_create_book_with_valid_data(self):
        """Корректное создание объекта книги с валидными данными"""
        book = Book("978-0-13-475759-9", "Clean Code", "Robert Martin", 2008, 5, 5)
        
        assert book.isbn == "978-0-13-475759-9"
        assert book.title == "Clean Code"
        assert book.author == "Robert Martin"
        assert book.year == 2008
        assert book.total_copies == 5
        assert book.available_copies == 5
    
    @pytest.mark.parametrize("isbn", ["", None])
    def test_should_raise_error_for_empty_isbn(self, isbn):
        """Валидация: пустой ISBN должен вызывать ValueError"""
        with pytest.raises(ValueError, match="ISBN cannot be empty"):
            Book(isbn, "Title", "Author", 2020, 1, 1)
    
    @pytest.mark.parametrize("title", ["", None])
    def test_should_raise_error_for_empty_title(self, title):
        """Валидация: пустое название должно вызывать ValueError"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Book("978-0-13-475759-9", title, "Author", 2020, 1, 1)
    
    @pytest.mark.parametrize("author", ["", None])
    def test_should_raise_error_for_empty_author(self, author):
        """Валидация: пустой автор должен вызывать ValueError"""
        with pytest.raises(ValueError, match="Author cannot be empty"):
            Book("978-0-13-475759-9", "Title", author, 2020, 1, 1)
    
    @pytest.mark.parametrize("year", [999, 2030, -100, 0])
    def test_should_raise_error_for_invalid_year(self, year):
        """Валидация: некорректный год должен вызывать ValueError"""
        with pytest.raises(ValueError, match="Invalid year"):
            Book("978-0-13-475759-9", "Title", "Author", year, 1, 1)
    
    @pytest.mark.parametrize("copies", [-1, -5])
    def test_should_raise_error_for_negative_copies(self, copies):
        """Валидация: отрицательное количество копий должно вызывать ValueError"""
        with pytest.raises(ValueError, match="Copies cannot be negative"):
            Book("978-0-13-475759-9", "Title", "Author", 2020, copies, copies)
    
    def test_is_available_should_return_true_when_copies_available(self, sample_book):
        """Метод is_available() возвращает True когда есть доступные копии"""
        assert sample_book.is_available() is True
    
    def test_is_available_should_return_false_when_no_copies_available(self, sample_book):
        """Метод is_available() возвращает False когда нет доступных копий"""
        sample_book.available_copies = 0
        assert sample_book.is_available() is False
    
    def test_borrow_should_decrease_available_copies_and_return_true(self, sample_book):
        """Метод borrow() уменьшает available_copies и возвращает True"""
        initial_copies = sample_book.available_copies
        result = sample_book.borrow()
        
        assert result is True
        assert sample_book.available_copies == initial_copies - 1
    
    def test_borrow_should_return_false_when_no_copies_available(self, sample_book):
        """Метод borrow() возвращает False когда нет доступных копий"""
        sample_book.available_copies = 0
        result = sample_book.borrow()
        
        assert result is False
        assert sample_book.available_copies == 0
    
    def test_return_book_should_increase_available_copies_and_return_true(self, sample_book):
        """Метод return_book() увеличивает available_copies и возвращает True"""
        sample_book.available_copies = 2
        initial_copies = sample_book.available_copies
        result = sample_book.return_book()
        
        assert result is True
        assert sample_book.available_copies == initial_copies + 1
    
    def test_return_book_should_return_false_when_all_copies_returned(self, sample_book):
        """Метод return_book() возвращает False когда все копии уже возвращены"""
        sample_book.available_copies = sample_book.total_copies
        result = sample_book.return_book()
        
        assert result is False
        assert sample_book.available_copies == sample_book.total_copies


# ============= ТЕСТЫ КЛАССА READER =============

class TestReader:
    """Тесты для класса Reader"""
    
    def test_should_create_reader_with_valid_data(self):
        """Корректное создание читателя с валидными данными"""
        reader = Reader("R001", "John Doe", "john.doe@email.com")
        
        assert reader.reader_id == "R001"
        assert reader.name == "John Doe"
        assert reader.email == "john.doe@email.com"
        assert reader.borrowed_books == set()
        assert len(reader.history) == 0
    
    @pytest.mark.parametrize("reader_id", ["", None])
    def test_should_raise_error_for_empty_reader_id(self, reader_id):
        """Валидация: пустой reader_id должен вызывать ValueError"""
        with pytest.raises(ValueError, match="Reader ID cannot be empty"):
            Reader(reader_id, "Name", "email@test.com")
    
    @pytest.mark.parametrize("name", ["", None])
    def test_should_raise_error_for_empty_name(self, name):
        """Валидация: пустое имя должно вызывать ValueError"""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Reader("R001", name, "email@test.com")
    
    @pytest.mark.parametrize("email", ["", None, "invalid", "invalid@", "@domain.com"])
    def test_should_raise_error_for_invalid_email(self, email):
        """Валидация: некорректный email должен вызывать ValueError"""
        with pytest.raises(ValueError, match="Invalid email"):
            Reader("R001", "Name", email)
    
    def test_can_borrow_should_return_true_when_below_limit(self, sample_reader):
        """Метод can_borrow() возвращает True когда у читателя меньше MAX_BOOKS"""
        assert sample_reader.can_borrow() is True
    
    def test_can_borrow_should_return_false_when_at_limit(self, sample_reader):
        """Метод can_borrow() возвращает False когда достигнут лимит"""
        # Добавляем максимальное количество книг
        for i in range(sample_reader.MAX_BOOKS):
            sample_reader.borrowed_books.add(f"ISBN{i}")
        
        assert sample_reader.can_borrow() is False
    
    def test_add_borrowed_book_should_add_isbn_to_borrowed_books(self, sample_reader):
        """Метод add_borrowed_book() добавляет ISBN в borrowed_books"""
        result = sample_reader.add_borrowed_book("978-0-13-475759-9")
        
        assert result is True
        assert "978-0-13-475759-9" in sample_reader.borrowed_books
        assert len(sample_reader.history) == 1
    
    def test_add_borrowed_book_should_return_false_for_duplicate(self, sample_reader):
        """Метод add_borrowed_book() возвращает False при попытке добавить дубликат"""
        sample_reader.add_borrowed_book("978-0-13-475759-9")
        result = sample_reader.add_borrowed_book("978-0-13-475759-9")
        
        assert result is False
        assert len(sample_reader.borrowed_books) == 1
    
    def test_add_borrowed_book_should_return_false_when_over_limit(self, sample_reader):
        """Метод add_borrowed_book() возвращает False при превышении лимита"""
        # Добавляем максимальное количество книг
        for i in range(sample_reader.MAX_BOOKS):
            sample_reader.add_borrowed_book(f"ISBN{i}")
        
        # Попытка добавить еще одну книгу
        result = sample_reader.add_borrowed_book("EXTRA-ISBN")
        
        assert result is False
        assert len(sample_reader.borrowed_books) == sample_reader.MAX_BOOKS
    
    def test_remove_borrowed_book_should_remove_isbn_from_borrowed_books(self, sample_reader):
        """Метод remove_borrowed_book() удаляет ISBN из borrowed_books"""
        sample_reader.add_borrowed_book("978-0-13-475759-9")
        result = sample_reader.remove_borrowed_book("978-0-13-475759-9")
        
        assert result is True
        assert "978-0-13-475759-9" not in sample_reader.borrowed_books
    
    def test_remove_borrowed_book_should_return_false_if_book_not_found(self, sample_reader):
        """Метод remove_borrowed_book() возвращает False если книги нет в списке"""
        result = sample_reader.remove_borrowed_book("NONEXISTENT-ISBN")
        
        assert result is False
    
    def test_history_should_record_operations_with_timestamps(self, sample_reader):
        """История (history) корректно записывает операции с временными метками"""
        sample_reader.add_borrowed_book("ISBN1")
        sample_reader.remove_borrowed_book("ISBN1")
        sample_reader.add_borrowed_book("ISBN2")
        
        assert len(sample_reader.history) == 3
        assert all(isinstance(record[0], datetime) for record in sample_reader.history)
        assert "borrowed ISBN1" in sample_reader.history[0][1]
        assert "returned ISBN1" in sample_reader.history[1][1]
        assert "borrowed ISBN2" in sample_reader.history[2][1]


# ============= ТЕСТЫ КЛАССА LIBRARY =============

class TestLibrary:
    """Тесты для класса Library"""
    
    def test_should_create_library_with_valid_name(self):
        """Корректное создание библиотеки"""
        library = Library("City Library")
        
        assert library.name == "City Library"
        assert library.books == {}
        assert library.readers == {}
        assert library.active_loans == {}
    
    @pytest.mark.parametrize("name", ["", None])
    def test_should_raise_error_for_empty_library_name(self, name):
        """Валидация: пустое название библиотеки должно вызывать ValueError"""
        with pytest.raises(ValueError, match="Library name cannot be empty"):
            Library(name)
    
    def test_add_book_should_add_new_book_and_return_true(self, empty_library):
        """Метод add_book() добавляет новую книгу и возвращает True"""
        result = empty_library.add_book("978-0-13-475759-9", "Clean Code", "Robert Martin", 2008, 3)
        
        assert result is True
        assert "978-0-13-475759-9" in empty_library.books
        book = empty_library.books["978-0-13-475759-9"]
        assert book.title == "Clean Code"
        assert book.author == "Robert Martin"
    
    def test_add_book_should_increase_copies_for_existing_book(self, empty_library):
        """Метод add_book() увеличивает количество копий для существующей книги"""
        empty_library.add_book("978-0-13-475759-9", "Clean Code", "Robert Martin", 2008, 3)
        result = empty_library.add_book("978-0-13-475759-9", "Clean Code", "Robert Martin", 2008, 2)
        
        assert result is True
        book = empty_library.books["978-0-13-475759-9"]
        assert book.total_copies == 5
        assert book.available_copies == 5
    
    def test_register_reader_should_register_new_reader(self, empty_library):
        """Метод register_reader() регистрирует нового читателя"""
        result = empty_library.register_reader("R001", "Alice Smith", "alice@email.com")
        
        assert result is True
        assert "R001" in empty_library.readers
        reader = empty_library.readers["R001"]
        assert reader.name == "Alice Smith"
        assert reader.email == "alice@email.com"
    
    def test_register_reader_should_return_false_for_duplicate(self, empty_library):
        """Метод register_reader() возвращает False для дубликата"""
        empty_library.register_reader("R001", "Alice Smith", "alice@email.com")
        result = empty_library.register_reader("R001", "Another Name", "another@email.com")
        
        assert result is False
    
    def test_find_books_by_author_should_find_books_case_insensitive(self, library_with_data):
        """Метод find_books_by_author() находит книги (регистронезависимый поиск)"""
        books1 = library_with_data.find_books_by_author("robert martin")
        books2 = library_with_data.find_books_by_author("ROBERT MARTIN")
        
        assert len(books1) == 2
        assert len(books2) == 2
        assert all("robert martin" in book.author.lower() for book in books1)
    
    def test_find_books_by_title_should_find_books_case_insensitive(self, library_with_data):
        """Метод find_books_by_title() находит книги (регистронезависимый поиск)"""
        books1 = library_with_data.find_books_by_title("clean code")
        books2 = library_with_data.find_books_by_title("CLEAN CODE")
        
        assert len(books1) == 1
        assert len(books2) == 1
        assert books1[0].title == "Clean Code"
    
    def test_get_available_books_should_return_only_available_books(self, library_with_data):
        """Метод get_available_books() возвращает только доступные книги"""
        available_books = library_with_data.get_available_books()
        
        assert all(book.is_available() for book in available_books)
    
    def test_borrow_book_should_successfully_borrow_book(self, library_with_data):
        """Успешная выдача книги читателю"""
        result, message = library_with_data.borrow_book("R001", "978-0-13-475759-9")
        
        assert result is True
        assert "successfully borrowed" in message.lower()
        assert "R001" in library_with_data.active_loans
        assert "978-0-13-475759-9" in library_with_data.active_loans["R001"]
    
    def test_borrow_book_should_raise_reader_not_found_error(self, library_with_data):
        """Выброс ReaderNotFoundError для несуществующего читателя"""
        with pytest.raises(ReaderNotFoundError):
            library_with_data.borrow_book("NONEXISTENT", "978-0-13-475759-9")
    
    def test_borrow_book_should_return_false_for_nonexistent_book(self, library_with_data):
        """Возврат (False, message) для несуществующей книги"""
        result, message = library_with_data.borrow_book("R001", "NONEXISTENT-ISBN")
        
        assert result is False
        assert "not found" in message.lower()
    
    def test_borrow_book_should_raise_book_not_available_error(self, library_with_data):
        """Выброс BookNotAvailableError когда книга недоступна"""
        # Занимаем все копии книги
        book = library_with_data.books["978-0-13-475759-9"]
        book.available_copies = 0
        
        with pytest.raises(BookNotAvailableError):
            library_with_data.borrow_book("R001", "978-0-13-475759-9")
    
    def test_borrow_book_should_return_false_when_reader_at_limit(self, library_with_data):
        """Возврат (False, message) когда читатель достиг лимита книг"""
        # Занимаем максимальное количество книг
        reader = library_with_data.readers["R001"]
        for i in range(reader.MAX_BOOKS):
            reader.borrowed_books.add(f"EXTRA{i}")
        
        result, message = library_with_data.borrow_book("R001", "978-0-13-475759-9")
        
        assert result is False
        assert "limit" in message.lower()
    
    def test_borrow_book_should_return_false_when_book_already_borrowed(self, library_with_data):
        """Возврат (False, message) когда читатель уже взял эту книгу"""
        library_with_data.borrow_book("R001", "978-0-13-475759-9")
        result, message = library_with_data.borrow_book("R001", "978-0-13-475759-9")
        
        assert result is False
        assert "already borrowed" in message.lower()
    
    def test_return_book_should_successfully_return_book_no_fine(self, library_with_data):
        """Успешный возврат книги без штрафа (в срок)"""
        # Выдаем книгу
        library_with_data.borrow_book("R001", "978-0-13-475759-9")
        
        result, fine = library_with_data.return_book("R001", "978-0-13-475759-9")
        
        assert result is True
        assert fine == 0.0
        # Книга должна быть удалена из активных займов
        assert "978-0-13-475759-9" not in library_with_data.active_loans.get("R001", {})
    
    def test_return_book_should_raise_reader_not_found_error(self, library_with_data):
        """Выброс ReaderNotFoundError для несуществующего читателя"""
        with pytest.raises(ReaderNotFoundError):
            library_with_data.return_book("NONEXISTENT", "978-0-13-475759-9")
    
    def test_return_book_should_return_false_for_nonexistent_book(self, library_with_data):
        """Возврат (False, 0.0) для несуществующей книги"""
        result, fine = library_with_data.return_book("R001", "NONEXISTENT-ISBN")
        
        assert result is False
        assert fine == 0.0
    
    def test_return_book_should_return_false_if_book_not_borrowed(self, library_with_data):
        """Возврат (False, 0.0) если эта книга не была взята читателем"""
        result, fine = library_with_data.return_book("R001", "978-0-13-475759-9")
        
        assert result is False
        assert fine == 0.0
    
    def test_calculate_fine_should_return_0_for_loan_within_period(self, library_with_data):
        """Метод calculate_fine() возвращает 0 для непросроченного займа"""
        # Выдаем книгу
        library_with_data.borrow_book("R001", "978-0-13-475759-9")
        
        fine = library_with_data.calculate_fine("R001", "978-0-13-475759-9")
        
        # Должен быть 0, так как книга только что выдана
        assert fine == 0.0
    
    def test_calculate_fine_should_calculate_fine_correctly(self, library_with_data, monkeypatch):
        """Метод calculate_fine() корректно рассчитывает штраф"""
        # Фиксируем время выдачи
        fixed_now = datetime(2024, 1, 1)
        
        class MockDateTime:
            @staticmethod
            def now():
                return fixed_now
        
        monkeypatch.setattr('library_system.datetime', MockDateTime)
        
        # Выдаем книгу
        library_with_data.borrow_book("R001", "978-0-13-475759-9")
        
        # Перемещаем время вперед на 20 дней (просрочка)
        overdue_time = fixed_now + timedelta(days=20)
        
        class MockDateTimeOverdue:
            @staticmethod
            def now():
                return overdue_time
        
        monkeypatch.setattr('library_system.datetime', MockDateTimeOverdue)
        
        fine = library_with_data.calculate_fine("R001", "978-0-13-475759-9")
        expected_fine = 6 * library_with_data.FINE_PER_DAY  # 20 - 14 = 6 дней просрочки
        
        assert fine == pytest.approx(expected_fine)
    
    def test_get_overdue_loans_should_return_overdue_loans(self, library_with_data, monkeypatch):
        """Метод get_overdue_loans() возвращает список просроченных займов"""
        # Фиксируем время выдачи
        fixed_now = datetime(2024, 1, 1)
        
        class MockDateTime:
            @staticmethod
            def now():
                return fixed_now
        
        monkeypatch.setattr('library_system.datetime', MockDateTime)
        
        # Выдаем книгу
        library_with_data.borrow_book("R001", "978-0-13-475759-9")
        
        # Перемещаем время вперед на 20 дней (просрочка)
        overdue_time = fixed_now + timedelta(days=20)
        
        class MockDateTimeOverdue:
            @staticmethod
            def now():
                return overdue_time
        
        monkeypatch.setattr('library_system.datetime', MockDateTimeOverdue)
        
        overdue_loans = library_with_data.get_overdue_loans()
        
        assert len(overdue_loans) > 0
        assert overdue_loans[0]['reader_id'] == "R001"
        assert overdue_loans[0]['book_isbn'] == "978-0-13-475759-9"
    
    def test_get_reader_stats_should_return_correct_statistics(self, library_with_data):
        """Метод get_reader_stats() возвращает корректную статистику"""
        # Выдаем несколько книг
        library_with_data.borrow_book("R001", "978-0-13-475759-9")
        library_with_data.borrow_book("R001", "978-0-13-595705-9")
        
        stats = library_with_data.get_reader_stats("R001")
        
        assert stats['reader_id'] == "R001"
        assert stats['currently_borrowed'] == 2
        assert stats['total_borrowed'] >= 2
    
    def test_get_reader_stats_should_raise_reader_not_found_error(self, library_with_data):
        """Метод get_reader_stats() выбрасывает ReaderNotFoundError для несуществующего читателя"""
        with pytest.raises(ReaderNotFoundError):
            library_with_data.get_reader_stats("NONEXISTENT")
    
    def test_get_popular_books_should_return_top_books(self, library_with_data):
        """Метод get_popular_books() возвращает топ популярных книг"""
        # Выдаем книги несколько раз для создания статистики
        library_with_data.borrow_book("R001", "978-0-13-475759-9")
        library_with_data.borrow_book("R002", "978-0-13-475759-9")
        library_with_data.return_book("R001", "978-0-13-475759-9")
        library_with_data.borrow_book("R001", "978-0-13-475759-9")
        
        popular_books = library_with_data.get_popular_books(limit=2)
        
        assert len(popular_books) <= 2
        # Книга с наибольшим количеством выдач должна быть первой
        if popular_books:
            assert popular_books[0][0] == "978-0-13-475759-9"


# ============= ИНТЕГРАЦИОННЫЕ ТЕСТЫ =============

class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_book_lifecycle(self, empty_library):
        """Полный цикл работы с книгой"""
        library = empty_library
        
        # 1. Добавление книги
        result = library.add_book("978-0-13-475759-9", "Clean Code", "Robert Martin", 2008, 3)
        assert result is True
        
        # 2. Регистрация читателя
        result = library.register_reader("R001", "Alice Smith", "alice@email.com")
        assert result is True
        
        # 3. Проверка доступности книги
        available_books = library.get_available_books()
        assert len(available_books) == 1
        
        # 4. Выдача книги
        result, message = library.borrow_book("R001", "978-0-13-475759-9")
        assert result is True
        
        # 5. Проверка статистики читателя
        stats = library.get_reader_stats("R001")
        assert stats['currently_borrowed'] == 1
        
        # 6. Проверка доступности книги после выдачи
        available_books = library.get_available_books()
        book = library.books["978-0-13-475759-9"]
        if book.available_copies == 0:
            assert len(available_books) == 0
        
        # 7. Возврат книги
        result, fine = library.return_book("R001", "978-0-13-475759-9")
        assert result is True
        assert fine == 0.0
        
        # 8. Проверка обновленной статистики
        stats = library.get_reader_stats("R001")
        assert stats['currently_borrowed'] == 0
        assert stats['total_borrowed'] >= 1
        
        # 9. Проверка доступности книги после возврата
        available_books = library.get_available_books()
        assert len(available_books) >= 1
    
    def test_scenario_with_overdue_fine(self, empty_library, monkeypatch):
        """Сценарий с просрочкой"""
        library = empty_library
        
        # Фиксируем время
        fixed_now = datetime(2024, 1, 1)
        
        class MockDateTime:
            @staticmethod
            def now():
                return fixed_now
        
        monkeypatch.setattr('library_system.datetime', MockDateTime)
        
        # 1. Добавление книги и регистрация читателя
        library.add_book("978-0-13-475759-9", "Clean Code", "Robert Martin", 2008, 1)
        library.register_reader("R001", "Alice Smith", "alice@email.com")
        
        # 2. Выдача книги
        library.borrow_book("R001", "978-0-13-475759-9")
        
        # 3. Эмуляция просрочки (перемещаем время на 20 дней вперед)
        overdue_time = fixed_now + timedelta(days=20)
        
        class MockDateTimeOverdue:
            @staticmethod
            def now():
                return overdue_time
        
        monkeypatch.setattr('library_system.datetime', MockDateTimeOverdue)
        
        # 4. Проверка расчета штрафа перед возвратом
        fine = library.calculate_fine("R001", "978-0-13-475759-9")
        expected_fine = 6 * library.FINE_PER_DAY  # 20 - 14 = 6 дней просрочки
        assert fine == pytest.approx(expected_fine)
        
        # 5. Проверка просроченных займов
        overdue_loans = library.get_overdue_loans()
        assert len(overdue_loans) == 1
        
        # 6. Возврат с штрафом
        result, actual_fine = library.return_book("R001", "978-0-13-475759-9")
        assert result is True
        assert actual_fine == pytest.approx(expected_fine)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])