import sys

from PyQt5.QtWidgets import *

from Widgets.Custom_Slider import CustomSlider
from Widgets.File_Widget import FileWidget


class Sidebar(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(280)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        self.setStyleSheet("""
                    QTabWidget::pane { 
                        border-top: 2px solid #C2C2C2;
                    }
                    QTabWidget::tab-bar {
                        left: 5px; 
                    }
                    QTabBar::tab {
                        background: #333; 
                        color: #dfe1e5; 
                        border: 1px solid #444; 
                        border-bottom-color: #444;  
                        border-top-left-radius: 4px;
                        border-top-right-radius: 4px;
                        min-width: 8ex;
                        padding: 8px;
                    }
                    QTabBar::tab:selected, QTabBar::tab:hover {
                        background: #555;
                    }
                    QTabBar::tab:selected {
                        border-color: #777;
                        border-bottom-color: #555;
                    }
                    QComboBox {
                        border: 1px solid #ffffff;
                        border-radius: 5px;
                        padding: 5px;
                        color: #dfe1e5;
                        font-size: 18px;
                    }
                    QComboBox QAbstractItemView {
                        border: 1px solid gray;
                        selection-background-color: #2e436e; 
                    }
                    """)

        # 创建一个文件控件
        self.file_widget = FileWidget()
        layout.addWidget(self.file_widget)

        # 创建信息栏
        self.adjust_layout = QVBoxLayout()
        self.choose_layout = QVBoxLayout()

        # 创建tab管理信息栏
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMinimumWidth(250)
        self.tab_widget.setStyleSheet("background-color: #2b2c2e;color: #dfe1e5")

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tab_widget.addTab(self.tab1, '调整')
        self.tab_widget.addTab(self.tab2, '选择')

        # 基础信息栏
        self.ct_layer = QLabel("CT层数：")
        self.ct_layer.setFixedHeight(18)
        self.ct_layer_slider = CustomSlider(0, 1, 0)
        self.adjust_layout.addWidget(self.ct_layer)
        self.adjust_layout.addWidget(self.ct_layer_slider)

        self.alpha_label = QLabel("透明度：")
        self.alpha_label.setFixedHeight(18)
        self.alpha_slider = CustomSlider(0, 100, 1)
        self.adjust_layout.addWidget(self.alpha_label)
        self.adjust_layout.addWidget(self.alpha_slider)

        self.win_width = QLabel("窗宽：")
        self.win_width.setFixedHeight(18)
        self.win_width_slider = CustomSlider(1, 2000, 0)
        self.adjust_layout.addWidget(self.win_width)
        self.adjust_layout.addWidget(self.win_width_slider)

        self.win_level = QLabel("窗位：")
        self.win_level.setFixedHeight(18)
        self.win_level_slider = CustomSlider(-1000, 1000, 0)
        self.adjust_layout.addWidget(self.win_level)
        self.adjust_layout.addWidget(self.win_level_slider)

        self.spacer = QSpacerItem(20, 71, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.adjust_layout.addItem(self.spacer)

        self.image_label = QLabel("图像选择：")
        self.image_combox = QComboBox()
        self.image_combox.addItem("病人原图+分割图像")
        self.image_combox.addItem("病人原图")
        self.image_combox.addItem("分割图像")
        self.image_layout = QVBoxLayout()
        self.image_layout.addWidget(self.image_label)
        self.image_layout.addWidget(self.image_combox)
        self.choose_layout.addLayout(self.image_layout)

        self.type_label = QLabel("类型选择：")
        self.type_combox = QComboBox()
        self.type_combox.addItem("单层分割")
        self.type_combox.addItem("三层插值分割")
        self.type_layout = QVBoxLayout()
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_combox)
        self.choose_layout.addLayout(self.type_layout)

        self.accuracy_label = QLabel("模型选择：")
        self.accuracy_combox = QComboBox()
        self.accuracy_combox.addItem("SAM1.0（vit_b）")
        self.accuracy_combox.addItem("MobileSAM（vit_t）")
        self.accuracy_layout = QVBoxLayout()
        self.accuracy_layout.addWidget(self.accuracy_label)
        self.accuracy_layout.addWidget(self.accuracy_combox)
        self.choose_layout.addLayout(self.accuracy_layout)

        self.spacer_2 = QSpacerItem(20, 71, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.choose_layout.addItem(self.spacer_2)

        self.tab1.setLayout(self.adjust_layout)
        self.tab2.setLayout(self.choose_layout)

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def stop_work(self):
        self.setDisabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Sidebar()
    window.show()
    sys.exit(app.exec_())