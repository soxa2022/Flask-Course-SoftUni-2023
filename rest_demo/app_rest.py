from flask import Flask, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class BookModel:
    pk = 1

    def __init__(self, author, title):
        self.pk = BookModel.pk
        self.title = title
        self.author = author
        BookModel.pk += 1

    def serialize(self):
        return {"Author": f"{self.author}", "Title": f"{self.title}"}


books = [BookModel(f"Author {i}", f"Title {i}") for i in range(1, 11)]


class Book(Resource):
    @staticmethod
    def find_book(idx):
        book = next(filter(lambda x: x.pk == idx, books), None)
        return book

    def get(self, pk):
        book = self.find_book(pk)
        if book:
            return book.serialize()

    def put(self, pk):
        book = self.find_book(pk)
        if book:
            data = request.get_json()
            book.title = data["Title"]
            book.author = data["Author"]
            return book.serialize(), 200
        return {"error": "Book Not Found"}, 404

    def delete(self, pk):
        book = self.find_book(pk)
        if book:
            books.remove(book)
            return f"Book {book.title} from {book.author} is deleted"
        return {"error": "Book Not Found"}, 404


class Books(Resource):
    def get(self):
        return {"data": [b.serialize() for b in books]}

    def post(self):
        try:
            data = request.get_json()
            book = BookModel(**data)
            books.append(book)
            return book.serialize(), 201
        except Exception as ex:
            return {"error": "Bad Request"}, 400


api.add_resource(Book, "/books/<int:pk>")
api.add_resource(Books, "/books")

if __name__ == "__main__":
    app.run(debug=True)
