# this serves as and empty placeholder to facilitate the developing and testing process without implementing the entire
# cura source code


import json


class Script:

    def __init__(self):
        self.settings = json.loads(self.getSettingDataString())

    def getSettingValueByKey(self, key):
        return self.settings['settings'][key]

    def getSettingDataString(self):
        return ""
