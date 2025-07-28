from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from Controllers.alcool_test_controller import AlcoolTestController

class AlcoolDataManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Tests Alcool - Derniers Résultats")
        self.setMinimumSize(700, 400)

        self.controller = AlcoolTestController()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Date", "Taux (%)", "Action"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.verticalHeader().setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        records = self.controller.get_all_values()

        for row, record in enumerate(records):
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(record.datte)))

            try:
                valeur_float = float(record.valeur)
                valeur_str = f"{valeur_float:.2f} %"
            except ValueError:
                valeur_str = "Valeur invalide"

            self.table.setItem(row, 1, QTableWidgetItem(valeur_str))

            delete_btn = QPushButton("🗑️ Supprimer")
            delete_btn.clicked.connect(lambda _, rid=record.id: self.confirm_delete(rid))
            self.table.setCellWidget(row, 2, delete_btn)

    def confirm_delete(self, record_id):
        confirm = QMessageBox.question(
            self, "Confirmer",
            f"🗑️ Supprimer le test alcool (ID {record_id}) ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                self.controller.delete_value(record_id)
                QMessageBox.information(self, "Supprimé", "Enregistrement supprimé avec succès.")
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Suppression échouée : {e}")
