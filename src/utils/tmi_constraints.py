
class TMIConstraints:
    def __init__(self, privmsg_per_30seconds, whispers_per_second, whispers_per_minute):
        self.privmsg_per_30seconds = privmsg_per_30seconds
        self.whispers_per_second = whispers_per_second
        self.whispers_per_minute = whispers_per_minute

TMIConstraints.moderator = TMIConstraints(
    privmsg_per_30seconds=100,
    whispers_per_second=3,
    whispers_per_minute=100
)
TMIConstraints.known = TMIConstraints(
    privmsg_per_30seconds=100,
    whispers_per_second=10,
    whispers_per_minute=200
)
TMIConstraints.verified = TMIConstraints(
    privmsg_per_30seconds=7500,
    whispers_per_second=20,
    whispers_per_minute=1200
)