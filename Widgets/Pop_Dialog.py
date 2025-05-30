import sys

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QVBoxLayout, QProgressBar, QLabel, QSizePolicy, QMessageBox, QDialog

class pop_dialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pop_close = 0
        self.close_signal = False
        self.stop_signal = False

        self.setWindowIcon(QIcon("my_icon.ico"))
        self.intUI()

    def intUI(self):
        self.setWindowTitle("运算")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()

        self.label = QLabel("运算中，请稍等...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def closeEvent(self, event):
        if self.pop_close == 0:
            reply = QMessageBox.warning(self, "警告", "尚未完成运算，是否停止？", QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.stop_signal = True
                self.label.setText("正在停止...")
                event.ignore()

            elif reply == QMessageBox.No:
                event.ignore()

        elif self.pop_close == 1:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = pop_dialog()
    window.show()
    sys.exit(app.exec_())