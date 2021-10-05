import settings
from boda.DriveSniffer import DriveSniffer

gclient = DriveSniffer(settings.PPT_TARGET_FOLDER, "creds.json")
invitados = gclient.download_file(settings.TEST_EXCEL_DRIVE_FILEID)

for invitado in invitados:
    renamed = gclient.copy_file(settings.PPT_DRIVE_FILEID, settings.PPT_TARGET_FOLDER,
                                f"InvitacionBoda{invitado['id']}")
    new_file = renamed["id"]
    acepto = "Acepto con gusto" if invitado["Acompanante"] == "" else "Aceptamos con gusto"
    noacepto = "Lamento no poder asistir" if invitado["Acompanante"] == "" else "Lamentamos no poder asistir"
    gclient.replaceContent("name1", invitado["Invitado"], new_file, invitado["id"])
    gclient.replaceContent("name2", invitado["Acompanante"], new_file, invitado["id"])
    gclient.replaceContent("acepto", acepto, new_file, invitado["id"])
    gclient.replaceContent("noacepto", noacepto, new_file, invitado["id"])
    print(renamed)
    pub = gclient.publish(new_file)
    link = f"https://docs.google.com/presentation/d/{new_file}/present?start=true&loop=false&delayms=5000"
    invitado["Link"] = link
    gclient.write_file(settings.TEST_EXCEL_DRIVE_FILEID, gclient.dict2matrix(invitados))

# https://docs.google.com/presentation/d/1OiYkAboDcFyGPobFooHZRFyGpzjSZevUrGoxfHjotc4/present?start=true&loop=false&delayms=5000