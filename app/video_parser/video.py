import os
import secrets
import sqlite3
from pathlib import Path

import cv2
from numpy import ndarray
from werkzeug.datastructures import FileStorage


class VideoParser:
    file_hash: str
    video_dir: Path
    video_file_path: Path
    total_frames: int
    original_fps: int
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
        self.total_frames, self.original_fps = self._get_frame_fps()

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

    def _get_frame_fps(self) -> tuple[int, int]:
        cap = cv2.VideoCapture(str(self.video_file_path))
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
        return length, fps

    def get_frame(self, frame_number: int) -> bytes:
        cap = cv2.VideoCapture(str(self.video_file_path))
        cap.set(1, frame_number)
        ret, frame = cap.read()
        if ret is None:
            raise KeyError(
                "Invalid Frame number: ", frame_number,
                "\nTotal Frame count of video is: ", self.total_frames
            )
        _, img = cv2.imencode('.jpg', frame[:, :, ::-1])
        buffer = img.tobytes()
        return buffer
