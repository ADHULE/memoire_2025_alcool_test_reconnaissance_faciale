from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

import re
from datetime import datetime

# importation des controllers
from Controllers.administrateur_controller import ADMINISTRATEUR_CONTROLLER


class ENREGISTREMENT_ADMIN(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Administrateurs")
        self.parent = parent
        self.admin_controller = ADMINISTRATEUR_CONTROLLER()

        # Layout principal
        self.main_layout = QVBoxLayout()

        # Groupes pour organiser les champs
        self.form_group = QGroupBox("Informations de l'Administrateur")
        self.form_layout = QGridLayout()
        self.list_group = QGroupBox("Liste des Administrateurs")
        self.list_layout = QVBoxLayout()
        self.search_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()

        self.list_view = QListView()
        self.list_model = QStandardItemModel(self.list_view)
        self.list_view.setModel(self.list_model)

        self.selected_admin_id = None  # Pour suivre l'ID de l'admin sélectionné pour la modification
        self.password_input = None  # Pour le champ de mot de passe
        self.nom_input = None
        self.postnom_input = None
        self.prenom_input = None
        self.phone_input = None
        self.email_input = None
        self.username_input = None
        self.role_input = None
        self.is_active_checkbox = None
        self.super_admin_checkbox = None

        self.enregistrer_button = None
        self.modifier_button = None
        self.refresh_button = None
        self.search_input = None
        self.show_password_checkbox = None

        self._build_ui()
        self._load_initial_data()

    def _build_ui(self):
        """Construit l'interface utilisateur moderne."""
        # Layout principal
        title_label = QLabel("Gestion des Administrateurs")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)

        # Formulaire d'enregistrement / modification
        self.nom_input = self._create_input_field("Nom")
        self.form_layout.addWidget(QLabel("Nom:"), 0, 0)
        self.form_layout.addWidget(self.nom_input, 0, 1)

        self.postnom_input = self._create_input_field("Post-Nom")
        self.form_layout.addWidget(QLabel("Post-Nom:"), 1, 0)
        self.form_layout.addWidget(self.postnom_input, 1, 1)

        self.prenom_input = self._create_input_field("Prénom")
        self.form_layout.addWidget(QLabel("Prénom:"), 2, 0)
        self.form_layout.addWidget(self.prenom_input, 2, 1)

        self.phone_input = self._create_input_field("Numéro de téléphone")
        self.form_layout.addWidget(QLabel("Téléphone:"), 3, 0)
        self.form_layout.addWidget(self.phone_input, 3, 1)

        self.email_input = self._create_input_field("Email")
        self.form_layout.addWidget(QLabel("Email:"), 4, 0)
        self.form_layout.addWidget(self.email_input, 4, 1)

        self.username_input = self._create_input_field("Nom d'utilisateur")
        self.form_layout.addWidget(QLabel("Nom d'utilisateur:"), 5, 0)
        self.form_layout.addWidget(self.username_input, 5, 1)

        self.password_input = self._create_input_field("Mot de passe", is_password=True)
        self.form_layout.addWidget(QLabel("Mot de passe:"), 6, 0)
        self.form_layout.addWidget(self.password_input, 6, 1)

        self.show_password_checkbox = QCheckBox("Afficher le mot de passe")
        self.show_password_checkbox.stateChanged.connect(self._toggle_password_visibility)
        self.form_layout.addWidget(self.show_password_checkbox, 7, 0, 1, 2)

        self.role_input = self._create_input_field("Rôle")
        self.form_layout.addWidget(QLabel("Rôle:"), 8, 0)
        self.form_layout.addWidget(self.role_input, 8, 1)

        self.is_active_checkbox = QCheckBox("Actif")
        self.form_layout.addWidget(self.is_active_checkbox, 9, 0)

        self.super_admin_checkbox = QCheckBox("Super Admin")
        self.form_layout.addWidget(self.super_admin_checkbox, 9, 1)

        self.form_group.setLayout(self.form_layout)
        self.main_layout.addWidget(self.form_group)

        # Buttons
        self.enregistrer_button = QPushButton("Enregistrer")
        self.enregistrer_button.clicked.connect(self._enregistrer_administrateur)
        self.modifier_button = QPushButton("Modifier")
        self.modifier_button.clicked.connect(self._modifier_administrateur)
        self.modifier_button.setVisible(False)

        self.button_layout.addWidget(self.enregistrer_button)
        self.button_layout.addWidget(self.modifier_button)
        self.main_layout.addLayout(self.button_layout)

        # Liste des administrateurs avec recherche et refresh
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un administrateur...")
        self.search_input.textChanged.connect(self._filter_administrateur)
        self.search_layout.addWidget(QLabel("Rechercher: "))
        self.search_layout.addWidget(self.search_input)

        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.clicked.connect(self._load_administrateurs)
        self.search_layout.addWidget(self.refresh_button)

        self.list_layout.addLayout(self.search_layout)
        self.list_layout.addWidget(self.list_view)
        self.list_view.selectionModel().selectionChanged.connect(
            self._on_item_selection_changed
        )
        self.list_group.setLayout(self.list_layout)
        self.main_layout.addWidget(self.list_group)

        self.setLayout(self.main_layout)

    def _toggle_password_visibility(self, state):
        """Affiche ou masque le mot de passe en fonction de l'état de la case à cocher."""
        if self.password_input:
            if state == Qt.Checked:
                self.password_input.setEchoMode(QLineEdit.Normal)
            else:
                self.password_input.setEchoMode(QLineEdit.Password)
        else:
            print("Erreur: self.password_input n'est pas défini dans _toggle_password_visibility")

    def _create_input_field(self, label_text, is_password=False):
        """Crée un widget QLineEdit."""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(label_text)
        if is_password:
            line_edit.setEchoMode(QLineEdit.Password)
        return line_edit

    def _create_label(self, text, object_name=None):
        """Crée un QLabel avec des propriétés communes."""
        label = QLabel(text)
        if object_name:
            label.setObjectName(object_name)
        return label

    def _show_message(self, title, message):
        """Affiche une boîte de message."""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(
            QMessageBox.Information if title == "Succès" else QMessageBox.Critical
        )
        msg_box.exec()

    def _get_field_value(self, widget):
        """Récupère le texte d'un QLineEdit."""
        return widget.text().strip() if widget else ""

    def _clear_fields(self):
        """Efface le contenu des champs de saisie."""
        self.nom_input.clear()
        self.postnom_input.clear()
        self.prenom_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.username_input.clear()
        if self.password_input:
            self.password_input.clear()
        self.role_input.clear()
        self.is_active_checkbox.setChecked(False)
        self.super_admin_checkbox.setChecked(False)
        self.selected_admin_id = None
        self.enregistrer_button.setVisible(True)
        self.modifier_button.setVisible(False)
        if self.show_password_checkbox:
            self.show_password_checkbox.setChecked(False)

    def _load_administrateurs(self):
        """Charge la liste des administrateurs depuis le contrôleur."""
        try:
            administrateurs = self.admin_controller.get_all_administrateurs()
            self._populate_list(administrateurs)
        except Exception as e:
            self._show_message(
                "Erreur", f"Erreur lors du chargement des administrateurs : {str(e)}"
            )

    def _populate_list(self, liste_administrateurs):
        """Peuple la QListView avec la liste des administrateurs."""
        self.list_model.clear()
        for admin in liste_administrateurs:
            item_text = (
                f"{admin.nom} {admin.postnom}, {admin.prenom} ({admin.username})"
            )
            item = QStandardItem(item_text)
            item.setData(admin.id, Qt.UserRole)  # Stocker l'ID pour une récupération facile
            self.list_model.appendRow(item)

    def _on_item_selection_changed(self, selected, deselected):
        """Gère le changement de sélection dans la liste."""
        if selected.indexes():
            self.selected_admin_id = selected.indexes()[0].data(Qt.UserRole)
            self._load_admin_for_modification(self.selected_admin_id)
        else:
            self.selected_admin_id = None
            self._clear_fields()
            self.enregistrer_button.setVisible(True)
            self.modifier_button.setVisible(False)
            if self.show_password_checkbox:
                self.show_password_checkbox.setChecked(False)

    def _load_admin_for_modification(self, admin_id):
        """Charge les informations d'un administrateur dans le formulaire de modification."""
        try:
            admin = self.admin_controller.get_administrateur_by_id(admin_id)
            if admin:
                self.nom_input.setText(admin.nom)
                self.postnom_input.setText(admin.postnom)
                self.prenom_input.setText(admin.prenom)
                self.phone_input.setText(str(admin.telephone))
                self.email_input.setText(admin.email if admin.email else "")
                self.username_input.setText(admin.username)
                self.role_input.setText(admin.role)
                self.is_active_checkbox.setChecked(admin.is_active)
                self.super_admin_checkbox.setChecked(admin.super_admin)

                # Désactiver la case à cocher d'affichage du mot de passe lors de la modification
                if self.show_password_checkbox:
                    self.show_password_checkbox.setEnabled(False)
                    self.show_password_checkbox.setChecked(False)
                    self.password_input.setEchoMode(QLineEdit.Password)

                self.enregistrer_button.setVisible(False)
                self.modifier_button.setVisible(True)
            else:
                self._show_message(
                    "Erreur", "Administrateur non trouvé pour la modification."
                )
        except Exception as e:
            self._show_message(
                "Erreur", f"Erreur lors du chargement de l'administrateur : {str(e)}"
            )

    def _delete_administrateur_confirmation(self, admin_id):
        """Affiche une boîte de confirmation avant de supprimer un administrateur."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cet administrateur ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._delete_administrateur(admin_id)

    def _delete_administrateur(self, admin_id):
        """Supprime un administrateur de la base de données."""
        try:
            if self.admin_controller.delete_administrateur(admin_id):
                self._show_message("Succès", "Administrateur supprimé avec succès.")
                self._load_administrateurs()
                self._clear_fields()
            else:
                self._show_message(
                    "Erreur", "Erreur lors de la suppression de l'administrateur."
                )
        except Exception as e:
            self._show_message("Erreur", f"Erreur lors de la suppression : {str(e)}")

    def _filter_administrateur(self, search_text):
        """Filtre la liste des administrateurs en fonction du texte de recherche."""
        try:
            administrateurs = self.admin_controller.get_all_administrateurs()
            filtered_administrateurs = [
                admin
                for admin in administrateurs
                if search_text.lower() in f"{admin.nom} {admin.postnom} {admin.prenom} {admin.username} {admin.role}".lower()
            ]
            self._populate_list(filtered_administrateurs)
        except Exception as e:
            self._show_message("Erreur", f"Erreur lors du filtrage : {str(e)}")

    def _load_initial_data(self):
        """Charge les données initiales au démarrage de la vue."""
        self._load_administrateurs()

    def _enregistrer_administrateur(self):
        """Enregistre un nouvel administrateur."""
        try:
            nom = self._get_field_value(self.nom_input)
            postnom = self._get_field_value(self.postnom_input)
            prenom = self._get_field_value(self.prenom_input)
            telephone = self._get_field_value(self.phone_input)
            email = self._get_field_value(self.email_input)
            username = self._get_field_value(self.username_input)
            password = self._get_field_value(self.password_input)
            role = self._get_field_value(self.role_input)
            is_active = self.is_active_checkbox.isChecked()
            super_admin = self.super_admin_checkbox.isChecked()

            if not all([nom, postnom, prenom, telephone, username, password, role]):
                self._show_message(
                    "Erreur", "Veuillez compléter tous les champs obligatoires (y compris le mot de passe)."
                )
                return

            if not telephone.isdigit():
                self._show_message(
                    "Erreur", "Le numéro de téléphone doit contenir uniquement des chiffres."
                )
                return

            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if email and not re.match(email_pattern, email):
                self._show_message("Erreur", "L'adresse email n'est pas valide.")
                return

            now = datetime.now()

            nouvel_admin = self.admin_controller.new_administrateur(
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                telephone=int(telephone),
                email=email,
                username=username,
                password=password,
                role=role,
                created_at=now.isoformat(),
                last_login=now.isoformat(),
                is_active=is_active,
                super_admin=super_admin,
            )

            if nouvel_admin:
                self._show_message(
                    "Succès", "Nouvel administrateur enregistré avec succès."
                )
                self._clear_fields()
                self._load_administrateurs()
            else:
                self._show_message(
                    "Erreur", "Erreur lors de l'enregistrement de l'administrateur."
                )

        except Exception as e:
            print("Erreur lors de l'enregistrement de l'administrateur:", str(e))
            self._show_message("Erreur", f"Une erreur s'est produite : {str(e)}")

    def _modifier_administrateur(self):
        """Modifie un administrateur existant."""
        if self.selected_admin_id is None:
            self._show_message(
                "Erreur",
                "Veuillez sélectionner un administrateur à modifier dans la liste.",
            )
            return
        try:
            nom = self._get_field_value(self.nom_input)
            postnom = self._get_field_value(self.postnom_input)
            prenom = self._get_field_value(self.prenom_input)
            telephone = self._get_field_value(self.phone_input)
            email = self._get_field_value(self.email_input)
            username = self._get_field_value(self.username_input)
            role = self._get_field_value(self.role_input)
            is_active = self.is_active_checkbox.isChecked()
            super_admin = self.super_admin_checkbox.isChecked()

            if not all([nom, postnom, prenom, telephone, username, role]):
                self._show_message(
                    "Erreur", "Veuillez compléter tous les champs obligatoires."
                )
                return

            if not telephone.isdigit():
                self._show_message(
                    "Erreur", "Le numéro de téléphone doit contenir uniquement des chiffres."
                )
                return

            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if email and not re.match(email_pattern, email):
                self._show_message("Erreur", "L'adresse email n'est pas valide.")
                return

            updated_admin = self.admin_controller.update_administrateur(
                self.selected_admin_id,
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                telephone=int(telephone),
                email=email,
                username=username,
                role=role,
                is_active=is_active,
                super_admin=super_admin,
            )

            if updated_admin:
                self._show_message("Succès", "Administrateur mis à jour avec succès.")
                self._clear_fields()
                self._load_administrateurs()
                self.enregistrer_button.setVisible(True)
                self.modifier_button.setVisible(False)
                self.selected_admin_id = None
                # Réactiver la case à cocher d'affichage du mot de passe pour les futurs enregistrements
                if self.show_password_checkbox:
                    self.show_password_checkbox.setEnabled(True)
            else:
                self._show_message(
                    "Erreur", "Erreur lors de la mise à jour de l'administrateur."
                )

        except Exception as e:
            print("Erreur lors de la modification de l'administrateur:", str(e))
            self._show_message("Erreur", f"Une erreur s'est produite : {str(e)}")


