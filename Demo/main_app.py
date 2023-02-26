from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

books = []

class Books(Resource):
    def get(self):
        pass


api.add_resource(Books, "books/")
api.add_resource(Books, "books/<int : id>")
if __name__ == "__main__":
    app.run(debug=True)
