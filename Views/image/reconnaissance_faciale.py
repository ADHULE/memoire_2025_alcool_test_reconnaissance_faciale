import sys
import cv2
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage


class CameraMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sélecteur de Caméras WiFi")
        self.setGeometry(100, 100, 1000, 600)

        # Dictionnaire des caméras ajoutées (clé = URL effective, valeur = nom convivial)
        self.available_cameras = {}
        self.selected_cameras = []
        self.camera_threads = {}
        self.camera_counter = 1  # Pour attribuer un nom unique à chaque caméra

        # Création du layout principal en deux panneaux (vidéo – contrôles)
        main_layout = QHBoxLayout(self)

        # Panneau gauche : pour les flux vidéo
        self.video_panel = QFrame(self)
        self.video_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.video_layout = QVBoxLayout()
        self.video_panel.setLayout(self.video_layout)

        # Panneau droit : pour les contrôles
        self.controls_panel = QFrame(self)
        self.controls_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        controls_layout = QVBoxLayout()

        # Titre pour le groupe de saisie
        title_label = QLabel("Ajouter une caméra WiFi")
        controls_layout.addWidget(title_label)

        # Champ de saisie de l'URL/IP
        self.url_lineedit = QLineEdit()
        self.url_lineedit.setPlaceholderText("Entrez l’URL ou l’adresse IP de la caméra")
        controls_layout.addWidget(self.url_lineedit)

        # Champ de saisie du mot de passe
        self.password_lineedit = QLineEdit()
        self.password_lineedit.setPlaceholderText("Entrez le mot de passe (si requis)")
        self.password_lineedit.setEchoMode(QLineEdit.Password)
        controls_layout.addWidget(self.password_lineedit)

        # Bouton pour ajouter la caméra après saisie
        self.add_camera_button = QPushButton("Ajouter la caméra")
        self.add_camera_button.clicked.connect(self.add_camera)
        controls_layout.addWidget(self.add_camera_button)

        # Label de feedback sur la connexion
        self.feedback_label = QLabel("")
        controls_layout.addWidget(self.feedback_label)

        # Liste des caméras ajoutées avec cases à cocher
        self.camera_list = QListWidget()
        controls_layout.addWidget(self.camera_list)

        # Bouton pour démarrer les flux vidéo des caméras sélectionnées dans la liste
        self.start_button = QPushButton("Démarrer les flux vidéo")
        self.start_button.clicked.connect(self.start_camera_streams)
        controls_layout.addWidget(self.start_button)

        self.controls_panel.setLayout(controls_layout)

        # Ajouter les deux panneaux dans le layout principal
        main_layout.addWidget(self.video_panel, stretch=3)  # Espace important pour les vidéos
        main_layout.addWidget(self.controls_panel, stretch=1)  # Panneau de contrôle plus étroit
        self.setLayout(main_layout)

        self.apply_styles()

    def add_camera(self):
        """
        Récupère l’URL et le mot de passe saisis, tente une connexion,
        et si elle est réussie, ajoute la caméra dans la liste.
        """
        url = self.url_lineedit.text().strip()
        password = self.password_lineedit.text().strip()

        if url == "":
            self.feedback_label.setText("Veuillez saisir une URL ou une adresse IP.")
            return

        # Constituer l'URL effective en insérant les identifiants si nécessaire.
        effective_url = url
        if "@" not in url and password != "":
            # Supposons ici que la caméra utilise le protocole RTSP et un nom d'utilisateur par défaut "admin"
            if url.lower().startswith("rtsp://"):
                effective_url = "rtsp://admin:" + password + "@" + url[7:]
            else:
                effective_url = url  # Pour d'autres protocoles, laisser tel quel

        # Tenter d'ouvrir la caméra pour tester la connexion
        cap = cv2.VideoCapture(effective_url)
        ret, frame = cap.read()
        if ret:
            self.feedback_label.setText("Connexion réussie!")
            friendly_name = f"Caméra {self.camera_counter}"
            self.camera_counter += 1
            self.available_cameras[effective_url] = friendly_name

            # Ajouter l'item dans la QListWidget (avec la donnée effective URL)
            item_text = f"{friendly_name} ({effective_url})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, effective_url)
            item.setCheckState(Qt.Unchecked)
            self.camera_list.addItem(item)
        else:
            self.feedback_label.setText("Connexion impossible à la caméra.")
        cap.release()

        # Effacer les champs de saisie
        self.url_lineedit.clear()
        self.password_lineedit.clear()

    def start_camera_streams(self):
        """
        Parcourt la liste des caméras ajoutées et démarre les flux vidéo uniquement pour
        celles dont la case est cochée.
        """
        self.selected_cameras = []
        for i in range(self.camera_list.count()):
            item = self.camera_list.item(i)
            if item.checkState() == Qt.Checked:
                cam_url = item.data(Qt.UserRole)
                self.selected_cameras.append(cam_url)

        # Effacer les anciens widgets vidéo
        while self.video_layout.count():
            widget = self.video_layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

        # Démarrer le flux vidéo pour chaque caméra sélectionnée
        for cam_url in self.selected_cameras:
            self.start_camera_stream(cam_url)

    def start_camera_stream(self, cam_url):
        """
        Crée un QLabel dans lequel le flux vidéo sera affiché et lance le flux dans un thread dédié.
        """
        friendly_name = self.available_cameras.get(cam_url, "Caméra inconnue")
        label = QLabel(self)
        label.setText(f"Chargement du flux : {friendly_name}")
        label.setAlignment(Qt.AlignCenter)
        self.video_layout.addWidget(label)

        thread = threading.Thread(target=self.capture_stream, args=(cam_url, label))
        thread.daemon = True
        thread.start()
        self.camera_threads[cam_url] = thread

    def capture_stream(self, cam_url, label):
        """
        Capture le flux vidéo à partir de l'URL fournie et l'affiche dans le QLabel correspondant.
        """
        cap = cv2.VideoCapture(cam_url)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                label.setPixmap(pixmap)
            else:
                label.setText(f"Flux de {self.available_cameras.get(cam_url, 'la caméra')} inaccessible.")
            time.sleep(0.1)
        cap.release()

    def apply_styles(self):
        """
        Charge et applique la feuille de style CSS depuis un fichier externe.
        """
        try:
            with open("Styles/webcam_style.css", "r") as file:
                self.setStyleSheet(file.read())
        except Exception as e:
            print("Erreur de chargement du style :", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraMonitor()
    window.show()
    sys.exit(app.exec())
