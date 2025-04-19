import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class FileWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(250)
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #2b2c2e;
        #         font-family: Arial;
        #         font-size: 20px;
        #     }
        #     QTreeView {
        #         border: 2px solid #eeeeee;
        #         border-radius: 10px;
        #         background-color: #2b2c2e;
        #         color: #dfe1e5;
        #     }
        #     QTreeView::item:selected {
        #         background-color: #4a4b4d;
        #     }
        # """)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 创建一个文件系统模型
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)  # 显示文件夹和文件的名称和类型，排除特殊条目
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)

        # 隐藏大小和修改日期列
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        # 默认显示C盘文件
        self.model.setRootPath('C:/')
        self.tree_view.setRootIndex(self.model.index('C:/'))

        layout.addWidget(self.tree_view)
        self.setLayout(layout)

    def updateFileList(self, path):
        self.model.setRootPath(path)
        self.tree_view.setRootIndex(self.model.index(path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileWidget()
    window.show()
    sys.exit(app.exec_())