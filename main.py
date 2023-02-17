from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

# import psycopg2
# conn = psycopg2.connect(database="Store", user="postgres", password="soxa", host="127.0.0.1", port="5432")
app = Flask(__name__)
api = Api(app)


# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:8410179042@localhost/Store'
#
# db = SQLAlchemy(app)
class BookModel:
    id_ = 0

    def __init__(self, author: str, title: str, ):
        self.author = author
        self.title = title
        self.id = self.increase_id()

    @staticmethod
    def increase_id():
        BookModel.id_ += 1
        return BookModel.id_

    def serialize(self):
        return {"Id": self.id, "author": self.author, "title": self.title}


books = [BookModel(f'Author {idx}', f'Title {idx}') for idx in range(1, 11)]


class BooksResource(Resource):
    def get(self):
        return {'books': [book.serialize() for book in books]}, 200

    def post(self):
        data = request.get_json()
        new_book = BookModel(**data)
        books.append(new_book)
        return new_book.serialize(), 201


class BookResource(Resource):
    def find_book(self, pk):
        # book = [b for b in books if b.id == pk]
        book = next(filter(lambda x: x.id == pk, books), None)
        return book

    def get(self, pk):
        book = self.find_book(pk)
        if not book:
            return f'Book with id = {pk} not found', 400
        return book.serialize()

    def put(self, pk):
        book = self.find_book(pk)
        if not book:
            return f'Book with id = {pk} not found', 404
        data = request.get_json()
        book.author = data['author']
        book.title = data['title']
        return book.serialize()

    def delete(self, pk):
        book = self.find_book(pk)
        if not book:
            return f'Book with id = {pk} not found', 404
        books.remove(book)
        return "Book was removed", 200


api.add_resource(BooksResource, '/books')
api.add_resource(BookResource, '/books/<int:pk>')

if __name__ == '__main__':
    app.run(debug=True)
