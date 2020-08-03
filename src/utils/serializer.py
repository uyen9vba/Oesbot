import json
import datetime

class JSONSerializer:
    def serialize(data):
        return json.dumps(data)

    def deserialize(cache):
        return json.loads(cache)

    def serialize_datetime(data):
        return json.dumps(data.timestamp() * 1000)

    def deserialize_datetime(cache):
        return json.loads(datetime.datetime.fromtimestamp(cache / 1000, tz=datetime.timezone.utc))
