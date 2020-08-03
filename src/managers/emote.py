class EmoteManager:
    def __init__(self, code, provider, id, urls):
        self.code = code
        self.provider = provider
        self.id = id
        self.urls = urls

    def __eq__(self, other):
        if not isinstance(other, EmoteManager):
            return False
        
        return self.provider == other.provider and self.id == other.id

    def __hash__(self):
        return hash((self.provider, self.id))

    def __repr__(self):
        return "[{}] {}".format(self.provider], self.code)

    def json(self):
        return {"code": self.code, "provider": self.provider, "id": self.id, "urls": self.urls}

    @staticmethod
    def emote(json):
        return EmoteManager(**json)

class Emote:
    def __init__(self, start, end, emote):
        self.start = start
        self.end = end
        self.emote = emote

    def __eq__(self, other):
        if not isinstance(other, Emote):
            return False

    def __hash__(self):
        return hash((self.start, self.end, self.emote))

    def __repr__(self):
        return "{} @ {}-{}".format(self.emote, self.start, self.end)

    def json(self):
        return {"start": self.start, "end": self.end, "emote": self.emote.json()}

