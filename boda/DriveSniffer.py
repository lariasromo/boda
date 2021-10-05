import os
import datetime
import json
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class DriveSniffer:
    def __init__(self, folder_id, creds_file):
        self.folder_id = folder_id
        self.creds_file = creds_file
        self.SCOPES = ["https://www.googleapis.com/auth/drive"]
        creds = self.run_permissions()
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.slides_service = build('slides', 'v1', credentials=creds)
        self.sheets_service = build('sheets', 'v4', credentials=creds)

    def run_permissions(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def getAllFolders(self):
        folder_id = self.folder_id
        results = self.drive_service.files().list(
            q="parents in '" + folder_id + "' and trashed = false",
            fields="nextPageToken, files(id, name, kind, mimeType, createdTime, modifiedTime)",
            pageSize=400).execute()

        return results

    def get_download_mimetype(self, mime_type):
        if mime_type == 'application/vnd.google-apps.document':
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif mime_type == "application/vnd.google-apps.presentation":
            return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        else:
            return mime_type

    def dict2matrix(self, ds):
        matrix = [list(ds[0].keys())]
        for x, d in enumerate(ds):
            matrix.append([])
            for r in d:
                matrix[x+1].append(d[r])
        return matrix

    def copy_file(self, file_id, new_folder, new_title):
        try:
            return self.drive_service.files().copy(fileId=file_id, body={'name': new_title}).execute()
        except Exception as e:
            print(e)
            print('An error occurred')
            return None

    def download_file(self, file_id):
        sheet = self.sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=file_id,
                                    range='Sheet1!A1:E').execute()
        values = result.get('values', [])
        headers = []
        intents = []
        for r, row in enumerate(values):
            intent = {}
            for c, s in enumerate(row):
                if r == 0:
                    headers.append(s)
                else:
                    intent[headers[c]] = s
            intents.append(intent)

        return [i for i in intents if i != {}]

    def write_file(self, file_id, values):
        body = {
            'values': values
        }
        result = self.sheets_service.spreadsheets().values().update(valueInputOption="USER_ENTERED",
            spreadsheetId=file_id, range='Sheet1!A1:E', body=body).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))
        return result

    def getJSONs(self):
        files = self.getAllFolders()
        xmls = []
        # print(files["files"])
        for file in files["files"]:
            if file["mimeType"] == "application/json":
                xmls.append(self.download_file(file["id"]).decode("utf-8"))

        return xmls

    def createResults(self, name, data):
        now = datetime.datetime.utcnow()
        file_metadata = {
            'name': "%s (%s UTC)" % (name, now),
            'mimeType': 'application/vnd.google-apps.folder',
            "parents": [self.folder_id]
        }
        file_name = "%s.json" % name
        with open(file_name, "w") as f:
            json.dump(data, f)
            f.close()
            media_body = MediaFileUpload(file_name, mimetype='application/json', resumable=True)
            file_metadata = {
                'name': file_name,
                'title': file_name,
                'mimeType': 'application/json',
                "parents": [self.folder_id]
            }

            self.drive_service.files().create(body=file_metadata, media_body=media_body).execute()

        os.remove(file_name)

    def replaceContent(self, old, new, file_id, invitado_id, pages=[]):
        self.slides_service.presentations().batchUpdate(
            body={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {
                                "text": '{{' + old + '}}'
                            },
                            "replaceText": new,
                            "pageObjectIds": pages,
                        }
                    },
                    # {
                    #     "updateTextStyle": {
                    #         "objectId": 'gf5c099f036_1_25',
                    #         "style": {
                    #             "link": {
                    #                 "url": f"http://acepto/{invitado_id}"
                    #             }
                    #         },
                    #         "fields": "*"
                    #     }
                    # },
                    {
                        "updateTextStyle": {
                            "objectId": "gf5c099f036_1_36",
                            "style": {
                                "link": {
                                    "url": f"http://acepto/{invitado_id}"
                                }
                            },
                            "fields": "*"
                        }
                    },
                    # {
                    #     "updateTextStyle": {
                    #         "objectId": 'gf5c099f036_1_26',
                    #         "style": {
                    #             "link": {
                    #                 "url": f"http://no-acepto/{invitado_id}"
                    #             }
                    #         },
                    #         "fields": "*"
                    #     }
                    # },
                    {
                        "updateTextStyle": {
                            "objectId": "gf5c099f036_1_37",
                            "style": {
                                "link": {
                                    "url": f"http://no-acepto/{invitado_id}"
                                }
                            },
                            "fields": "*"
                        }
                    }
                ]
            },
            presentationId=file_id
        ).execute()

    def publish(self, file_id):
        creds = self.run_permissions()
        service = build('drive', 'v2', credentials=creds)
        p = service.revisions().patch(fileId=file_id, revisionId=1,
                                         body={"published": True, "publishedOutsideDomain": True}).execute()
        return service.revisions().get(fileId=file_id, revisionId=1).execute()

    def getPages(self, presentationId):
        return self.slides_service.presentations().get(presentationId=presentationId).execute()

    def getElements(self):
        return self.slides_service.presentations().pages(fields=["pageElements.objectId"])
