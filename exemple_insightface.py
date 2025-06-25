import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QFileDialog, QSizePolicy
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from insightface.app import FaceAnalysis

class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reconnaissance Faciale")
        self.setMinimumSize(800, 600)

        # Interface graphique
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setScaledContents(True)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.btn_start = QPushButton("Démarrer")
        self.btn_stop = QPushButton("Arrêter")
        self.btn_add = QPushButton("Ajouter une personne")

        # Mise en page
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_add)
        self.setLayout(layout)

        # Initialisation du modèle InsightFace
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0)
        self.face_db = []

        # Caméra
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Connexions des boutons
        self.btn_start.clicked.connect(self.start_video)
        self.btn_stop.clicked.connect(self.stop_video)
        self.btn_add.clicked.connect(self.ajouter_personne)

    def start_video(self):
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.timer.start(30)

    def stop_video(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.video_label.clear()

    def ajouter_personne(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Choisir une image")
        if filename:
            img = cv2.imread(filename)
            faces = self.app.get(img)
            if faces:
                self.face_db.append({
                    "nom": filename.split("/")[-1],
                    "embedding": faces[0].embedding
                })

    def update_frame(self):
        if not self.cap:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        faces = self.app.get(frame)
        for face in faces:
            bbox = face.bbox.astype(int)
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            personne = "Inconnu"
            best_score = 0.0
            for profil in self.face_db:
                sim = np.dot(face.embedding, profil["embedding"]) / (
                    np.linalg.norm(face.embedding) * np.linalg.norm(profil["embedding"])
                )
                if sim > 0.65 and sim > best_score:
                    personne = profil["nom"]
                    best_score = sim

            age = f"{int(face.age)} ans" if hasattr(face, "age") else "âge inconnu"
            label = f"{personne} ({age})"
            cv2.putText(frame, label, (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qimg = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.showMaximized()  # Démarre directement en plein écran
    sys.exit(app.exec())
