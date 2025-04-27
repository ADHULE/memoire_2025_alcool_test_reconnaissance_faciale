from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

import re

# importation des controllers
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER


class CHAUFFEUR_VIEW(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Chauffeurs")
        self.parent = parent
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.central_layout = QHBoxLayout()

        # Initialiser le QListView et QStandardItemModel
        self.list_view = QListView()
        self.list_view.setObjectName("list_view")
        self.list_model = QStandardItemModel(self.list_view)
        self.list_view.setModel(self.list_model)

        # Initialisation de contrôleurs
        self.chauffeur_controller = CHAUFFEUR_CONTROLLER()

        self.builded_UI()
        self.load_initial_data()  # Charger les données au démarrage

    def builded_UI(self):
        # Ajout des blocs gauche et droit (VLayout) dans une fenêtre (Frame), tous dans le bloc central (HLayout)
        self.central_layout.addWidget(self.create_frame(self.setup_left_layout()))
        self.central_layout.addWidget(self.create_frame(self.setup_right_layout()))
        self.setLayout(self.central_layout)

    def setup_left_layout(self):
        title_label = QLabel("ENREGISTRER LES CHAUFFEURS")
        title_label.setObjectName("titleLabel")
        self.left_layout.addWidget(title_label)

        self.left_layout.addStretch()

        self.nom_input = self.create_line_edit(
            self.create_label("Nom"), "Nom du chauffeur..."
        )
        self.left_layout.addWidget(self.nom_input)

        self.postnom_input = self.create_line_edit(
            self.create_label("Post-Nom"), "Post-nom du chauffeur..."
        )
        self.left_layout.addWidget(self.postnom_input)

        self.prenom_input = self.create_line_edit(
            self.create_label("Prénom"), "Prénom du chauffeur..."
        )
        self.left_layout.addWidget(self.prenom_input)

        self.phone_input = self.create_line_edit(
            self.create_label("Numéro de téléphone"),
            "Numéro de téléphone du chauffeur...",
        )
        self.left_layout.addWidget(self.phone_input)

        self.email_input = self.create_line_edit(
            self.create_label("Email"), "Email du chauffeur..."
        )
        self.left_layout.addWidget(self.email_input)

        self.permis_input = self.create_line_edit(
            self.create_label("Numéro de permis"), "Numéro du permis de conduire..."
        )
        self.left_layout.addWidget(self.permis_input)

        button_layout = self.create_button("Enregistrer", self.enregistrer_chauffeur)
        self.left_layout.addWidget(button_layout)

        self.left_layout.addStretch()
        return self.left_layout

    def setup_right_layout(self):
        layout = QVBoxLayout()

        self.search_input_container = self.create_line_edit_with_label(
            "Rechercher un chauffeur par...",
            "Entrez un mot clé...",
        )
        layout.addWidget(self.search_input_container)
        self.search_input_line_edit = self.search_input_container.findChild(QLineEdit)
        if self.search_input_line_edit:
            self.search_input_line_edit.textChanged.connect(self.filter_chauffeur)
        else:
            print("Erreur: Impossible de trouver le QLineEdit dans le widget de recherche.")

        layout.addWidget(self.list_view)
        self.list_view.selectionModel().selectionChanged.connect(self.on_item_selection_changed)

        refresh_button = QPushButton("Rafraîchir")
        refresh_button.clicked.connect(self.load_chauffeurs)
        layout.addWidget(refresh_button)

        return layout

    def create_label(self, text, object_name=None):
        label = QLabel(text)
        label.adjustSize()
        label.setWordWrap(True)
        if object_name:
            label.setObjectName(object_name)
        return label

    def create_line_edit(self, label, placeholdertext=None, object_name=None):
        widget = QWidget()
        layout = QVBoxLayout()
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholdertext)
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(label)
        layout.addWidget(line_edit)
        widget.setLayout(layout)
        return widget

    def create_line_edit_with_label(self, label_text, placeholdertext=None, object_name=None):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholdertext)
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(label)
        layout.addWidget(line_edit)
        widget.setLayout(layout)

        if object_name:
            line_edit.setObjectName(object_name)

        return widget

    def create_button(self, text, callback):
        button = QPushButton(text)
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(button)
        layout.addStretch()

        button.clicked.connect(callback)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def create_frame(self, layout):
        frame = QFrame()
        frame.setObjectName("forme_frame")
        frame.setLayout(layout)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(1)
        return frame

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(
            QMessageBox.Information if title == "Succès" else QMessageBox.Critical
        )
        msg_box.exec()

    """_____________________________MANIPULATIONS DES DONNEES__________________________________"""

    def enregistrer_chauffeur(self):
        try:
            # Récupération des valeurs des champs
            nom = self.nom_input.layout().itemAt(1).widget().text().strip()
            postnom = self.postnom_input.layout().itemAt(1).widget().text().strip()
            prenom = self.prenom_input.layout().itemAt(1).widget().text().strip()
            phone = self.phone_input.layout().itemAt(1).widget().text().strip()
            email = self.email_input.layout().itemAt(1).widget().text().strip()
            numero_permis = self.permis_input.layout().itemAt(1).widget().text().strip()

            # Vérification des champs obligatoires
            if not nom or not postnom or not prenom or not phone or not numero_permis:
                self.show_message("Erreur", "Veuillez compléter tous les champs sauf l'email qui peut rester vide.")
                return  # Arrêter l'exécution si des champs sont vides

            # Vérification du format du téléphone (doit contenir uniquement des chiffres)
            if not phone.isdigit():
                self.show_message("Erreur", "Le numéro de téléphone doit contenir uniquement des chiffres.")
                return

            # Vérification du format de l'email (valide mais facultatif)
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if email and not re.match(email_pattern, email):
                self.show_message("Erreur", "L'adresse email n'est pas valide.")
                return

            # Enregistrement du chauffeur
            self.chauffeur_controller.new_Driver(nom, postnom, prenom, phone, email, numero_permis)
            self.show_message("Succès", "Nouveau chauffeur enregistré avec succès.")

            # Nettoyage des champs et rechargement de la liste
            self.clear_fields()
            self.load_chauffeurs()

        except Exception as e:
            print("Erreur lors de l'enregistrement du chauffeur:", str(e))
            self.show_message("Erreur", f"Une erreur s'est produite : {str(e)}")

    def clear_fields(self):
        """Efface le contenu des champs de saisie."""
        self.nom_input.layout().itemAt(1).widget().clear()
        self.postnom_input.layout().itemAt(1).widget().clear()
        self.prenom_input.layout().itemAt(1).widget().clear()
        self.phone_input.layout().itemAt(1).widget().clear()
        self.email_input.layout().itemAt(1).widget().clear()
        self.permis_input.layout().itemAt(1).widget().clear()

    def load_chauffeurs(self):
        try:
            chauffeurs = self.chauffeur_controller.get_all_drivers()
            self.populate_list(chauffeurs)
        except Exception as e:
            self.show_message(
                "Erreur", f"Erreur lors du chargement des chauffeurs : {str(e)}"
            )

    def populate_list(self, liste_chauffeurs):
        self.list_model.clear()
        for chauffeur in liste_chauffeurs:
            item_text = (
                f"{chauffeur.nom} {chauffeur.postnom}, {chauffeur.prenom}, "
                f"Tél: {chauffeur.telephone}, Email: {chauffeur.email if chauffeur.email else 'N/A'}, "
                f"Permis: {chauffeur.numero_permis}"
            )
            item = QStandardItem(item_text)

            layout = QHBoxLayout()
            layout.addWidget(QLabel(item_text))

            modify_button = QPushButton("Modifier")
            modify_button.setObjectName("modify_button")
            modify_button.clicked.connect(
                lambda _, id=chauffeur.id: self.modify_chauffeur(id)
            )
            modify_button.setVisible(False)
            layout.addWidget(modify_button)

            delete_button = QPushButton("Supprimer")
            delete_button.setObjectName("delete_button")
            delete_button.clicked.connect(
                lambda _, id=chauffeur.id: self.delete_chauffeur(id)
            )
            delete_button.setVisible(False)
            layout.addWidget(delete_button)

            layout.addStretch()
            container_widget = QWidget()
            container_widget.setLayout(layout)

            item.setSizeHint(container_widget.sizeHint())
            self.list_model.appendRow(item)
            self.list_view.setIndexWidget(item.index(), container_widget)

    def on_item_selection_changed(self, selected, deselected):
        for index in selected.indexes():
            item_widget = self.list_view.indexWidget(index)
            if item_widget:
                modify_button = item_widget.findChild(QPushButton, "modify_button")
                delete_button = item_widget.findChild(QPushButton, "delete_button")
                if modify_button and delete_button:
                    modify_button.setVisible(True)
                    delete_button.setVisible(True)

        for index in deselected.indexes():
            item_widget = self.list_view.indexWidget(index)
            if item_widget:
                modify_button = item_widget.findChild(QPushButton, "modify_button")
                delete_button = item_widget.findChild(QPushButton, "delete_button")
                if modify_button and delete_button:
                    modify_button.setVisible(False)
                    delete_button.setVisible(False)

    def modify_chauffeur(self, chauffeur_id):
        try:
            self.parent.open_modify_chauffeur_page(chauffeur_id)
        except AttributeError:
            self.show_message("Erreur", "La fenêtre de modification n'est pas implémentée dans la fenêtre parente.")
        except Exception as e:
            self.show_message(
                "Erreur",
                f"Erreur lors de la modification du chauffeur : {type(e).__name__} - {str(e)}",
            )

    def delete_chauffeur(self, chauffeur_id):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer ce chauffeur ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.chauffeur_controller.delete_driver(chauffeur_id)
                self.show_message("Succès", "Chauffeur supprimé avec succès.")
                self.load_chauffeurs()
            except Exception as e:
                self.show_message("Erreur", f"Erreur lors de la suppression : {str(e)}")

    def filter_chauffeur(self, search_text):
        try:
            chauffeurs = self.chauffeur_controller.get_all_drivers()
            filtered_chauffeurs = []
            for chauffeur in chauffeurs:
                search_string = (
                    f"{chauffeur.nom} {chauffeur.postnom} {chauffeur.prenom} "
                    f"{chauffeur.telephone} {chauffeur.email if chauffeur.email else ''} "
                    f"{chauffeur.numero_permis}".lower()
                )
                if search_text.lower() in search_string:
                    filtered_chauffeurs.append(chauffeur)
            self.populate_list(filtered_chauffeurs)
        except Exception as e:
            self.show_message("Erreur", f"Erreur lors du filtrage : {str(e)}")

    def load_initial_data(self):
        """Charge les données initiales au démarrage de la vue."""
        self.load_chauffeurs()
