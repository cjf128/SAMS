import sys

import numpy as np
from PyQt5.QtCore import QPointF, Qt, QEvent, QRectF
from PyQt5.QtGui import QColor, QTransform, QPen, QMouseEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsPixmapItem, QGraphicsPathItem, QGraphicsRectItem, QGraphicsScene, \
    QApplication


class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.point_list = []
        self.input_box = []
        self.parent = parent

        self.wheel = True
        self.press = False
        self.move_state = False
        self.frame = False
        self.line = False
        self.dragging = False
        self.drawing = False

        self.switch = 0
        self.segment_state = 0
        self.draw_state = 0
        self.index = 0
        self.n_layer = 0
        self.o_layer = -1
        self.spacing = (1, 1, 1)

        self.pixmap_item = QGraphicsPixmapItem()
        self.path_item = QGraphicsPathItem()
        self.rect_item = QGraphicsRectItem()

        self.start_point = QPointF()
        self.end_point = QPointF()
        self.last_mouse_position = QPointF()

        self.segment_start = []
        self.segment_end = []
        self.line_list = []
        self.eraser_list = []

        self.config()

    def config(self):
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor(0, 0, 0))
        self.setScene(self.scene)

        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def load_image(self, pixmap, angle):
        global scale_x, scale_y
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)

        if self.switch == 0:
            scale_x = self.spacing[0]
            scale_y = self.spacing[1]
        elif self.switch == 1:
            scale_x = self.spacing[1]
            scale_y = self.spacing[2]
        elif self.switch == 2:
            scale_x = self.spacing[0]
            scale_y = self.spacing[2]

        transform = QTransform()
        transform.rotate(angle)
        transform.scale(scale_x, scale_y)
        self.pixmap_item.setTransform(transform)

        self.scene.addItem(self.pixmap_item)

        self.rect_item = None
        self.path_item = None

    def update_box(self):
        self.input_box = []
        self.segment_start = []
        self.segment_end = []

        self.o_layer = -1
        self.index = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.press = True
            self.last_mouse_position = event.pos()

            self.scene_pos = self.mapToScene(event.pos())
            self.point = self.pixmap_item.mapFromScene(self.scene_pos).toPoint()
            self.point_list = self.point.x(), self.point.y()

            if self.move_state:
                self.dragging = True

            if self.frame:
                self.setCursor(Qt.CrossCursor)
                self.start_point = self.pixmap_item.mapFromScene(self.scene_pos).toPoint()
                self.end_point = self.start_point
                if self.segment_state == 0:
                    if self.rect_item:
                        self.scene.removeItem(self.rect_item)
                    self.rect_item = QGraphicsRectItem(QRectF(self.start_point, self.end_point))
                    self.rect_item.setPen(QPen(QColor('red'), 1))
                    self.rect_item.setTransform(self.pixmap_item.transform())
                    self.scene.addItem(self.rect_item)
                    self.drawing = True

                elif self.segment_state == 1:
                    if self.n_layer != self.o_layer and self.index <= 2:
                        if self.rect_item:
                            self.scene.removeItem(self.rect_item)
                        self.rect_item = QGraphicsRectItem(QRectF(self.start_point, self.end_point))
                        self.rect_item.setPen(QPen(QColor("#00adb5"), 1))
                        point = (self.start_point.x(), self.start_point.y(), self.n_layer)
                        self.segment_start.append(point)
                        self.rect_item.setTransform(self.pixmap_item.transform())
                        self.scene.addItem(self.rect_item)

                    elif self.n_layer == self.o_layer and self.index <= 3:
                        self.segment_start.pop()
                        if self.rect_item:
                            self.scene.removeItem(self.rect_item)
                        self.rect_item = QGraphicsRectItem(QRectF(self.start_point, self.end_point))
                        self.rect_item.setPen(QPen(QColor("#00adb5"), 1))
                        point = (self.start_point.x(), self.start_point.y(), self.n_layer)
                        self.segment_start.append(point)
                        self.rect_item.setTransform(self.pixmap_item.transform())
                        self.scene.addItem(self.rect_item)

                    if self.n_layer != self.o_layer and self.index <= 3:
                        self.index += 1

                    self.drawing = True

            if self.line:
                if self.path_item:
                    self.scene.removeItem(self.path_item)
                self.path_item = QGraphicsPathItem()
                self.path_item.setPen(QPen(QColor('red'), 1))
                self.scene.addItem(self.path_item)
                self.start_point = self.pixmap_item.mapFromScene(self.scene_pos).toPoint()
                path = self.path_item.path()
                path.moveTo(self.start_point)
                self.path_item.setTransform(self.pixmap_item.transform())
                self.path_item.setPath(path)
                point = [self.start_point.x(), self.start_point.y()]
                self.line_list = [point]
                self.draw_state = 1
                self.drawing = True

        if event.button() == Qt.RightButton:
            if self.line:
                if self.path_item:
                    self.scene.removeItem(self.path_item)
                self.path_item = QGraphicsPathItem()
                self.path_item.setPen(QPen(QColor('blue'), 1))
                self.scene.addItem(self.path_item)
                self.start_point = self.pixmap_item.mapFromScene(self.scene_pos).toPoint()
                path = self.path_item.path()
                path.moveTo(self.start_point)
                self.path_item.setTransform(self.pixmap_item.transform())
                self.path_item.setPath(path)
                point = [self.start_point.x(), self.start_point.y()]
                self.eraser_list = [point]
                self.draw_state = 0
                self.drawing = True

        if self.parent:
            parent_event = QMouseEvent(
                self.press,
                QEvent.MouseButtonPress,
            )
            QApplication.sendEvent(self.parent, parent_event)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.setMouseTracking(True)
        self.delta = event.pos() - self.last_mouse_position
        self.last_mouse_position = event.pos()

        self.scene_pos = self.mapToScene(event.pos())
        self.point = self.pixmap_item.mapFromScene(self.scene_pos).toPoint()
        self.point_list = self.point.x(), self.point.y()

        if self.dragging:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - self.delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - self.delta.y())

        if self.drawing and self.frame:
            self.end_point = self.pixmap_item.mapFromScene(self.scene_pos).toPoint()
            if self.rect_item:
                self.rect_item.setRect(QRectF(self.start_point, self.end_point).normalized())
                self.input_box = np.array([self.start_point.x(), self.start_point.y(),
                                           self.end_point.x(), self.end_point.y()])

        if self.drawing and self.line:
            if self.path_item:
                path = self.path_item.path()
                path.lineTo(self.point)
                self.path_item.setPath(path)
                point = [self.point.x(), self.point.y()]
                if self.draw_state == 1:
                    self.line_list.append(point)
                elif self.draw_state == 0:
                    self.eraser_list.append(point)

        if self.parent:
            parent_event = QMouseEvent(
                self.press,
                QEvent.MouseButtonPress,
            )
            QApplication.sendEvent(self.parent, parent_event)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.press = False
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)

        if self.drawing:
            if self.frame and self.segment_state == 1:
                if self.index <= 3:
                    if self.n_layer != self.o_layer:
                        self.o_layer = self.n_layer
                        point = (self.end_point.x(), self.end_point.y(), self.n_layer)
                        self.segment_end.append(point)

                elif self.index < 3:
                    if self.o_layer == self.n_layer:
                        self.segment_end.pop()
                        point = (self.end_point.x(), self.end_point.y(), self.n_layer)
                        self.segment_end.append(point)

            self.drawing = False

        if self.parent:
            parent_event = QMouseEvent(
                self.press,
                QEvent.MouseButtonPress,
            )
            QApplication.sendEvent(self.parent, parent_event)

        super().mousePressEvent(event)

    def wheelEvent(self, event):
        factor = 1.15
        if event.modifiers() == Qt.ControlModifier and self.wheel:
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor

            self.scale(factor, factor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())
