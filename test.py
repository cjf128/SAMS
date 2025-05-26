import sys
import numpy as np
import nibabel as nib
from PySide2.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QSlider, QLabel, QMessageBox
)
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import Qt
from PySide2 import sip


class NiftiViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.img = None  # NIfTI图像对象
        self.data = None  # 三维数据数组
        self.orientation = None  # 方向编码元组（如('R', 'A', 'S')）
        self.current_axis = None  # 当前显示轴索引
        self.axis_map = {}  # 解剖平面与轴索引的映射
        self.initUI()

    def initUI(self):
        # ====================== 控制按钮 ======================
        self.btn_open = QPushButton("导入NIfTI文件")
        self.btn_open.clicked.connect(self.load_nifti)

        self.btn_sagittal = QPushButton("矢状面")
        self.btn_coronal = QPushButton("冠状面")
        self.btn_axial = QPushButton("横断面")
        self.btn_sagittal.clicked.connect(lambda: self.switch_axis('sagittal'))
        self.btn_coronal.clicked.connect(lambda: self.switch_axis('coronal'))
        self.btn_axial.clicked.connect(lambda: self.switch_axis('axial'))

        # ====================== 图像显示标签 ======================
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(600, 600)

        # ====================== 切片滑动条 ======================
        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setMinimum(0)
        self.slice_slider.setMaximum(0)
        self.slice_slider.valueChanged.connect(self.update_slice)

        # ====================== 布局设置 ======================
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_sagittal)
        btn_layout.addWidget(self.btn_coronal)
        btn_layout.addWidget(self.btn_axial)

        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.slice_slider)

        self.setLayout(main_layout)
        self.setWindowTitle('医学影像查看器')
        self.setGeometry(200, 200, 800, 800)

    def load_nifti(self):
        """加载NIfTI文件并解析方向信息"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择NIfTI文件", "",
            "NIfTI文件 (*.nii *.nii.gz)"
        )
        if not file_path:
            return

        try:
            # 读取图像但不转换方向，保持原始方向
            self.img = nib.load(file_path)
            self.orientation = nib.aff2axcodes(self.img.affine)

            # 映射解剖平面到轴索引
            self.axis_map = {
                'sagittal': self.orientation.index(('R', 'L')),
                'coronal': self.orientation.index(('A', 'P')),
                'axial': self.orientation.index(('S', 'I'))
            }

            # 提取数据并预处理
            self.data = np.ascontiguousarray(self.img.get_fdata(), dtype=np.float32)
            self.data = (self.data - np.min(self.data)) / (np.max(self.data) - np.min(self.data)) * 255
            self.data = self.data.astype(np.uint8)

            # 初始化默认视图（横断面）
            self.switch_axis('axial')

        except Exception as e:
            QMessageBox.critical(self, "错误", f"文件解析失败：{str(e)}")

    def switch_axis(self, view_type):
        """根据解剖平面类型切换显示轴"""
        axis = self.axis_map[view_type]
        self.current_axis = axis
        max_slice = self.data.shape[axis] - 1
        self.slice_slider.setMaximum(max_slice)
        self.slice_slider.setValue(max_slice // 2)

        # 更新按钮文本显示方向信息
        direction = self.get_axis_direction(axis)
        getattr(self, f'btn_{view_type}').setText(
            f"{view_type.capitalize()} ({direction})"
        )
        self.update_slice()

    def get_axis_direction(self, axis):
        """获取轴的解剖方向描述"""
        code = self.orientation[axis]
        direction_map = {
            'R': '右→左', 'L': '左→右',
            'A': '前→后', 'P': '后→前',
            'S': '上→下', 'I': '下→上'
        }
        return direction_map.get(code, code)

    def update_slice(self):
        """更新当前切片显示"""
        if self.data is None:
            return

        idx = self.slice_slider.value()
        slice_data = np.take(self.data, idx, axis=self.current_axis)

        # 处理图像方向
        if self.orientation[self.current_axis] in ['L', 'P', 'I']:
            slice_data = np.flip(slice_data, axis=1)  # 镜像翻转反向轴

        # 转换为QPixmap
        h, w = slice_data.shape
        ptr = sip.voidptr(slice_data.ctypes.data)
        q_img = QImage(ptr, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = NiftiViewer()
    viewer.show()
    sys.exit(app.exec_())