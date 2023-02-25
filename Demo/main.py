from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello():
    context = {"name": "Flask"}
    return render_template("index.html", **context)


if "__main__" == __name__:
    app.run()
