from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER

class IMAGE_VIEW(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Photos")
        self.photo_controller = IMAGE_CONTROLLER()
        self.chauffeur_controller = CHAUFFEUR_CONTROLLER()

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setSpacing(20)

        self.leftLayout = self.create_left_layout()
        self.rightLayout = self.create_right_layout()

        self.hboxLayout.addWidget(self.create_frame(self.leftLayout))
        self.hboxLayout.addWidget(self.create_frame(self.rightLayout))
        self.setLayout(self.hboxLayout)

    def create_left_layout(self):
        leftLayout = QVBoxLayout()

        title_label = self.create_label("AJOUTER L'IMAGE", object_name="titleLabel")
        leftLayout.addWidget(title_label)

        self.label_select_image = self.create_label("Sélectionner une image")
        self.select_image_button = self.create_button("Parcourir...", self.browse_image)
        leftLayout.addWidget(self.label_select_image)
        leftLayout.addWidget(self.select_image_button)

        self.label_url = self.create_label("URL")
        self.url_input = self.create_line_edit()
        leftLayout.addWidget(self.label_url)
        leftLayout.addWidget(self.url_input)

        self.create_button = self.create_button("Créer", self.create_photo)
        leftLayout.addWidget(self.create_button)

        return leftLayout

    def create_right_layout(self):
        rightLayout = QVBoxLayout()

        self.filter_input = self.create_line_edit("Filtrer par nom")
        self.filter_input.textChanged.connect(self.filter_chauffeurs)
        rightLayout.addWidget(self.filter_input)

        self.chauffeur_list_layout, self.scroll_area = self.create_scrollable_area()
        
        rightLayout.addWidget(self.scroll_area)

        self.chauffeur_radio_buttons = {}
        self.populate_chauffeur_list()

        return rightLayout

    def create_scrollable_area(self):
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_layout.setAlignment(Qt.AlignTop)
        list_widget.setLayout(list_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(list_widget)

        return list_layout, scroll_area

    def create_label(self, text, object_name=None):
        label = QLabel(text)
        if object_name:
            label.setObjectName(object_name)
        return label

    def create_line_edit(self, placeholder=None):
        line_edit = QLineEdit()
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        return line_edit

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.url_input.setText(file_path)

    def populate_chauffeur_list(self, chauffeurs=None):
        if chauffeurs is None:
            chauffeurs = self.chauffeur_controller.get_all_drivers()

        while self.chauffeur_list_layout.count():
            item = self.chauffeur_list_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        self.chauffeur_radio_buttons.clear()

        for chauffeur in chauffeurs:
            radio_button = QRadioButton(f"{chauffeur.nom} {chauffeur.prenom}")
            self.chauffeur_list_layout.addWidget(radio_button)
            self.chauffeur_radio_buttons[chauffeur.id] = radio_button

    def filter_chauffeurs(self, filter_text):
        chauffeurs = self.chauffeur_controller.get_all_drivers()
        filtered_chauffeurs = [
            chauffeur
            for chauffeur in chauffeurs
            if filter_text.lower() in f"{chauffeur.nom} {chauffeur.prenom}".lower()
        ]
        self.populate_chauffeur_list(filtered_chauffeurs)

    def create_photo(self):
        file_path = self.url_input.text()
        personne_id = next(
            (
                chauffeur_id
                for chauffeur_id, radio_button in self.chauffeur_radio_buttons.items()
                if radio_button.isChecked()
            ),
            None,
        )

        if file_path and personne_id:
            try:
                photo = self.photo_controller.add_photo(file_path, personne_id)
                if photo:
                    QMessageBox.information(self, "Succès", "Photo ajoutée avec succès.")
                else:
                    QMessageBox.warning(self, "Avertissement", "Échec de l'ajout de la photo.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de la photo : {e}")
        else:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une image et un chauffeur.")

    def create_frame(self, layout):
        frame = QFrame()
        frame.setObjectName("forme_frame")
        frame.setLayout(layout)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(1)
        return frame
