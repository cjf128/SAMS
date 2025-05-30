import sys
from PySide2.QtCore import Qt
from PySide2.QtGui import QGuiApplication
from PySide2.QtWidgets import QApplication

from MainApp import SegmentApp

if __name__ == "__main__":
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QGuiApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    window = SegmentApp()
    window.show()
    sys.exit(app.exec_())
