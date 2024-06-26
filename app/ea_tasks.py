from threading import Thread

from app.models import set_status
from app.video_parser import EmotionAnalyzer


class EmotionAnalysisTaskManager:
    tasks: list[EmotionAnalyzer] = []

    def __init__(self, app=None):
        self.app = app

    def init_app(self, app) -> None:
        self.app = app

    def add_task(self, task: EmotionAnalyzer) -> None:
        self.tasks.append(task)

    def get_task(self, index: int = None) -> EmotionAnalyzer:
        if index is None:
            index = 0
        return self.tasks[index]

    def get_tasks(self, start: int = 0, stop: int = 10) -> list[EmotionAnalyzer] or EmotionAnalyzer or None:
        try:
            result = self.tasks[start:stop]
            if not result:
                result = None
        except IndexError:
            result = None

        return result

    def handle_done_task(self, task: EmotionAnalyzer) -> None:
        set_status(self.app, task.video.file_hash, 'PROCESSING')
        self.tasks.remove(task)

    def handle_processing_task(self, task: EmotionAnalyzer) -> None:
        print("PROCESSING TASK: ", task.video.file_hash)

    def handle_uninitialized_task(self, task: EmotionAnalyzer) -> None:
        set_status(self.app, task.video.file_hash, 'PROCESSING')

        if task.step == 0:
            task.find_unique_faces()

        elif task.step == 1:
            task.find_emotions()

        elif task.step == -1:
            set_status(self.app, task.video.file_hash, 'DONE')
            task.status = 'DONE'

    def handle_failed_task(self, task: EmotionAnalyzer) -> None:
        set_status(self.app, task.video.file_hash, 'FAILED')
        task.reset()

    def update(self) -> None:
        tasks: list[EmotionAnalyzer] = self.get_tasks()
        if tasks is None:
            return

        for task in tasks:
            if task.status == 'DONE':
                # Thread(target=self.handle_done_task, args=[task]).start()
                self.handle_done_task(task)

            elif task.status == 'UNINITIALIZED':
                # Thread(target=self.handle_uninitialized_task, args=[task]).start()
                self.handle_uninitialized_task(task)

            elif task.status == 'PROCESSING':
                # Thread(target=self.handle_processing_task, args=[task]).start()
                self.handle_processing_task(task)

            print(task, task.status)
