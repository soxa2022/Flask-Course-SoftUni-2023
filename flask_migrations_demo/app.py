from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from decouple import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config("USER_NAME")}:{config("PASSWORD")}' \
                                        f'@localhost:{config("PORT")}/{config("DB_NAME")}'
db = SQLAlchemy(app)
api = Api(app)
migrate = Migrate(app, db)


def as_dict(value):
    return {c.name: getattr(value, c.name) for c in value.__table__.columns}


class BookModel(db.Model):
    __tablename__ = 'books'
    pk = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    reader_pk = db.Column(db.Integer, ForeignKey('readers.pk'))
    reader = db.relationship('ReaderModel')


class ReaderModel(db.Model):
    __tablename__ = 'readers'
    pk = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    books = db.relationship("BookModel", backref="books", lazy='dynamic')


class BookResource(Resource):
    def post(self):
        data = request.get_json()
        book = BookModel(**data)
        db.session.add(book)
        db.session.commit()
        return as_dict(book), 201


class ReaderResource(Resource):
    def post(self):
        data = request.get_json()
        reader = ReaderModel(**data)
        db.session.add(reader)
        db.session.commit()
        return as_dict(reader), 201


api.add_resource(BookResource, '/books')
api.add_resource(ReaderResource, '/readers')

# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

# Many-to Junction table

# readers_books = db.Table(
#     "readers_books", db.Model.metadata,
#     db.Column("book_pk", db.Integer, db.ForeignKey("books.pk")),
#     db.Column("reader_pk", db.Integer, db.ForeignKey("readers.pk")),
# )
#
#
# class BookModel(db.Model):
#     __tablename__ = "books"
#     pk = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255), nullable=False)
#     author = db.Column(db.String(255), nullable=False)
#
# class ReaderModel(db.Model):
#     __tablename__ = "readers"
#     pk = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(255), nullable=False)
#     last_name = db.Column(db.String(255), nullable=False)
#     books = db.relationship('BookModel’,secondary=readers_books,  lazy='subquery', backref=db.backref('books', lazy=True))
