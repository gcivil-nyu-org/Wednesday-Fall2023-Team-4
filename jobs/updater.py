from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import expire_student_status


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(expire_student_status, 'interval', seconds=86400)
    scheduler.start()
