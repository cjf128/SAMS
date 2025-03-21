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
        # 设置样式
        self.setStyleSheet("""
                    QSpinBox, QDoubleSpinBox {
                        background-color: #2b2c2e;
                        color: #dfe1e5;
                        border: 1px solid #3a3b3d;
                        border-radius: 4px;
                        padding: 2px;
                    }

                    QSpinBox::up-button, QDoubleSpinBox::up-button {
                        width: 5px;
                        border-width: 1px;
                    }

                    QSpinBox::down-button, QDoubleSpinBox::down-button {
                        width: 5px;
                        border-width: 1px;
                    }
                """)

        self.initUI()

    def initUI(self):
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setStyleSheet("""
            QSlider::groove {
                height: 8px;
                margin: 2px;
                border-radius: 8px;
            }

            QSlider::handle {
                background: #dfe1e5;
                border: 1px solid #1e1f22;
                width: 18px;
                height: 18px;
                margin: -5px 0; 
                border-radius: 9px;
            }

            QSlider::sub-page {
                background: #2b2d30;
                border: 1px solid #999999;
                height: 8px;
                border-radius: 4px;
            }

            QSlider::add-page {
                background: #dfe1e5;
                border: 1px solid #999999;
                height: 8px;
                border-radius: 4px;
            }
        """)
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
