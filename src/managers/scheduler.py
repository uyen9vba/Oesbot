import datetime

from apscheduler.schedulers.background import BackgroundScheduler

class ScheduledJob:
    def __init__(self, job):
        self.job = job

    def pause(self, *args, **kwargs):
        if self.job:
            self.job.pause(*args, **kwargs)

    def resume(self, *args, **kwargs):
        if self.job:
            self.job.resume(*args, **kwargs)

    def remove(self, *args, **kwargs):
        if self.job:
            self.job.remove(*args, **kwargs)


class ScheduleManager:
    def __init__(self, scheduler):
        self.scheduler = scheduler
    
    @staticmethod
    def init():
        self.scheduler = BackgroundScheduler(daemon=True)
        self.scheduler.start()

    @staticmethod
    def execute(function, args=[], kwargs={}, scheduler=None):
        if scheduler is None:
            scheduler = self.scheduler

        if scheduler is None:
            raise ValueError("No scheduler available")

        job = scheduler.add_job(
            function,
            "date",
            datetime.datetime.utcnow(),
            args=args,
            kwargs=kwargs
        )

        return ScheduledJob(job)

    @staticmethod
    def execute_delayed(delay, function, args=[], kwargs{}, scheduler=None):
        if scheduler is None:
            scheduler = self.scheduler

        if scheduler is None: 
            raise ValueError("No scheduler available")

        job = scheduler.add_job(
            function,
            "date",
            datetime.datetime.utcnow() +datetime.timedelta(seconds=delay),
            args=args,
            kwargs=kwargs
        )

        return ScheduledJob(job)

    @staticmethod
    def execute_interval(interval, function, args=[], kwargs={}, scheduler=None, jitter=None):
        if scheduler is None:
            scheduler = self.scheduler

        if scheduler is None:
            raise ValueError("No Scheduler available")

        job = scheduler.add_job(
            function,
            "interval",
            seconds=interval,
            args=args,
            kwargs=kwargs,
            jitter=jitter
        )

        return ScheduledJob(job)