import sys

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFileSystemModel, QTreeView, QApplication
from PySide2.QtCore import QDir

class FileWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(250)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 创建一个文件系统模型
        self.model = QFileSystemModel(self)
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)  # 显示文件夹和文件的名称和类型，排除特殊条目
        self.tree_view = QTreeView(self)
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