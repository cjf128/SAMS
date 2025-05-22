import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class CustomSlider(QWidget):
    def __init__(self, minimum, maximum, type):
        super().__init__()
        self.setMinimumWidth(250)
        self.minimum = minimum
        self.maximum = maximum
        self.type = type

        self.initUI()

    def initUI(self):
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self.minimum)
        self.slider.setMaximum(self.maximum)

        if self.type == 0:
            self.spin_box = QSpinBox()
            self.slider.valueChanged.connect(self.spin_box.setValue)
            self.spin_box.valueChanged.connect(self.slider.setValue)

        elif self.type == 1:
            self.spin_box = QDoubleSpinBox()
            self.spin_box.setSingleStep(0.01)
            self.spin_box.setDecimals(2)
            self.slider.valueChanged.connect(self.updateSpinBoxValue)
            self.spin_box.valueChanged.connect(self.updateSliderValue)

        self.spin_box.setFixedWidth(70)
        self.spin_box.setMinimum(self.minimum)
        self.spin_box.setMaximum(self.maximum)

        layout = QHBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.spin_box)

        self.setLayout(layout)

    def updateSpinBoxValue(self, value):
        self.spin_box.setValue(value / 100)

    def updateSliderValue(self, value):
        self.slider.setValue(int(value * 100))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomSlider(0, 1, 1)
    window.show()
    sys.exit(app.exec_())
