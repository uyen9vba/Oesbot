import concurrent.futures

from wrappers.kraken import KrakenWrapper
from wrappers.bttv import BTTVWrapper
from wrappers.ffz import FFZWrapper
from managers.scheduler import BackgroundScheduler

class EmoteManager:
    def __init__(self, login, id_):
        self.login = login
        self.id_ = id_
        self.global_emotes = KrakenWrapper.get_global_emotes()
        self.channel_emotes = HelixWrapper.get_channel_emotes(self.login, self.id_)
        self.bttv_global_emotes = BTTVWrapper.get_global_emotes()
        self.bttv_channel_emotes = BTTVWrapper.get_channel_emotes(self.login)
        self.ffz_global_emotes = FFZWrapper.get_global_emotes()
        self.ffz_channel_emotes = FFZWrapper.get_channel_emotes(self.login)

        BackgroundScheduler.execute_interval(1 * 60 * 60, self.update_channel_emotes)
        BackgroundScheduler.execute_interval(1 * 60 * 60, self.update_global_emotes)

    def update_channel_emotes(self):
        concurrent.futures.ThreadPoolExecutor.submit(KrakenWrapper.get_channel_emotes(self.login, self.id_, force=True))
        concurrent.futures.ThreadPoolExecutor.submit(BTTVWrapper.get_channel_emotes(self.login, force=True))
        concurrent.futures.ThreadPoolExecutor.submit(FFZWrapper.get_channel_emotes(self.login, force=True))
        
    def update_global_emotes(self):
        concurrent.futures.ThreadPoolExecutor.submit(KrakenWrapper.get_global_emotes(force=True))
        concurrent.futures.ThreadPoolExecutor.submit(BTTVWrapper.get_global_emotes(force=True))
        concurrent.futures.ThreadPoolExecutor.submit(FFZWrapper.get_global_emotes(force=True))

    #def query_emote(self, word):
        
class EmoteAuth:
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
        return "[{}] {}".format(self.provider, self.code)

    def json(self):
        return {"code": self.code, "provider": self.provider, "id": self.id, "urls": self.urls}

    

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

