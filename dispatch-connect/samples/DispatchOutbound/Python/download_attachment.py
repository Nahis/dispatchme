import shutil
import requests

token_id = 'token_id'
file = requests.get("http://files-api.dispatch.me/v1/datafiles/%s" % token_id, stream=True)
extension = file.headers["content-type"].split("/")[1]
with open("%s/images/%s.%s" % ("working_folder", token_id, extension), "wb") as f:
    shutil.copyfileobj(file.raw, f)
