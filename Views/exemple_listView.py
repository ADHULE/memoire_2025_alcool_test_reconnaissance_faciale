import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import*
from PySide6.QtCore import*

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemple QListView")
        self.resize(400, 300)

        self.list_view = QListView()
        
        # Modèle de données
        self.model = QStringListModel()
        self.model.setStringList(["Élément 1", "Élément 2", "Élément 3", "Élément 4"])

        self.list_view.setModel(self.model)

        layout = QVBoxLayout()
        layout.addWidget(self.list_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
