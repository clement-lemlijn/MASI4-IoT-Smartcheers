
from flask import Flask

app = Flask(__name__)


@app.route("/greeting", methods=["GET"])
def greeting():
    return "Hello World"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
