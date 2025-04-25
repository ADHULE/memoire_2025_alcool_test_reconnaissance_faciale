import sys
from PySide6.QtWidgets import*
from PySide6.QtGui import *
from PySide6.QtCore import *

import os

class InfoPage(QWidget):
    def __init__(self, parent=None):
        super(InfoPage, self).__init__(parent)
       
        self.main_window = parent

        # Layout principal
        main_layout = QVBoxLayout()
        
        # Zone de recherche
        self.search_label = QLabel("Recherche (Nom, Postnom, Prénom):")
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.search_persons)
        
        # Bouton pour afficher toutes les informations
        self.show_all_button = QPushButton("Afficher Toutes les Informations")
        self.show_all_button.clicked.connect(self.show_all_persons)
        
        # Ajouter les éléments de recherche dans un formulaire
        search_form = QFormLayout()
        search_form.addRow(self.search_label, self.search_edit)
        search_form.addWidget(self.show_all_button)

        # Liste pour afficher les résultats de la recherche
        self.results_list = QListView()
        self.model = QStandardItemModel()
        self.results_list.setModel(self.model)
        self.results_list.clicked.connect(self.display_person_info)

        # Section pour afficher les images et les boutons
        self.image_layout = QVBoxLayout()
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        image_widget = QWidget()
        image_widget.setLayout(self.image_layout)
        self.image_scroll.setWidget(image_widget)

        # Centraliser les éléments
        central_layout = QHBoxLayout()
        central_layout.addWidget(self.results_list)
        central_layout.addWidget(self.image_scroll)

        # Ajouter tous les éléments au layout principal
        main_layout.addLayout(search_form)
        main_layout.addLayout(central_layout)

        self.setLayout(main_layout)

    def search_persons(self):
        """Rechercher les personnes par nom, postnom ou prénom."""
        search_text = self.search_edit.text()
        persons = self.session.query(Personne).filter(
            Personne.nom.contains(search_text) |
            Personne.postnom.contains(search_text) |
            Personne.prenom.contains(search_text)
        ).all()
        
        self.model.clear()
        for person in persons:
            item = QStandardItem(f"{person.id}: {person.nom} {person.postnom} {person.prenom}")
            item.setData(person, Qt.UserRole)
            self.model.appendRow(item)

    def show_all_persons(self):
        """Afficher toutes les personnes sans filtre."""
        persons = self.session.query(Personne).all()
        
        self.model.clear()
        for person in persons:
            item = QStandardItem(f"{person.id}: {person.nom} {person.postnom} {person.prenom}")
            item.setData(person, Qt.UserRole)
            self.model.appendRow(item)

    def display_person_info(self, index):
        """Afficher les images de la personne sélectionnée et ajouter les boutons Modifier et Supprimer."""
        item = self.model.itemFromIndex(index)
        person = item.data(Qt.UserRole)
        if person:
            # Clear current images and buttons
            for i in reversed(range(self.image_layout.count())): 
                widget_to_remove = self.image_layout.itemAt(i).widget()
                self.image_layout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)

            # Display images
            for image in person.images:
                pixmap = QPixmap(image.nom)
                image_label = QLabel()
                image_label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio))
                self.image_layout.addWidget(image_label)

            # Ajouter les boutons de modification et de suppression uniquement après sélection
            modify_button = QPushButton("Modifier")
            modify_button.setStyleSheet("background:#198754; border: 1px solid white;")
            modify_button.clicked.connect(lambda _, p=person: self.open_modify_page(p))
            self.image_layout.addWidget(modify_button)

            delete_button = QPushButton("Supprimer")
            delete_button.setStyleSheet("background:red; border: 1px solid white;")
            delete_button.clicked.connect(lambda _, p=person: self.delete_person(p.id))
            self.image_layout.addWidget(delete_button)

    def delete_person(self, person_id):
        """Supprimer la personne sélectionnée."""
        person = self.session.query(Personne).filter(Personne.id == person_id).first()
        if person:
            self.session.delete(person)
            self.session.commit()
            QMessageBox.information(self, "Succès", "Personne supprimée avec succès")
            self.clear_fields()
            self.show_all_persons()  # Rafraîchir la liste après suppression
        else:
            QMessageBox.warning(self, "Erreur", "Personne non trouvée")

    def clear_fields(self):
        """Effacer les champs du formulaire."""
        for i in reversed(range(self.image_layout.count())):
            widget_to_remove = self.image_layout.itemAt(i).widget()
            self.image_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

    def open_modify_page(self, person):
        """Ouvrir la page de modification pour la personne sélectionnée."""
        self.main_window.stack.setCurrentWidget(self.main_window.modify_page)
        self.main_window.modify_page.load_person(person)
