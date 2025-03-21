import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication

from Widgets.SegmentApp import SegmentApp

if __name__ == "__main__":
    try:
        import pyi_splash
        import time

        for i in range(100):
            text = f"加载中……进度{i}%"

            pyi_splash.update_text(text)  # 更新显示的文本

        pyi_splash.close()  # 关闭闪屏

    except ImportError:
        pass

    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QGuiApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    window = SegmentApp()
    window.show()
    sys.exit(app.exec_())
