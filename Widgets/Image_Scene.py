import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor

class ImageScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        center = rect.center()
        painter.setPen(QPen(QColor(0, 0, 255, 128), 1, Qt.DashLine))

        painter.drawLine(int(rect.left()), int(center.y()), int(rect.right()), int(center.y()))
        painter.drawLine(int(center.x()), int(rect.top()), int(center.x()), int(rect.bottom()))


class MainWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = ImageScene()
        self.setScene(self.scene)
        self.setFixedSize(800, 600)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
