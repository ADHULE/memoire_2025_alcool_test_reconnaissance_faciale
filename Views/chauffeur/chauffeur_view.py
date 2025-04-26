from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import re  # permet de gerer le format de l'annee
from Controllers.chauffeur_controller import Chauffeur_Controller

class Chauffeur_View(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chauffeurs")
        self.parent = parent
        self.chauffeur_controller = Chauffeur_Controller
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.central_layout = QHBoxLayout()

        # Initialiser le QListView et QStandardItemModel
        self.list_view = QListView()
        self.list_view.setObjectName("list_view")
        self.list_model = QStandardItemModel(self.list_view)
        self.list_view.setModel(self.list_model)

        self.builded_UI()
        self.load_chauffeurs()

    def builded_UI(self):
        # ajout des blocs gauch et droit (VLayout) dans une fenetre (Frame) les tous dans bloc central (HLayout)
        self.central_layout.addWidget(self.create_frame(self.setup_left_layout()))
        self.central_layout.addWidget(self.create_frame(self.setup_right_layout()))
        self.setLayout(self.central_layout)

    def setup_left_layout(self):
        title_label = QLabel("ENREGISTRER UN CHAUFFEUR")
        title_label.setObjectName("titleLabel")
        self.left_layout.addWidget(title_label)

        self.left_layout.addStretch()

        self.nom_input = self.create_line_edit(
            self.create_label("Nom"), "Entrer le nom du chauffeur"
        )
        self.left_layout.addLayout(self.nom_input)

        self.postnom_input = self.create_line_edit(
            self.create_label("Post-Nom"), "Entrer le postnom du chauffeur"
        )
        self.left_layout.addLayout(self.postnom_input)

        self.prenom_input = self.create_line_edit(
            self.create_label("Prénom"), "Entrer le prénom du chauffeur"
        )
        self.left_layout.addLayout(self.prenom_input)

        self.phone_input = self.create_line_edit(
            self.create_label("Numéro de Téléphone"),
            "Entrer le numéro de téléphone du chauffeur",
        )
        self.left_layout.addLayout(self.phone_input)

        self.email_input = self.create_line_edit(
            self.create_label("Email"), "Entrer l'email ou laisser vide"
        )
        self.left_layout.addLayout(self.email_input)

        self.permis_input = self.create_line_edit(
            self.create_label("Numéro de Permis"), "Entrer le numéro de permis du chauffeur"
        )
        self.left_layout.addLayout(self.permis_input)

        self.create_button = self.create_button("Créer", self.create_chauffeur)

        self.left_layout.addLayout(self.create_button)

        self.left_layout.addStretch()
        return self.left_layout

    def setup_right_layout(self):
        layout = QVBoxLayout()  # Créer un layout vertical

        self.search_input = self.create_line_edit(
            self.create_label("Rechercher un chauffeur par..."),
            "Entrer un mot pour chercher...",
        )
        layout.addLayout(self.search_input)

        self.search_input.itemAt(1).widget().textChanged.connect(
            self.filter_chauffeurs
        )  # add search function

        # aficher la liste de tout etudiants
        self.list_view.selectionModel().selectionChanged.connect(
            self.on_item_selection_changed
        )

        layout.addWidget(self.list_view)
        refresh_button = QPushButton("Rafraîchir")  # add refresh button
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

    # Les méthodes load_facultes, load_departements et load_promotions ne sont plus nécessaires

    def create_chauffeur(self):
        nom = self.nom_input.itemAt(1).widget().text()
        postnom = self.postnom_input.itemAt(1).widget().text()
        prenom = self.prenom_input.itemAt(1).widget().text()
        phone = self.phone_input.itemAt(1).widget().text()
        email = (
            self.email_input.itemAt(1).widget().text().strip()
            if self.email_input.itemAt(1).widget().text().strip()
            else None
        )
        numero_permis = self.permis_input.itemAt(1).widget().text().strip()

        if not nom or not postnom or not prenom or not phone or not numero_permis:
            self.show_message(
                "Erreur", "Veuillez remplir tous les champs obligatoires."
            )
            return

        try:
            if self.chauffeur_controller:
                self.chauffeur_controller.new_Driver(
                    nom, postnom, prenom, phone, email, numero_permis
                )
                self.show_message("Succès", "Chauffeur créé avec succès.")
                self.clear_fields()
                self.load_chauffeurs()
            else:
                self.show_message(
                    "Erreur", "Le contrôleur de chauffeur n'est pas initialisé."
                )
        except Exception as e:
            self.show_message(
                "Erreur", f"Erreur lors de la création du chauffeur : {str(e)}"
            )

    def clear_fields(self):
        self.nom_input.itemAt(1).widget().clear()
        self.postnom_input.itemAt(1).widget().clear()
        self.prenom_input.itemAt(1).widget().clear()
        self.phone_input.itemAt(1).widget().clear()
        self.email_input.itemAt(1).widget().clear()
        self.permis_input.itemAt(1).widget().clear()

    def load_chauffeurs(self):
        try:
            if self.chauffeur_controller:
                chauffeurs = self.chauffeur_controller.get_all_drivers()
                self.populate_list(chauffeurs)
            else:
                self.show_message(
                    "Erreur", "Le contrôleur de chauffeur n'est pas initialisé."
                )
        except Exception as e:
            self.show_message(
                "Erreur", f"Erreur lors du chargement des chauffeurs : {str(e)}"
            )

    def populate_list(self, liste_chauffeurs):
        self.list_model.clear()
        for chauffeur in liste_chauffeurs:
            item_text = (
                f"{chauffeur.nom} {chauffeur.postnom}, {chauffeur.prenom} - "
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
            if self.parent and hasattr(self.parent, "open_modify_chauffeur_page"):
                self.parent.open_modify_chauffeur_page(chauffeur_id)
            else:
                self.show_message(
                    "Erreur", "La fonction de modification n'est pas disponible."
                )
        except Exception as e:
            self.show_message(
                "Erreur",
                f"Erreur lors de la modification : {type(e).__name__} - {str(e)}",
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
                if self.chauffeur_controller:
                    self.chauffeur_controller.delete_driver(chauffeur_id)
                    self.show_message("Succès", "Chauffeur supprimé avec succès.")
                    self.load_chauffeurs()
                else:
                    self.show_message(
                        "Erreur", "Le contrôleur de chauffeur n'est pas initialisé."
                    )
            except Exception as e:
                self.show_message("Erreur", f"Erreur lors de la suppression : {str(e)}")

    def filter_chauffeurs(self, search_text):
        try:
            if self.chauffeur_controller:
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
            else:
                self.show_message(
                    "Erreur", "Le contrôleur de chauffeur n'est pas initialisé."
                )
        except Exception as e:
            self.show_message("Erreur", f"Erreur lors du filtrage : {str(e)}")

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(
            QMessageBox.Information if title == "Succès" else QMessageBox.Critical
        )
        msg_box.exec()

    def create_frame(self, layout):
        frame = QFrame()
        frame.setObjectName("forme_frame")
        frame.setLayout(layout)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(1)
        return frame