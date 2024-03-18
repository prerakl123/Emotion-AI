from app import celery


@celery.task(serializer="pickle")
def analyze_video(analyser):
    analyser.run()
