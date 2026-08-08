from flask import Flask, render_template

from config import Config
from routes.interview import interview_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.register_blueprint(interview_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)