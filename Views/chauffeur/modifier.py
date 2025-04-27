from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

import re  # Utilisé pour la validation du format de l'année académique
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER

class MDIFIER_CHAUFFEUR(QDialog):
    def __init__(self, etudiant_id, parent=None):
        super().__init__(parent)
        self.etudiant_id = etudiant_id
        self.setWindowTitle("Modifier les informations de l'étudiant")
        self.main_layout = QVBoxLayout()  # Utilisation d'un seul layout vertical

        # Initialisation des contrôleurs
       

        self.setLayout(self.setup_ui())
        self.load_etudiant_data()

    def setup_ui(self):
        title_label = QLabel("MODIFIER LES INFORMATIONS DE L'ÉTUDIANT")
        title_label.setObjectName("titleLabel")
        self.main_layout.addWidget(title_label)

        self.nom_input = self.create_line_edit(
            self.create_label("Nom"), "Entrer le nom de l'étudiant"
        )
        self.main_layout.addLayout(self.nom_input)

        self.postnom_input = self.create_line_edit(
            self.create_label("Post-Nom"), "Entrer le postnom de l'étudiant"
        )
        self.main_layout.addLayout(self.postnom_input)

        self.prenom_input = self.create_line_edit(
            self.create_label("Prénom"), "Entrer le prénom de l'étudiant"
        )
        self.main_layout.addLayout(self.prenom_input)

        self.phone_input = self.create_line_edit(
            self.create_label("Phone Number"),
            "Entrer le numéro de téléphone de l'étudiant",
        )
        self.main_layout.addLayout(self.phone_input)

        self.email_input = self.create_line_edit(
            self.create_label("Email"), "Entrer l'email ou laisser vide de l'étudiant"
        )
        self.main_layout.addLayout(self.email_input)

        self.faculte_combobox = QComboBox()
        self.faculte_id_input = self.create_combobox(
            self.create_label("Faculté"), self.faculte_combobox, "faculte_combobox"
        )
        self.main_layout.addLayout(self.faculte_id_input)

        self.departement_combobox = QComboBox()
        self.departement_id_input = self.create_combobox(
            self.create_label("Département"),
            self.departement_combobox,
            "departement_combobox",
        )
        self.main_layout.addLayout(self.departement_id_input)

        self.promotion_combobox = QComboBox()
        self.promotion_id_input = self.create_combobox(
            self.create_label("Promotion"),
            self.promotion_combobox,
            "promotion_combobox",
        )
        self.main_layout.addLayout(self.promotion_id_input)

        self.create_button_layout = self.create_button("Modifier", self.modify_etudiant)
        self.main_layout.addLayout(self.create_button_layout)

        # appelle des fonctions afin de les utilisées
        self.load_departements()
        self.load_facultes()
        self.load_promotions()

        return self.main_layout

    def create_label(self, text, object_name=None):
        label = QLabel(text)
        label.adjustSize()
        label.setWordWrap(True)
        if object_name:
            label.setObjectName(object_name)
        return label

    def create_line_edit(self, label, placeholdertext=None, object_name=None):
        line_edit = QLineEdit()
        line_edit.adjustSize()
        line_edit.setPlaceholderText(placeholdertext)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(line_edit)
        if object_name:
            line_edit.setObjectName(object_name)
        return layout

    def create_button(self, text, callback, object_name=None):
        button = QPushButton(text)
        button.adjustSize()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(button)
        layout.addStretch()
        if object_name:
            button.setObjectName(object_name)
        if callback:
            button.clicked.connect(callback)
        return layout

    def create_combobox(self, label, combobox, object_name=None):
        layout = QHBoxLayout()
        if object_name:
            combobox.setObjectName(object_name)
        layout.addWidget(label)
        layout.addWidget(combobox)
        return layout

    def load_facultes(self):
        try:
            facultes = self.faculte_controller.get_facultes()
            self.faculte_combobox.clear()
            for faculte in facultes:
                self.faculte_combobox.addItem(faculte.nom, faculte.id)
        except Exception as e:
            self.show_message("Erreur", f"Une erreur est survenue : {str(e)}")

    def load_departements(self):
        try:
            departements = self.departement_controller.get_departements()
            self.departement_combobox.clear()
            for departement in departements:
                self.departement_combobox.addItem(departement.nom, departement.id)
        except Exception as e:
            self.show_message(
                "Erreur",
                f"Une erreur est survenue lors de chargement de departements : {str(e)}",
            )

    def load_promotions(self):
        try:
            promotions = self.promotion_controller.get_promotions()
            liste_promotions = {
                liste.id: liste.nom
                for liste in self.liste_nom_promotion_controller.read_all_liste()
            }
            self.promotion_combobox.clear()
            for promotion in promotions:
                liste_nom = liste_promotions.get(promotion.id_liste, "Inconnu")
                self.promotion_combobox.addItem(liste_nom, promotion.id)
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors du chargement des promotions : {str(e)}"
            )

    def load_etudiant_data(self):
        try:
            etudiant = self.etudiant_controller.get_etudiant_by_id(self.etudiant_id)
            self.nom_input.itemAt(1).widget().setText(etudiant.nom)
            self.postnom_input.itemAt(1).widget().setText(etudiant.postnom)
            self.prenom_input.itemAt(1).widget().setText(etudiant.prenom)
            self.phone_input.itemAt(1).widget().setText(etudiant.phone)
            self.email_input.itemAt(1).widget().setText(etudiant.email or "")

            faculte_index = self.faculte_combobox.findData(etudiant.faculte_id)
            if faculte_index != -1:
                self.faculte_combobox.setCurrentIndex(faculte_index)

            departement_index = self.departement_combobox.findData(
                etudiant.departement_id
            )
            if departement_index != -1:
                self.departement_combobox.setCurrentIndex(departement_index)

            promotion_index = self.promotion_combobox.findData(etudiant.promotion_id)
            if promotion_index != -1:
                self.promotion_combobox.setCurrentIndex(promotion_index)

        except Exception as e:
            self.show_message(
                "Erreur",
                f"Erreur lors du chargement des données de l'étudiant : {str(e)}",
            )

    def modify_etudiant(self):
        nom = self.nom_input.itemAt(1).widget().text()
        postnom = self.postnom_input.itemAt(1).widget().text()
        prenom = self.prenom_input.itemAt(1).widget().text()
        phone = self.phone_input.itemAt(1).widget().text()
        email = (
            self.email_input.itemAt(1).widget().text().strip()
            if self.email_input.itemAt(1).widget().text().strip()
            else None
        )
        faculte_id = self.faculte_combobox.currentData()
        departement_id = self.departement_combobox.currentData()
        promotion_id = self.promotion_combobox.currentData()

        if not nom or not postnom or not prenom or not phone:
            self.show_message(
                "Erreur", "Veuillez remplir tous les champs obligatoires."
            )
            return

        self.etudiant_controller.update_etudiant(
            self.etudiant_id,
            nom,
            postnom,
            prenom,
            phone,
            email,
            faculte_id,
            departement_id,
            promotion_id,
        )
        self.show_message("Succès", "Étudiant modifié avec succès.")
        self.accept()

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)