import settings
from flask import Flask

app = Flask(__name__)

@app.route("/acepto/<name>")
@app.route("/no-acepto/<name>")
def invite(name):
    return """<iframe src="https://drive.google.com/file/d/1A76ke6_thFTwcOe2iV7CGtydkPoil8VM/preview" width="100%" 
    height="100%" allow="autoplay"></iframe>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.FLASK_PORT)