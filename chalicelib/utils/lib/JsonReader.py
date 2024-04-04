import json


class JsonReader:
    def read_from_file(file_path):
        f = open(file_path)
        return json.load(f)

    def read_from_str(json_string):
        return json.loads(json_string)
