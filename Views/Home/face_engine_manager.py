# face_engine_manager.py
import numpy as np
import cv2
from insightface.app import FaceAnalysis


class FaceEngineManager:
    def __init__(self, model_name='buffalo_l'):
        self.engine = FaceAnalysis(name=model_name, providers=['CPUExecutionProvider'])
        self.engine.prepare(ctx_id=0)

    def detect_faces(self, frame_rgb):
        return self.engine.get(frame_rgb)

    def encode_face(self, image):
        faces = self.engine.get(image)
        return faces[0].embedding if faces else None

    def compute_similarity(self, emb1, emb2):
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
