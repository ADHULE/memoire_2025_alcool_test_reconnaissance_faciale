import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QToolButton, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Responsive Menu Example")
        self.resize(800, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        # self.load_stylesheet()
        for tab_name in ["Tab 1", "Tab 2", "Tab 3"]:
            tab = QWidget()
            layout = QVBoxLayout()
            label = QLabel(tab_name)
            layout.addWidget(label)
            tab.setLayout(layout)
            self.tab_widget.addTab(tab, tab_name)

        self.menu_button = QToolButton(self)
        self.menu_button.setIcon(QIcon.fromTheme("open-menu"))
        self.menu_button.setPopupMode(QToolButton.InstantPopup)
        self.menu_button.setMenu(QMenu(self.menu_button))

        for option in ["Option 1", "Option 2", "Option 3"]:
            self.menu_button.menu().addAction(option)

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.currentChanged.emit(0)

    def on_tab_changed(self, index):
        self.menu_button.setVisible(index == 2)

    def resizeEvent(self, event):
        is_narrow = event.size().width() < 600
        self.tab_widget.tabBar().setVisible(not is_narrow)
        self.menu_button.setVisible(is_narrow)
        super().resizeEvent(event)

    
    def load_stylesheet(self):
        with open("Styles/tabwidget_style.css", "r") as file:
            self.setStyleSheet(file.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
