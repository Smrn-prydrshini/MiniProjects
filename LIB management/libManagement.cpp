#include <iostream>
#include <vector>
using namespace std;

class Book {
public:
    int id;
    string title, author;
    
    Book(int id, string title, string author) {
        this->id = id;
        this->title = title;
        this->author = author;
    }
};

class Library {
private:
    vector<Book> books;

public:
    void addBook(int id, string title, string author) {
        books.push_back(Book(id, title, author));
        cout << "✅ Book added successfully!\n";
    }

    void displayBooks() {
        if (books.empty()) {
            cout << "📚 No books available in the library.\n";
            return;
        }
        cout << "\n📖 Library Books:\n";
        for (const auto &book : books) {
            cout << "ID: " << book.id << " | Title: " << book.title << " | Author: " << book.author << endl;
        }
    }

    void searchBook(int id) {
        for (const auto &book : books) {
            if (book.id == id) {
                cout << "✅ Book Found: " << book.title << " by " << book.author << endl;
                return;
            }
        }
        cout << "❌ Book not found!\n";
    }

    void deleteBook(int id) {
        for (auto it = books.begin(); it != books.end(); it++) {
            if (it->id == id) {
                books.erase(it);
                cout << "✅ Book deleted successfully!\n";
                return;
            }
        }
        cout << "❌ Book ID not found!\n";
    }
};

int main() {
    Library lib;
    int choice, id;
    string title, author;

    while (true) {
        cout << "\n📚 Library Management System\n";
        cout << "1. Add Book\n2. Display Books\n3. Search Book\n4. Delete Book\n5. Exit\nEnter choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter Book ID: ";
                cin >> id;
                cin.ignore();
                cout << "Enter Book Title: ";
                getline(cin, title);
                cout << "Enter Author Name: ";
                getline(cin, author);
                lib.addBook(id, title, author);
                break;
            case 2:
                lib.displayBooks();
                break;
            case 3:
                cout << "Enter Book ID to search: ";
                cin >> id;
                lib.searchBook(id);
                break;
            case 4:
                cout << "Enter Book ID to delete: ";
                cin >> id;
                lib.deleteBook(id);
                break;
            case 5:
                cout << "📌 Exiting... Thank you!\n";
                return 0;
            default:
                cout << "❌ Invalid choice! Try again.\n";
        }
    }
}
