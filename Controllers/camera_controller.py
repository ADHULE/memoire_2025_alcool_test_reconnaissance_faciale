from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox
import cv2
import os
import numpy as np

class CameraController:
    def __init__(self, view):
        """Initialisation du contrôleur avec une référence à la vue."""
        self.view = view
        self.webcam = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.face_cascade = cv2.CascadeClassifier(
            "Views/image/haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.training_file = None
        self.is_recognizing = False
        self.camera_active = False

        self._populate_camera_list()
        self._start_default_camera()

    def _populate_camera_list(self):
        """Détecte et peuple la liste des caméras connectées."""
        available_cameras = self._get_connected_cameras()
        self.view.update_camera_list(available_cameras)

    def _get_connected_cameras(self):
        """Détecte les caméras connectées."""
        available_cameras = {}
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras[i] = f"Caméra {i}"
                cap.release()
        return available_cameras

    def _start_default_camera(self):
        self._start_camera(0)

    def _start_camera(self, camera_source):
        """Démarre la webcam sélectionnée."""
        if self.webcam and self.webcam.isOpened():
            self.stop_camera()

        self.webcam = cv2.VideoCapture(camera_source)

        if not self.webcam.isOpened():
            self.view.display_message("Erreur", f"Impossible d'ouvrir la caméra {camera_source}", QMessageBox.Icon.Critical)
            self.camera_active = False
            return

        self.view.display_message("Info", f"Caméra connectée à {camera_source}")
        self.timer.start(30)
        self.camera_active = True
        self.view.set_camera_active(self.camera_active)

    def stop_camera(self):
        """Arrête la webcam."""
        if self.webcam and self.webcam.isOpened():
            self.timer.stop()
            self.webcam.release()
            self.webcam = None
            self.camera_active = False
            self.view.set_camera_active(False)
            self.view.display_message("Info", "Webcam fermée")
        else:
            self.view.display_message("Avertissement", "Aucune webcam n'est active.", QMessageBox.Icon.Warning)

    def update_frame(self):
        """Capture et affiche un frame de la caméra."""
        if self.webcam and self.webcam.isOpened():
            success, frame = self.webcam.read()
            if success:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.view.display_frame(frame_rgb)
            else:
                self.stop_camera()
                self.view.display_message("Avertissement", "Flux vidéo interrompu.", QMessageBox.Icon.Warning)

    def select_training_file(self, file_path):
        """Sélectionne et charge un fichier d'entraînement."""
        if file_path:
            self.training_file = file_path
            try:
                self.recognizer.read(self.training_file)
                self.view.update_recognize_button(True, "Démarrer Reconnaissance")
                self.view.display_message("Succès", f"Fichier chargé: {os.path.basename(self.training_file)}")
            except Exception as e:
                self.view.display_message("Erreur", f"Erreur chargement fichier: {e}", QMessageBox.Icon.Critical)

    def toggle_reconnaissance(self):
        """Active/Désactive la reconnaissance faciale."""
        if not self.webcam or not self.webcam.isOpened():
            self.view.display_message("Avertissement", "Démarrer la webcam d'abord.", QMessageBox.Icon.Warning)
            return

        if not self.training_file:
            self.view.display_message("Avertissement", "Sélectionner un fichier YAML d'entraînement.", QMessageBox.Icon.Warning)
            return

        self.is_recognizing = not self.is_recognizing
        btn_text = "Arrêter Reconnaissance" if self.is_recognizing else "Démarrer Reconnaissance"
        self.view.update_recognize_button(self.is_recognizing, btn_text)
