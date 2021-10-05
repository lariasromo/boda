import settings
from flask import Flask

from boda.DriveSniffer import DriveSniffer

app = Flask(__name__)

@app.route("/<acepto>/<name>")
@app.route("/<acepto>/<name>")
def invite(acepto, name):
    gclient = DriveSniffer(settings.PPT_TARGET_FOLDER, "creds.json")
    invitados = gclient.download_file(settings.TEST_EXCEL_DRIVE_FILEID)
    for i in invitados:
        if i["id"] == name:
            i["RSVP"] = acepto
            gclient.write_file(settings.TEST_EXCEL_DRIVE_FILEID, gclient.dict2matrix(invitados))
            return """<iframe src="https://drive.google.com/file/d/1A76ke6_thFTwcOe2iV7CGtydkPoil8VM/preview" 
            width="100%" height="100%" allow="autoplay"></iframe>""", 200
    return "", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.FLASK_PORT)