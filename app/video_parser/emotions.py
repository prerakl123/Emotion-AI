import os
import sqlite3
import time
from pathlib import Path

import cv2
from deepface import DeepFace
from numpy import ndarray

from app.constants import STATUS
from app.video_parser import VideoParser


class EmotionParser:
    video: VideoParser
    emotion_analysis_dict: dict

    def __init__(self, video: VideoParser):
        self.video = video
        self.unique_faces_dir = self.video.create_subdir("unique_faces")

    def get_unique_faces_filenames(self) -> list[str]:
        return os.listdir(self.unique_faces_dir)

    @classmethod
    def load_images(cls, *image_paths) -> list:
        return [cv2.imread(img) for img in image_paths]

    def save_image(self, frame: ndarray, filename: str = "image.jpg", dir_path: Path = None) -> None:
        if dir_path is None:
            dir_path = self.unique_faces_dir

        cv2.imwrite(filename=dir_path.as_posix() + '/' + filename, img=frame)

    def get_excluded_people(self):
        return fetch_from_db(
            db_path=self.video.video_dir / "emotion_analysis.db",
            statement="SELECT person_name FROM people_data WHERE is_excluded=1;"
        )

    def set_excluded_people(self, *excluded_people_names):
        for name in excluded_people_names:
            set_to_db(
                db_path=self.video.video_dir / "emotion_analysis.db",
                statement=f"UPDATE people_data SET is_excluded=1 WHERE person_name='{name}';"
            )

    @classmethod
    def get_emotions(cls, frame: ndarray, actions: list = None, **deepface_config) -> list[dict]:
        if actions is None:
            actions = ['emotion']
        return DeepFace.analyze(frame, actions=actions, **deepface_config)

    @classmethod
    def compare(cls, face1: ndarray, face2: ndarray, **deepface_config):
        return DeepFace.verify(face1, face2, **deepface_config)

    def is_same(self, face1: ndarray, face2: ndarray) -> bool:
        try:
            result = self.compare(face1, face2)['verified']
        except ValueError:
            result = False

        return result


class EmotionAnalyzer(EmotionParser):
    current_frame: int
    status: STATUS
    unique_faces: list
    excluded_faces: list
    step: int = 0

    def __init__(self, video: VideoParser):
        EmotionParser.__init__(self, video)
        self.video = video
        self.running = True
        self.status = 'UNINITIALIZED'
        self.unique_faces = self.load_images(*self.get_unique_faces_filenames())

    def __repr__(self) -> str:
        return f"<EmotionAnalyzer hash='{self.video.file_hash}'>"

    def reset(self):
        self.current_frame = 0
        self.step = 0

    def find_unique_faces(self) -> None:
        """
        Find all the unique faces in a video and save them in
        ```./{video_hash}/unique_faces/person_{i}.jpg``` where i is the
        ID of the unique person found.
        """
        self.status = 'PROCESSING'

        start_time = time.time()
        while self.running and self.status == 'PROCESSING':
            ret, frame = self.video.read()
            detected_faces = self.video.find_faces(frame)

            for (x, y, w, h) in detected_faces:
                df = frame[y:y+h, x:x+w]

                for uf in self.unique_faces:
                    if not self.is_same(df, uf):
                        self.unique_faces.append(df)

            if self.current_frame == self.video.total_frames:
                self.running = False

        for i, img in enumerate(self.unique_faces):
            self.save_image(img, filename=f"person_{i}.jpg")

        self.step += 1

        print(f"Elapsed time for finding unique faces ({self.video.file_hash}):", time.time() - start_time, "s")

    def set_excluded_faces(self) -> None:
        ep = self.get_excluded_people()
        self.excluded_faces = self.load_images(
            filename for filename in self.get_unique_faces_filenames()
            if filename.split(".")[0] in ep
        )

    def find_emotions(self) -> None:
        self.status = 'PROCESSING'

        conn, cursor = get_conn_cursor(self.video.video_dir / "emotion_analysis.db")

        start_time = time.time()
        while self.running and self.status == 'PROCESSING':
            ret, frame = self.video.read()
            self.current_frame += 1

            detected_faces = self.video.find_faces(frame)
            for (x, y, w, h) in detected_faces:
                df = frame[y:y + h, x:x + w]

                try:
                    self.get_emotions(frame=df)
                except ValueError:
                    pass


def fetch_from_db(db_path: Path, statement: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(statement)
    try:
        result = cursor.fetchall()[0]
    except IndexError:
        result = list()
    except Exception as e:
        print(repr(e))
        result = list()
    conn.close()
    return result


def set_to_db(db_path: Path, statement: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(statement)
    conn.commit()
    conn.close()


def get_conn_cursor(db_path: Path) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return conn, cursor
