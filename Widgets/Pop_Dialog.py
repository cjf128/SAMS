import sys

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QProgressBar, QLabel, QSizePolicy, \
    QDesktopWidget, QMessageBox, QDialog


class pop_dialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pop_close = 0
        self.close_signal = False
        self.stop_signal = False

        self.setWindowIcon(QIcon("my_icon.ico"))
        self.setStyleSheet("background-color: #393e46; color: #eeeeee")
        self.intUI()

    def intUI(self):
        self.setWindowTitle("运算")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()

        self.label = QLabel("运算中，请稍等...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, 20)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)

        self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #bbb;
                        border-radius: 5px;
                        background: #f3f3f3;
                        height: 20px;
                        width: 250px;
                    }
                    QProgressBar::chunk {
                        background: #00adb5;
                        width: 20px;
                    }
                """)

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