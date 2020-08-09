class TMIStatus:
    def __init__(self, messages_per_30seconds, whispers_per_second, whispers_per_minute):
        self.messages_per_30seconds = messages_per_30seconds
        self.whispers_per_second = whispers_per_second
        self.whispers_per_minute = whispers_per_minute

TMIStatus.moderator = TMIStatus(
    messages_per_30seconds=100,
    whispers_per_second=3,
    whispers_per_minute=100
)
TMIStatus.known = TMIStatus(
    messages_per_30seconds=100,
    whispers_per_second=10,
    whispers_per_minute=200
)
TMIStatus.verified = TMIStatus(
    messages_per_30seconds=7500,
    whispers_per_second=20,
    whispers_per_minute=1200
)