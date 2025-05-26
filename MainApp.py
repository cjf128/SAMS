import os
import sys
import copy
import re
import threading

import SimpleITK as sitk
import cv2
import torch
import numpy as np
import vtk
from PySide2.QtCore import Signal, QPoint, Qt, QSize
from PySide2.QtGui import QIcon, QKeySequence, QGuiApplication, QPixmap
from PySide2.QtWidgets import QMainWindow, QToolBar, QAction, QHBoxLayout, QLabel, QVBoxLayout, QStackedWidget, \
    QToolButton, QSizePolicy, QSplitter, QWidget, QFileDialog, QMessageBox, QApplication
import segment_anything
from segment_anything import sam_model_registry as sam_model_registry_sam
import mobile_sam
from mobile_sam import sam_model_registry as sam_model_registry_mobile
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from Widgets.Image_View import ImageViewer
from Widgets.Pop_Dialog import pop_dialog
from Widgets.Side_Bar import Sidebar


class SegmentApp(QMainWindow):
    FINSH_CANCELLED = Signal()

    def __init__(self, parent=None):
        super(SegmentApp, self).__init__(parent)

        self.num = -1
        self.alpha = 0.3
        self.win_width = 300
        self.win_level = 50
        self.angle = 0

        self.image_state = 3
        self.number = 0
        self.switch = 0
        self.side_state = 1

        self.y_star = 0
        self.y_end = 0
        self.x_star = 0
        self.x_end = 0

        self.ct_all = []
        self.pre_all = []
        self.draw_list = []

        self.operating = False
        self.press = False
        self.exist = False
        self.load = False
        self.reload = False

        self._dragPosition = QPoint()
        self.filepath = ''

        self.sam_checkpoint = "./model/sam_vit_b_01ec64.pth"
        self.model_type = "vit_b"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"  # 设备类型

        # 加载模型并设置预测器
        sam = sam_model_registry_sam[self.model_type](checkpoint=self.sam_checkpoint)  # 加载模型
        sam.to(device=self.device)  # 将模型加载到指定设备
        self.SamPredictor = segment_anything.SamPredictor(sam)  # 设置 3D 模型预测器

        self.resize(1200, 900)
        self.setWindowTitle("MRI图像单器官半自动分割软件v3.0.0")
        self.setWindowIcon(QIcon("my_icon.ico"))

        self.config_tools()
        self.config_Layout()
        self.config_connectAction()

    def config_tools(self):
        """
        工具栏初始化
        """
        self.tool_bar = QToolBar(self)
        self.tool_bar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar)

        self.tool_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.tool_bar.setIconSize(QSize(28, 28))

        self.load_action = QAction(QIcon('./my_svg/folder-add-outline.svg'), '导入', self)
        self.load_action.setShortcut(QKeySequence('Ctrl+O'))
        self.tool_bar.addAction(self.load_action)

        self.save_action = QAction(QIcon('./my_svg/save-outline.svg'), "保存", self)
        self.save_action.setShortcut(QKeySequence('Ctrl+S'))
        self.tool_bar.addAction(self.save_action)

        self.side_action = QAction(QIcon('./my_svg/layout-outline.svg'), "侧栏", self)
        self.tool_bar.addAction(self.side_action)

        self.move_action = QAction(QIcon('./my_svg/plus-outline.svg'), "翻图", self)
        self.move_action.setCheckable(True)
        self.move_action.setChecked(True)
        self.move_action.setShortcut(QKeySequence('Ctrl+M'))
        self.tool_bar.addAction(self.move_action)

        self.win_action = QAction(QIcon("./my_svg/smiling-face-outline.svg"), "调窗", self)
        self.win_action.setCheckable(True)
        self.win_action.setShortcut(QKeySequence("Ctrl+T"))
        self.tool_bar.addAction(self.win_action)

        self.line_action = QAction(QIcon('./my_svg/radio-button-off-outline.svg'), '画笔', self)
        self.line_action.setCheckable(True)
        self.line_action.setShortcut(QKeySequence('Ctrl+W'))
        self.tool_bar.addAction(self.line_action)

        self.frame_action = QAction(QIcon('./my_svg/square-outline.svg'), 'SAM', self)
        self.frame_action.setCheckable(True)
        self.frame_action.setShortcut(QKeySequence('Ctrl+F'))
        self.tool_bar.addAction(self.frame_action)

        self.operation_action = QAction(QIcon('./my_svg/play-circle-outline.svg'), "运算", self)
        self.operation_action.setShortcut(QKeySequence('Ctrl+P'))
        self.tool_bar.addAction(self.operation_action)

        self.vtk_action = QAction(QIcon('./my_svg/layers-outline.svg'), "3D显示", self)
        self.vtk_action.setCheckable(True)
        self.tool_bar.addAction(self.vtk_action)

        self.switch_action = QAction(QIcon('./my_svg/copy-outline.svg'), '转换', self)
        self.switch_action.setShortcut(QKeySequence('Ctrl+G'))
        self.tool_bar.addAction(self.switch_action)

        self.reset_action = QAction(QIcon('./my_svg/refresh-outline.svg'), '复位', self)
        self.reset_action.setShortcut(QKeySequence('Ctrl+B'))
        self.tool_bar.addAction(self.reset_action)

        self.redo_action = QAction(QIcon('./my_svg/sync-outline.svg'), "重做", self)
        self.redo_action.setShortcut(QKeySequence('Ctrl+R'))
        self.tool_bar.addAction(self.redo_action)

    def config_Layout(self):
        """
        控件布局初始化
        """
        main_widget = QWidget(self)
        self.splitter_widget = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_widget)

        self.sidebar = Sidebar()
        self.sidebar.setMaximumWidth(600)
        self.sidebar.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.sidebar.win_width_slider.spin_box.setValue(self.win_width)
        self.sidebar.win_level_slider.spin_box.setValue(self.win_level)
        self.sidebar.alpha_slider.spin_box.setValue(self.alpha)

        self.image = ImageViewer(self)
        self.vtk_image = QVTKRenderWindowInteractor()

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self.image)
        self.stacked_widget.addWidget(self.vtk_image)
        self.stacked_widget.setCurrentWidget(self.image)

        self.up_left_text = QLabel()
        self.up_left_text.setFixedHeight(25)
        self.update_text()

        anti_rotate = QAction(QIcon('./my_svg/corner-up-left-outline.svg'), '逆时针旋转', self)  # 图标路径
        self.anti_rotate_button = QToolButton()
        self.anti_rotate_button.setDefaultAction(anti_rotate)
        self.anti_rotate_button.setToolButtonStyle(Qt.ToolButtonIconOnly)

        clock_rotate = QAction(QIcon('./my_svg/corner-up-right-outline.svg'), '顺时针旋转', self)  # 图标路径
        self.clock_rotate_button = QToolButton()
        self.clock_rotate_button.setDefaultAction(clock_rotate)
        self.clock_rotate_button.setToolButtonStyle(Qt.ToolButtonIconOnly)

        up_layout = QHBoxLayout()
        up_layout.addWidget(self.up_left_text)
        up_layout.addWidget(self.anti_rotate_button)
        up_layout.addWidget(self.clock_rotate_button)

        self.down_right_text = QLabel()
        self.down_right_text.setFixedHeight(18)
        self.down_right_text.setText("x:0; y:0")
        self.down_right_text.setAlignment(Qt.AlignRight)

        self.down_left_text = QLabel()
        self.down_left_text.setFixedHeight(18)
        self.down_left_text.setAlignment(Qt.AlignLeft)

        down_layout = QHBoxLayout()
        down_layout.addWidget(self.down_left_text)
        down_layout.addWidget(self.down_right_text)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(2)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addLayout(up_layout)
        right_layout.addWidget(self.stacked_widget)
        right_layout.addLayout(down_layout)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        self.splitter_widget.addWidget(self.sidebar)
        self.splitter_widget.addWidget(right_widget)
        self.splitter_widget.setSizes([300, 800])

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.splitter_widget)

        main_widget.setLayout(main_layout)

        self.statusbar = QMainWindow.statusBar(self)
        self.statusbar.showMessage("Ready")

    def config_connectAction(self):
        """
        初始化信号与槽连接
        """
        self.FINSH_CANCELLED.connect(self.finish_work)

        self.load_action.triggered.connect(self.load_slot)
        self.save_action.triggered.connect(self.save_slot)
        self.side_action.triggered.connect(self.side_slot)
        self.operation_action.triggered.connect(self.operation)
        self.redo_action.triggered.connect(self.redo_slot)
        self.switch_action.triggered.connect(self.switch_slot)
        self.reset_action.triggered.connect(self.reset_slot)
        self.vtk_action.triggered.connect(self.vtk_slot)

        self.frame_action.triggered.connect(self.frame_solt)
        self.line_action.triggered.connect(self.line_slot)
        self.move_action.triggered.connect(self.move_slot)
        self.win_action.triggered.connect(self.win_slot)

        self.sidebar.file_widget.tree_view.doubleClicked.connect(self.load_slot)

        self.sidebar.win_width_slider.spin_box.valueChanged.connect(self.change_win_width)
        self.sidebar.win_level_slider.spin_box.valueChanged.connect(self.change_win_level)
        self.sidebar.alpha_slider.spin_box.valueChanged.connect(self.change_alpha)
        self.sidebar.ct_layer_slider.spin_box.valueChanged.connect(self.change_ct_layer)

        self.sidebar.image_combox.currentIndexChanged.connect(self.onImageStateChange)
        self.sidebar.type_combox.currentIndexChanged.connect(self.onTypeStateChange)
        self.sidebar.accuracy_combox.currentIndexChanged.connect(self.onModelChange)

        self.anti_rotate_button.triggered.connect(self.anti_rotate)
        self.clock_rotate_button.triggered.connect(self.clock_rotate)

    def reset_slot(self):
        """
        复位处理
        """
        if self.exist:
            self.image.fitInView(self.image.pixmap_item, Qt.KeepAspectRatio)

            self.update_all()
            if self.vtk_action.isChecked():
                self.vtk_slot()

    def side_slot(self):
        """
        侧栏打开与隐藏
        """
        if self.sidebar.isHidden():
            self.sidebar.setVisible(True)
            self.splitter_widget.setSizes([300, 800])
        elif self.sidebar.isVisible():
            self.sidebar.setVisible(False)

    def switch_slot(self):
        """
        切换视图处理-参数改变，重新处理数据，更新图像
        """
        if self.exist and not self.vtk_action.isChecked():
            self.vtk_action.setChecked(False)
            self.vtk_hide()
            self.switch += 1
            self.MatrixToImage(self.file_path)
            self.reload = True
            self.update_image()

    def redo_slot(self):
        """
        重做-清空标注
        """
        if self.exist:
            self.pre_all = np.zeros_like(self.ct_all)
            self.draw_list = []
            self.image.update_box()
            self.update_image()
            if self.vtk_action.isChecked():
                self.vtk_slot()

    def anti_rotate(self):
        self.angle -= 90
        self.reload = True
        self.update_image()

    def clock_rotate(self):
        self.angle += 90
        self.reload = True
        self.update_image()

    # 打开文件
    def load_slot(self, index):
        """
        导入数据
        """
        file_path = ''
        if not index:
            # 打开文件对话框
            file_path, filetype = QFileDialog.getOpenFileName(self, 'Open file', '', "Text Files (*.nii.gz);")
        elif index:
            file_path = self.sidebar.file_widget.model.filePath(index)

        if file_path != '' and (file_path.endswith('.nii') or file_path.endswith('.nii.gz')):
            folder_path = os.path.dirname(file_path)
            self.sidebar.file_widget.updateFileList(folder_path)

            cn = re.compile(u"[\u4e00-\u9fa5]")  # 检查中文
            match = cn.search(file_path)
            if match:
                QMessageBox.warning(self, "警告", "文件路径中不能含有中文", QMessageBox.Ok)
            else:
                self.file_path = file_path
                self.statusbar.showMessage('已导入文件：' + self.file_path)
                self.exist = True
                self.load = True
                self.reload = True
                self.MatrixToImage(self.file_path)

                self.move_slot()
                self.vtk_action.setChecked(False)
                self.vtk_hide()
                self.sidebar.image_combox.setCurrentIndex(0)
                self.update_image()
                self.update_text()

    def MatrixToImage(self, filepath):
        """
        数据初始化
        """
        image = sitk.ReadImage(filepath)
        self.image.spacing = image.GetSpacing()
        data = sitk.GetArrayFromImage(image)
        trans = [[1, 2, 0], [0, 1, 2], [0, 2, 1]]
        correct = [[2, 1, 0], [2, 0, 1], [0, 2, 1]]
        self.index = self.switch % 3
        self.image.switch = self.index

        data = np.transpose(data, axes=trans[self.index])

        self.ct_all = copy.deepcopy(data)
        if self.load:
            self.pre_all = np.zeros_like(self.ct_all)
        else:
            self.pre_all = np.transpose(self.pre_all, axes=correct[self.index])

        self.setting()

    def setting(self):
        """
        导入数据后初始化层数
        """
        self.sidebar.ct_layer_slider.slider.setMaximum(self.ct_all.shape[2] - 1)
        self.sidebar.ct_layer_slider.spin_box.setMaximum(self.ct_all.shape[2] - 1)
        self.number = self.ct_all.shape[2] // 2
        self.image.n_layer = self.number
        self.sidebar.ct_layer_slider.spin_box.setValue(self.number)
        # 此时会更新图像，层数会改变，因此要将层数设置放前面

    def save_slot(self):
        """
        保存设置
        """
        if np.any(self.pre_all) and not self.operating:
            file_, ok = QFileDialog.getSaveFileName(self,
                                                    "文件保存",
                                                    self.filepath,
                                                    "NiFTI(*.nii.gz);;All Files (*)")


            if file_ != "":
                image = copy.deepcopy(self.pre_all)
                save = [[2, 0, 1], [0, 1, 2], [0, 2, 1]]
                image = np.transpose(image, axes=save[self.index])

                image = sitk.GetImageFromArray(image)
                self.statusBar().showMessage('已保存文件：' + file_)
                sitk.WriteImage(image, file_)
        else:
            QMessageBox.warning(self, "警告", "无可保存分割图像！", QMessageBox.Ok)

    def change_win_width(self, value):
        """
        调整窗宽
        """
        self.win_width = value

        if self.exist:
            self.update_image()

    def change_win_level(self, value):
        """
        调整窗位
        """
        self.win_level = value

        if self.exist:
            self.update_image()

    def change_alpha(self, value):
        """
        标注区域的透明度
        """
        self.alpha = value
        if self.exist:
            self.update_image()

    def change_ct_layer(self, value):
        """
        调整图像层数
        """
        self.number = value
        self.image.n_layer = self.number
        if self.exist:
            self.update_all()
            self.update_text()

    def onImageStateChange(self):
        """
        图像状态改变
        """
        if self.exist:
            selected_state = self.sidebar.image_combox.currentText()
            if selected_state == "病人原图":
                self.image_state = 2
            elif selected_state == "分割图像":
                self.image_state = 1
            elif selected_state == "病人原图+分割图像":
                self.image_state = 3

            self.update_image()
            self.update_text()
        else:
            return

    def onTypeStateChange(self):
        """
        分割类型状态改变
        """
        selected_state = self.sidebar.type_combox.currentText()
        if selected_state == "单层分割":
            self.image.segment_state = 0
            if self.image.rect_item:
                self.image.scene.removeItem(self.image.rect_item)
        elif selected_state == "三层插值分割":
            self.image.segment_state = 1
            if self.image.rect_item:
                self.image.scene.removeItem(self.image.rect_item)

    def onModelChange(self):
        """
        模型精度改变
        """
        selected_model = self.sidebar.accuracy_combox.currentText()
        if "vit_b" in selected_model:
            self.model_type = 'vit_b'
            self.sam_checkpoint = "model/sam_vit_b_01ec64.pth"

            sam = sam_model_registry_sam[self.model_type](checkpoint=self.sam_checkpoint)
            sam.to(device=self.device)
            self.SamPredictor = segment_anything.SamPredictor(sam)

        elif "vit_t" in selected_model:
            self.model_type = 'vit_t'
            self.sam_checkpoint = "model/mobile_sam.pt"

            sam = sam_model_registry_mobile[self.model_type](checkpoint=self.sam_checkpoint)
            sam.to(device=self.device)
            self.SamPredictor = mobile_sam.SamPredictor(sam)

    def frame_solt(self):
        """
        使用SAM画框-设置按键冲突，调整图像状态
        """
        if self.frame_action.isChecked():
            self.move_action.setChecked(False)
            self.line_action.setChecked(False)
            self.win_action.setChecked(False)
            self.image.update_box()

            if self.exist:
                self.image.move_state = False
                self.image.frame = True
                self.image.line = False

                self.update_all()

        if not self.frame_action.isChecked():
            self.move_action.setChecked(True)
            self.image.move_state = True
            if self.exist:
                self.image.frame = False
                self.update_all()

    def line_slot(self):
        """
        画笔工具-设置按键冲突，调整图像状态
        """
        if self.line_action.isChecked():
            self.move_action.setChecked(False)
            self.frame_action.setChecked(False)
            self.win_action.setChecked(False)
            self.image.update_box()

            if self.exist:
                self.image.move_state = False
                self.image.frame = False
                self.image.line = True

                self.update_all()

        if not self.line_action.isChecked():
            self.move_action.setChecked(True)
            self.image.move_state = True
            if self.exist:
                self.image.line = False
                self.update_all()

    def move_slot(self):
        """
        图像移动工具-设置按键冲突，调整图像状态
        """
        if self.move_action.isChecked():
            self.frame_action.setChecked(False)
            self.line_action.setChecked(False)
            self.win_action.setChecked(False)
            self.image.update_box()

            if self.exist:
                self.image.move_state = True
                self.image.line = False
                self.image.frame = False

                self.update_all()

        if not self.move_action.isChecked():
            if self.exist:
                self.image.move_state = False
                self.update_all()

    def win_slot(self):
        """
        调窗工具-设置按键冲突，调整图像状态
        """
        if self.win_action.isChecked():
            self.frame_action.setChecked(False)
            self.line_action.setChecked(False)
            self.move_action.setChecked(False)
            self.image.update_box()

            if self.exist:
                self.image.move_state = False
                self.image.line = False
                self.image.frame = False
                self.update_all()

        if not self.win_action.isChecked():
            self.move_action.setChecked(True)
            self.image.move_state = True
            if self.exist:
                self.update_all()

    def vtk_slot(self):
        """
        3D显示
        """
        if self.vtk_action.isChecked():
            self.frame_action.setCheckable(False)
            self.line_action.setCheckable(False)
            self.move_action.setCheckable(False)
            self.win_action.setCheckable(False)

            if self.exist:
                self.image.move_state = False
                self.image.line = False
                self.image.frame = False
                self.update_all()

            self.sidebar.setDisabled(True)
            self.image.wheel = False

            if self.exist:
                image_array = copy.deepcopy(self.pre_all)
                save = [[2, 0, 1], [0, 1, 2], [0, 2, 1]]
                image_array = np.transpose(image_array, axes=save[self.index])
                image_array = np.flip(image_array, axis=(0, 1))

                # 创建 VTK 渲染器和窗口
                self.renderer = vtk.vtkRenderer()
                self.render_window = self.vtk_image.GetRenderWindow()
                self.render_window.AddRenderer(self.renderer)
                self.iren = self.render_window.GetInteractor()

                # 设置交互器样式
                style = vtk.vtkInteractorStyleTrackballCamera()
                self.iren.SetInteractorStyle(style)

                # 将 Numpy 数组转换为 VTK 图像数据
                data_importer = vtk.vtkImageImport()
                data_string = image_array.tobytes()
                data_importer.CopyImportVoidPointer(data_string, len(data_string))
                data_importer.SetDataScalarTypeToUnsignedShort()
                data_importer.SetNumberOfScalarComponents(1)
                data_importer.SetDataExtent(0, image_array.shape[2] - 1, 0, image_array.shape[1] - 1, 0,
                                            image_array.shape[0] - 1)
                data_importer.SetWholeExtent(0, image_array.shape[2] - 1, 0, image_array.shape[1] - 1, 0,
                                             image_array.shape[0] - 1)

                # 设置体积渲染的属性
                volume_mapper = vtk.vtkSmartVolumeMapper()
                volume_mapper.SetInputConnection(data_importer.GetOutputPort())

                volume_property = vtk.vtkVolumeProperty()
                volume_property.ShadeOn()
                volume_property.SetInterpolationTypeToLinear()

                # 设置颜色传递函数
                color_func = vtk.vtkColorTransferFunction()
                color_func.AddRGBPoint(0, 0.0, 0.0, 0.0)  # 未标注部分为黑色
                color_func.AddRGBPoint(1, 1.0, 0.0, 0.0)  # 标注部分为红色
                volume_property.SetColor(color_func)

                # 设置不透明度传递函数
                opacity_func = vtk.vtkPiecewiseFunction()
                opacity_func.AddPoint(0, 0.00)  # 未标注部分完全透明
                opacity_func.AddPoint(1, 1.00)  # 标注部分完全不透明
                volume_property.SetScalarOpacity(opacity_func)

                # 创建体积并设置其属性
                volume = vtk.vtkVolume()
                volume.SetMapper(volume_mapper)
                volume.SetProperty(volume_property)

                # 将体积添加到渲染器
                self.renderer.AddVolume(volume)
                self.renderer.SetBackground(0, 0, 0)  # 设置背景颜色为白色

                # 创建 XYZ 轴显示
                axes = vtk.vtkAxesActor()

                # 设置坐标轴的长度，使其从中心点发散
                axes.SetTotalLength(200, 200, 200)

                # 添加坐标轴到渲染器
                self.renderer.AddActor(axes)

                # 自动调整视角以适应整个图像
                self.renderer.ResetCamera()

                # 开始 VTK 交互
                self.iren.Initialize()
                self.iren.Start()

                self.stacked_widget.setCurrentWidget(self.vtk_image)

            else:
                QMessageBox.warning(self, '警告', '请先导入图像!', QMessageBox.Ok)
                self.vtk_action.setChecked(False)

        elif not self.vtk_action.isChecked():
            self.vtk_hide()
            self.move_action.setChecked(True)
            self.image.move_state = True

    def vtk_hide(self):
        self.frame_action.setCheckable(True)
        self.line_action.setCheckable(True)
        self.move_action.setCheckable(True)
        self.win_action.setCheckable(True)

        self.sidebar.setDisabled(False)
        self.image.wheel = True

        self.stacked_widget.setCurrentWidget(self.image)

    def update_all(self):
        """
        更新-以防按键冲突后仍有残留项
        """
        self.image.line_list = []
        self.image.eraser_list = []
        self.image.input_box = []
        self.draw_list = []
        self.update_image()

    def update_text(self):
        """
        上信息栏更新信息
        """
        ct_text = self.sidebar.ct_layer_slider.spin_box.value()
        image_text = self.sidebar.image_combox.currentText()

        self.up_left_text.setText(" CT层数：" + str(ct_text) + " | " + image_text)

    def operation(self):
        if np.any(self.image.input_box):
            self.pop_widget = pop_dialog()
            self.pop_widget.show()
            self.setDisabled(True)
            operation_thread = threading.Thread(target=self.calculation)
            operation_thread.daemon = True
            operation_thread.start()

    def finish_work(self):
        if self.image.segment_state == 1:
            self.image.index = 0
            self.image.segment_start = []
            self.image.segment_end = []
        self.pop_widget.pop_close = 1
        self.pop_widget.close()
        self.setDisabled(False)
        self.update_all()

    def normalize(self, slice):
        window_upper = self.win_level + self.win_width / 2
        window_lower = self.win_level - self.win_width / 2
        slice = np.clip(slice, window_lower, window_upper)
        slice = (slice - window_lower) / self.win_width * 255
        slice = slice.astype(np.uint8)
        return slice

    def calculation(self):
        """
        SAM运算
        """
        if self.image.segment_state == 0:
            current_slice = self.ct_all[:, :, self.number]
            current_slice = self.normalize(current_slice)
            current_slice = np.stack([current_slice] * 3, axis=-1)

            input_box = self.image.input_box
            if input_box[0] > input_box[2]:
                temp = input_box[0]
                input_box[0] = input_box[2]
                input_box[2] = temp
            if input_box[1] > input_box[3]:
                temp = input_box[1]
                input_box[1] = input_box[3]
                input_box[3] = temp

            if not self.number == self.num:
                self.SamPredictor.set_image(current_slice)
            masks, _, _ = self.SamPredictor.predict(box=input_box, multimask_output=False)
            masks = masks[0, :, :].astype(np.uint8)

            self.num = self.number
            self.pre_all[:, :, self.number] += masks
            self.FINSH_CANCELLED.emit()

        elif self.image.segment_state == 1:
            def find_xy_for_z(p1, p2, z_values):
                # 解构点P1和P2的坐标
                x1, y1, z1 = p1
                x2, y2, z2 = p2

                # 计算方向向量
                dx = x2 - x1
                dy = y2 - y1
                dz = z2 - z1

                # 存储结果的列表
                results = []

                # 对每个z值计算对应的x和y
                for z in z_values:
                    if dz == 0:
                        print("直线与z轴平行，无法计算对应的x和y")
                        return
                    t = (z - z1) / dz
                    x = x1 + t * dx
                    y = y1 + t * dy
                    results.append([x, y, z])

                return results

            if self.image.index == 3:
                box = []
                epoch = 0

                start_1 = min(self.image.segment_start[0][2], self.image.segment_start[1][2])
                start_2 = min(self.image.segment_start[1][2], self.image.segment_start[2][2])

                end_1 = max(self.image.segment_start[0][2], self.image.segment_start[1][2])
                end_2 = max(self.image.segment_start[1][2], self.image.segment_start[2][2])

                z_values_1 = list(range(start_1, end_1 + 1))
                z_values_2 = list(range(start_2, end_2 + 1))
                z_values = sorted(list(set(z_values_1 + z_values_2)))

                result_1 = find_xy_for_z(self.image.segment_start[0], self.image.segment_start[1], z_values_1)
                result_2 = find_xy_for_z(self.image.segment_start[1], self.image.segment_start[2], z_values_2)
                result_3 = find_xy_for_z(self.image.segment_end[0], self.image.segment_end[1], z_values_1)
                result_4 = find_xy_for_z(self.image.segment_end[1], self.image.segment_end[2], z_values_2)

                result_1 = sorted(result_1, key=lambda x: x[-1])
                result_2 = sorted(result_2, key=lambda x: x[-1])
                result_3 = sorted(result_3, key=lambda x: x[-1])
                result_4 = sorted(result_4, key=lambda x: x[-1])

                if result_1[0][2] > result_2[0][2]:
                    for j in range(len(z_values_2)):
                        x2, y2, z2 = result_2[j]
                        x4, y4, z4 = result_4[j]

                        rect_2 = [int(x2), int(y2), int(x4), int(y4)]
                        box.append(rect_2)

                    for i in range(len(z_values_1)):
                        x1, y1, z1 = result_1[i]
                        x3, y3, z3 = result_3[i]

                        rect_1 = [int(x1), int(y1), int(x3), int(y3)]
                        box.append(rect_1)

                elif result_1[0][2] < result_2[0][2]:
                    for i in range(len(z_values_1)):
                        x1, y1, z1 = result_1[i]
                        x3, y3, z3 = result_3[i]

                        rect_1 = [int(x1), int(y1), int(x3), int(y3)]
                        box.append(rect_1)

                    for j in range(len(z_values_2)):
                        x2, y2, z2 = result_2[j]
                        x4, y4, z4 = result_4[j]

                        rect_2 = [int(x2), int(y2), int(x4), int(y4)]
                        box.append(rect_2)

                # 去掉重复元素的同时保留顺序
                seen = set()
                unique_box = []
                for sublist in box:
                    t = tuple(sublist)
                    if t not in seen:
                        seen.add(t)
                        unique_box.append(sublist)

                box = np.array(unique_box)

                for index in z_values:
                    if self.pop_widget.stop_signal:
                        break

                    current_slice = self.ct_all[:, :, index]
                    current_slice = self.normalize(current_slice)

                    current_slice = np.stack([current_slice] * 3, axis=-1)

                    input_box = box[epoch]
                    epoch += 1

                    # 使用模型进行预测
                    self.SamPredictor.set_image(current_slice)
                    masks, _, _ = self.SamPredictor.predict(box=input_box, multimask_output=False)
                    masks = masks[0, :, :].astype(np.uint8)
                    self.pre_all[:, :, index] += masks

            self.FINSH_CANCELLED.emit()

    def update_image(self):
        """
        图像更新
        """
        img = self.prepare_image()
        self.image.load_image(img, self.angle)

        if self.reload:
            self.image.scene.setSceneRect(self.image.scene.itemsBoundingRect())
            if self.load:
                self.image.fitInView(self.image.pixmap_item, Qt.KeepAspectRatio)
                self.load = False
            self.reload = False

    def closeEvent(self, event):
        """
        重写关闭事件
        """
        reply = QMessageBox.question(self, '退出提示',
                                     "确定退出?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        """
        鼠标按下事件重写，用于拖拽和绘图
        """
        super().mousePressEvent(event)
        self.image.n_layer = self.number
        if event.button() == Qt.LeftButton and not self.image.press:
            self.press = True
            self._dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

        if self.image.press:
            self.down_right_text.setText(f"x:{self.image.point_list[0]}; y:{self.image.point_list[1]}")
            if self.image.segment_state == 1 and self.frame_action.isChecked():
                if self.image.index == 1:
                    self.down_left_text.setText("正在画起始框")
                if self.image.index == 2:
                    self.down_left_text.setText("正在画最大特征框")
                if self.image.index == 3:
                    self.down_left_text.setText("正在画终止框")

    def mouseMoveEvent(self, event):
        """
        鼠标移动重写，用于移动和绘图
        """
        super().mouseMoveEvent(event)
        self.setMouseTracking(True)

        if self.exist:
            if self.win_action.isChecked() and self.image.press:
                delta = self.image.delta

                self.win_width = np.clip(self.win_width, 0, 2000)
                self.win_level = np.clip(self.win_level, -1000, 1000)

                self.win_width += int(delta.x())
                self.win_level += int(delta.y())
                self.sidebar.win_width_slider.spin_box.setValue(self.win_width)
                self.sidebar.win_level_slider.spin_box.setValue(self.win_level)

            if self.image.press:
                self.down_right_text.setText(f"x:{self.image.point_list[0]}; y:{self.image.point_list[1]}")
                event.accept()

        if self.press and not self.image.press:
            self.move(event.globalPos() - self._dragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        鼠标释放重写，用于重设状态
        """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.down_left_text.setText("")
            self.press = False
            event.accept()

    def wheelEvent(self, event):
        """
        鼠标滚动重写，用于切换层数，放缩
        """
        self.setMouseTracking(True)
        angle = event.angleDelta()

        if self.exist and not self.vtk_action.isChecked() and not event.modifiers():
            if angle.y() > 0 and self.number < self.ct_all.shape[2] - 1:
                self.number += 1
                self.sidebar.ct_layer_slider.spin_box.setValue(self.number)
            elif angle.y() < 0 < self.number:
                self.number -= 1
                self.sidebar.ct_layer_slider.spin_box.setValue(self.number)

            self.update_all()

    def keyPressEvent(self, event):
        """
        键盘按下重写，用于各种工具编辑
        """
        super().keyPressEvent(event)

        if event.key() == Qt.Key_Return and self.line_action.isChecked():
            if np.any(self.image.line_list):
                self.draw_list = self.image.line_list
            elif np.any(self.image.eraser_list):
                self.draw_list = self.image.eraser_list

            if np.any(self.draw_list):
                point = []
                for x, y in self.draw_list:
                    point.append([[x, y]])

                point = np.array(point)
                point = np.transpose(point, [1, 0, 2]).astype(np.int32)
                self.draw_list = point
                self.update_image()

                # 清空绘制列表
                self.image.line_list = []
                self.image.eraser_list = []

        if event.key() == Qt.Key_Return and self.frame_action.isChecked() and self.image.segment_state == 0:
            self.operation()

    def prepare_image(self):
        """
        图像加载
        """
        ct = np.array(self.ct_all[:, :, self.number])
        pre = np.array(self.pre_all[:, :, self.number], dtype=np.uint8)
        line = self.draw_list

        ct = self.normalize(ct)

        if np.any(line) and self.image_state != 2:
            poly = self.image.draw_state
            cv2.fillPoly(pre, line, poly)
            self.pre_all[:, :, self.number] = pre
            self.draw_list = []

        if self.image_state != 2:
            pre = np.where(pre >= 0.5, 1, 0).astype(np.uint8)
            pre = pre * 255

            new_pre = np.stack([pre] * 3, axis=-1).astype(np.uint8)
            new_pre[:, :, 1] = 0
            new_pre[:, :, 2] = 0

            if self.image_state == 1:
                new_im = new_pre

        if self.image_state != 1:
            new_ct = np.stack([ct] * 3, axis=-1).astype(np.uint8)
            if self.image_state == 2:
                new_im = new_ct

        if self.image_state == 3:
            new_im = cv2.addWeighted(new_ct, 1, new_pre, self.alpha, 0)

        height, width, channels = new_im.shape
        bytes_per_line = channels * width
        from PySide2.QtGui import QImage
        pre_image = QImage(new_im.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pre_image = QPixmap.fromImage(pre_image)
        return pre_image


if __name__ == "__main__":
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QGuiApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    window = SegmentApp()
    window.show()
    sys.exit(app.exec_())



