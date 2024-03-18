import base64
import json
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Sequence

import cv2
from cv2.data import haarcascades
from numpy import ndarray
from werkzeug.datastructures import FileStorage

hcc = cv2.CascadeClassifier(haarcascades + 'haarcascade_frontalface_default.xml')
"Haarcascade Classifier for face detection."


class VideoParser:
    file_hash: str
    video_dir: Path
    video_file_path: Path
    total_frames: int
    original_fps: int
    dimensions: int
    video_db: Path

    def __init__(
        self,
        file: FileStorage,
        db_folder: os.PathLike = None
    ):
        if db_folder is None:
            db_folder = Path("./db")

        self.file_hash = self._set_file_hash()
        self.video_dir = self._init_video_dir(db_folder)
        self.video_file_path = self._save_original_video(file)

        self._cap = cv2.VideoCapture(str(self.video_file_path))

        (self.total_frames,
         self.original_fps,
         self.dimensions) = self._get_props()

        self._init_config_files(self.video_dir)
        self._init_video_analysis_db(self.video_dir)

    @classmethod
    def _set_file_hash(cls) -> str:
        return secrets.token_hex(20)

    def _init_video_dir(self, db_folder: Path) -> Path:
        new_dir = db_folder / self.file_hash
        os.makedirs(new_dir, exist_ok=True)
        return new_dir

    def _init_config_files(self, vid_dir: Path) -> None:
        with open(vid_dir / "analysis.json", 'w') as analysis_file:
            json.dump(
                obj={"total_frames": self.total_frames},
                fp=analysis_file,
                indent=4
            )
            analysis_file.close()

    @classmethod
    def _init_video_analysis_db(cls, vid_dir: Path) -> None:
        conn = sqlite3.connect(vid_dir / "emotion_analysis.db")
        conn.execute("PRAGMA foreign_keys = 2")
        cursor = conn.cursor()
        stmts = """
            CREATE TABLE IF NOT EXISTS people_data(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name VARCHAR(255),
                frames INTEGER,
                dominant_emotion VARCHAR,
                is_excluded TINYINT(1) DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS emotion_data(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NULL,
                frame_no INTEGER NOT NULL,
                angry VARCHAR(255) NULL,
                disgust VARCHAR(255) NULL,
                fear VARCHAR(255) NULL,
                happy VARCHAR(255) NULL,
                sad VARCHAR(255) NULL,
                surprise VARCHAR(255) NULL,
                neutral VARCHAR(255) NULL,
                FOREIGN KEY (person_id) REFERENCES people_data(id)
            );
            
            CREATE TABLE IF NOT EXISTS diarization(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER,
                start_time VARCHAR,
                end_time VARCHAR,
                transcript TEXT,
                FOREIGN KEY (person_id) REFERENCES people_data(id) 
            )
        """
        cursor.executescript(stmts)
        conn.commit()
        conn.close()

    def _save_original_video(self, file: FileStorage) -> Path:
        ovf_name = self.video_dir / file.filename
        file.save(ovf_name)
        return ovf_name

    def _get_props(self) -> tuple[int, int, tuple[int, int]]:
        length = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(self._cap.get(cv2.CAP_PROP_FPS))
        width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return length, fps, (height, width)

    def create_subdir(self, name: str) -> Path:
        os.makedirs(self.video_dir / name, exist_ok=True)
        return self.video_dir / name

    def get_frame_bytes_by_index(self, frame_number: int, to_b64: bool = False) -> bytes:
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self._cap.read()
        if ret is None:
            raise KeyError(
                "Invalid Frame number: ", frame_number,
                "\nTotal Frame count of video is: ", self.total_frames
            )

        _, img = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        buffer = img.tobytes()

        self.reset_cap()

        if to_b64:
            return base64.b64encode(buffer)

        return buffer

    def get_frame_np_by_index(self, frame_number: int) -> ndarray:
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self._cap.read()
        if ret is None:
            raise KeyError(
                "Invalid Frame number: ", frame_number,
                "\nTotal Frame count of video is: ", self.total_frames
            )

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def read(self) -> tuple[bool, ndarray]:
        return self._cap.read()

    def reset_cap(self) -> None:
        self._cap.release()
        self._cap = cv2.VideoCapture(str(self.video_file_path))

    @classmethod
    def convert_to(cls, frame: ndarray, code: int, **config) -> ndarray:
        return cv2.cvtColor(src=frame, code=code, **config)

    @classmethod
    def find_faces(
            cls, frame: ndarray,
            scale_factor: float = 1.2,
            min_neighbors: int = 6,
            min_size: tuple = (100, 100)
    ) -> Sequence[Sequence[int]]:
        return hcc.detectMultiScale(
            image=frame,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size
        )
