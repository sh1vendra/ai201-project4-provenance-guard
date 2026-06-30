from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
