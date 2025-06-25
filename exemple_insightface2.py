# --- IMPORTATION DES MODULES ---
import cv2  # OpenCV pour capturer la vidéo et afficher les images
import numpy as np  # Pour les calculs mathématiques sur les vecteurs d'embedding
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QMessageBox, QGroupBox,
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer, Signal

# Tente d'importer InsightFace. Si non disponible, affiche un message d'erreur.
try:
    from insightface.app import FaceAnalysis

    INSIGHTFACE_AVAILABLE = True
except ImportError:
    print("ATTENTION : Le module InsightFace n'a pas été trouvé.")
    print("La reconnaissance faciale ne sera pas fonctionnelle sans InsightFace.")
    print("Assurez-vous de l'avoir installé (par exemple, 'pip install insightface').")
    INSIGHTFACE_AVAILABLE = False


class FaceRecognitionApp(QMainWindow):
    # --- SIGNALS CUSTOMISÉS ---
    # Signal émis lorsque de nouveaux cadres vidéo sont disponibles
    # Cela permet de mettre à jour l'interface graphique de manière sûre depuis un thread différent si nécessaire (ici, QTimer est dans le même thread principal)
    frame_ready = Signal(QImage)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application de Reconnaissance Faciale")
        self.setGeometry(100, 100, 1000, 700)  # (x, y, width, height)

        # --- INITIALISATION DE INSIGHTFACE ---
        self.app = None
        if INSIGHTFACE_AVAILABLE:
            try:
                # On crée une instance de l'analyseur avec le modèle 'buffalo_l'
                # Le provider 'CPUExecutionProvider' signifie qu'on utilise le processeur
                self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
                self.app.prepare(ctx_id=0)  # ctx_id=0 indique l'utilisation du CPU
            except Exception as e:
                QMessageBox.critical(self, "Erreur InsightFace",
                                     f"Impossible d'initialiser InsightFace : {e}\n"
                                     "Assurez-vous que tous les dépendances sont installées et que le modèle 'buffalo_l' est téléchargé.")
                self.app = None  # Désactiver InsightFace si l'initialisation échoue

        # --- DÉFINITION DE LA BASE DE DONNÉES DE VISAGES ---
        self.face_db = []  # Cette liste contiendra tous les profils avec leurs embeddings

        # --- INITIALISATION DE LA CAMÉRA ---
        self.cap = None  # Objet de capture vidéo OpenCV
        self.timer = QTimer(self)  # Timer pour mettre à jour le flux vidéo
        self.timer.timeout.connect(self.update_frame)  # Connecte le timer à la méthode de mise à jour

        # --- INTERFACE UTILISATEUR (UI) ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # --- Section Gauche : Flux Vidéo et Contrôles ---
        self.video_panel = QVBoxLayout()

        self.video_label = QLabel("Chargement de la caméra...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(640, 480)  # Taille fixe pour le flux vidéo
        self.video_label.setStyleSheet("background-color: black; border: 2px solid gray;")
        self.video_panel.addWidget(self.video_label)

        self.control_buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Démarrer Caméra")
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button = QPushButton("Arrêter Caméra")
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)  # Désactivé au démarrage

        self.control_buttons_layout.addWidget(self.start_button)
        self.control_buttons_layout.addWidget(self.stop_button)
        self.video_panel.addLayout(self.control_buttons_layout)

        self.main_layout.addLayout(self.video_panel)

        # --- Section Droite : Gestion de la Base de Données des Visages ---
        # Déplacé l'initialisation de ces éléments UI AVANT _load_initial_faces()
        self.db_panel = QVBoxLayout()

        # Groupement pour ajouter un nouveau visage
        self.add_face_group = QGroupBox("Ajouter un Visage à la Base")
        self.add_face_layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom de la personne")
        self.add_face_layout.addWidget(QLabel("Nom:"))
        self.add_face_layout.addWidget(self.name_input)

        self.image_path_label = QLabel("Aucune image sélectionnée.")
        self.add_face_layout.addWidget(self.image_path_label)

        self.browse_button = QPushButton("Parcourir Image...")
        self.browse_button.clicked.connect(self.browse_image)
        self.add_face_layout.addWidget(self.browse_button)

        self.add_button = QPushButton("Ajouter Visage")
        self.add_button.clicked.connect(self.add_face_to_db)
        self.add_face_layout.addWidget(self.add_button)

        self.add_face_group.setLayout(self.add_face_layout)
        self.db_panel.addWidget(self.add_face_group)

        # Groupement pour les visages enregistrés
        self.registered_faces_group = QGroupBox("Visages Enregistrés")
        self.registered_faces_layout = QVBoxLayout()
        self.registered_faces_list = QListWidget()  # C'est ici que self.registered_faces_list est initialisé
        self.registered_faces_layout.addWidget(self.registered_faces_list)
        self.registered_faces_group.setLayout(self.registered_faces_layout)
        self.db_panel.addWidget(self.registered_faces_group)

        self.main_layout.addLayout(self.db_panel)

        # --- Connecter le signal frame_ready au label vidéo (sécurisé) ---
        self.frame_ready.connect(lambda img: self.video_label.setPixmap(QPixmap.fromImage(img)))

        # Maintenant, nous pouvons charger les visages initiaux et mettre à jour la liste en toute sécurité
        self._load_initial_faces()  # Charge des visages prédéfinis au démarrage
        self._update_registered_faces_list()  # Met à jour la liste des visages enregistrés à l'interface graphique

    def _load_initial_faces(self):
        """Charge des visages prédéfinis au démarrage de l'application."""
        # Exemple: Ajouter un visage depuis un fichier local
        # Assurez-vous que 'systeme_adhule.jpeg' existe dans le même répertoire que ce script
        # ou fournissez le chemin complet.
        initial_image_path = "systeme_adhule.jpeg"
        if INSIGHTFACE_AVAILABLE and self.app:
            self._add_face_from_path(initial_image_path, "Adhule", initial_load=True)
        else:
            print(f"Impossible d'ajouter {initial_image_path} car InsightFace n'est pas disponible ou initialisé.")

    def _add_face_from_path(self, image_path, name, initial_load=False):
        """
        Fonction interne pour ajouter un visage à la base de données à partir d'un chemin d'image.
        Utilisée par ajouter_personne et _load_initial_faces.
        """
        if not self.app:
            if not initial_load:  # Éviter les popups à l'initialisation si InsightFace est absent
                QMessageBox.critical(self, "Erreur", "Le moteur de reconnaissance faciale n'est pas initialisé.")
            return

        img = cv2.imread(image_path)  # Chargement de l'image
        if img is None:
            if not initial_load:
                QMessageBox.warning(self, "Erreur Image", f"Image introuvable : {image_path}")
            else:
                print(f"⚠️ Image initiale introuvable : {image_path}")
            return

        faces = self.app.get(img)  # Détection de visages dans l'image
        if not faces:
            if not initial_load:
                QMessageBox.warning(self, "Pas de Visage",
                                    f"Aucun visage détecté dans l'image sélectionnée pour {name}.")
            else:
                print(f"⚠️ Aucun visage détecté dans l'image initiale de {name}")
            return

        embedding = faces[0].embedding  # Récupération de l'embedding du premier visage
        self.face_db.append({
            "nom": name,
            "embedding": embedding
        })
        if not initial_load:
            QMessageBox.information(self, "Succès", f"{name} a été ajouté à la base de données.")
        else:
            print(f"✅ {name} a été ajouté à la base de données (initialisation).")
        self._update_registered_faces_list()

    def browse_image(self):
        """Ouvre une boîte de dialogue pour sélectionner une image."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.selected_image_path = selected_files[0]
                self.image_path_label.setText(f"Image sélectionnée : {self.selected_image_path.split('/')[-1]}")
            else:
                self.selected_image_path = None
                self.image_path_label.setText("Aucune image sélectionnée.")

    def add_face_to_db(self):
        """Ajoute une personne à la base de données de visages."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Champ Manquant", "Veuillez entrer un nom pour la personne.")
            return
        if not hasattr(self, 'selected_image_path') or not self.selected_image_path:
            QMessageBox.warning(self, "Image Manquante", "Veuillez sélectionner une image de la personne.")
            return

        self._add_face_from_path(self.selected_image_path, name)
        # Réinitialiser les champs après l'ajout
        self.name_input.clear()
        self.selected_image_path = None
        self.image_path_label.setText("Aucune image sélectionnée.")

    def _update_registered_faces_list(self):
        """Met à jour la liste affichée des visages enregistrés."""
        self.registered_faces_list.clear()
        if not self.face_db:
            self.registered_faces_list.addItem("Aucun visage enregistré pour le moment.")
        else:
            for profil in self.face_db:
                self.registered_faces_list.addItem(profil["nom"])

    def start_camera(self):
        """Démarre la capture vidéo de la caméra."""
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)  # 0 = première caméra trouvée
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Erreur Caméra", "Impossible d'accéder à la caméra.")
                self.cap = None
                return

        self.timer.start(30)  # Met à jour le cadre toutes les 30 ms (~33 FPS)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_camera(self):
        """Arrête la capture vidéo et libère les ressources."""
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.setText("Caméra arrêtée.")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_frame(self):
        """
        Capture un cadre de la caméra, effectue la reconnaissance faciale
        et met à jour l'affichage dans l'interface graphique.
        """
        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop_camera()
            QMessageBox.critical(self, "Erreur Caméra", "Échec de la lecture du cadre de la caméra.")
            return

        # Convertit l'image en RGB pour InsightFace et PySide6
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.app:  # N'exécute la reconnaissance que si InsightFace est initialisé
            faces = self.app.get(frame_rgb)  # Détecte tous les visages dans l'image

            for face in faces:
                bbox = face.bbox.astype(int)  # Coordonnées du visage détecté
                # Dessine un rectangle autour du visage
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)

                personne_trouvee = "Inconnu"  # Valeur par défaut si aucun match
                meilleur_score = 0.0  # Initialisation du meilleur score de ressemblance

                # Boucle sur tous les visages enregistrés pour comparer
                for profil in self.face_db:
                    score, match = self._comparer(face.embedding, profil["embedding"])
                    if match and score > meilleur_score:
                        personne_trouvee = profil["nom"]  # On garde le nom de la personne correspondante
                        meilleur_score = score  # On enregistre le meilleur score obtenu

                # Récupère le sexe estimé automatiquement (male/female)
                sexe = face.sex.capitalize() if hasattr(face, "sex") else "Inconnu"
                # Récupère l'âge estimé automatiquement
                age = int(face.age) if hasattr(face, "age") else "?"

                # Prépare une étiquette à afficher
                etiquette = f"{personne_trouvee} ({sexe}, {age} ans, Score: {meilleur_score:.2f})"

                # Affiche l'étiquette au-dessus du visage détecté
                cv2.putText(frame, etiquette, (bbox[0], bbox[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)  # Couleur jaune pour le texte

        # Convertit l'image OpenCV (BGR) en QImage pour PySide6
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        # Utiliser QImage.Format_BGR888 car frame est en BGR
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)

        # Émet le signal avec l'image pour la mettre à jour dans le QLabel
        self.frame_ready.emit(q_img)

    def _comparer(self, emb1, emb2, seuil=0.65):
        """
        Calcule la similarité cosinus entre deux embeddings.
        Retourne le score et si c'est au-dessus du seuil.
        """
        # Calcule la similarité entre deux vecteurs
        # Assurez-vous que les embeddings sont des numpy arrays
        emb1 = np.asarray(emb1)
        emb2 = np.asarray(emb2)

        # Empêcher la division par zéro si un vecteur a une norme de zéro
        norm_emb1 = np.linalg.norm(emb1)
        norm_emb2 = np.linalg.norm(emb2)

        if norm_emb1 == 0 or norm_emb2 == 0:
            return 0.0, False  # Retourne 0 et pas de correspondance si un vecteur est nul

        similarity = np.dot(emb1, emb2) / (norm_emb1 * norm_emb2)
        return similarity, similarity > seuil

    def closeEvent(self, event):
        """
        Gère la fermeture de l'application pour libérer les ressources de la caméra.
        """
        self.stop_camera()  # S'assure que la caméra est arrêtée proprement
        super().closeEvent(event)


# --- POINT D'ENTRÉE DE L'APPLICATION ---
if __name__ == "__main__":
    app = QApplication([])
    window = FaceRecognitionApp()
    window.show()
    app.exec()
