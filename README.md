# [SAMS] - 基于Segment Anything Model的医学图像交互式标注软件

[![PySide6](https://img.shields.io/badge/PyQt-5.15+-green.svg)](https://pypi.org/project/PySide6/)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPLv3-red.svg)](LICENSE)

## 项目简介
SAMS是一个基于PySide6框架开发的跨平台桌面应用程序，专为处理nii.gz格式的医学图像设计。该软件提供了强大的功能来显示、调整窗口级别（调窗）和对医学图像进行标注。结合Segment Anything Model (SAM) 和 MobileSAM 的强大能力，用户可以实现高精度的自动分割与手动精细调整相结合的高效标注流程。

**功能特性**  
✅ 图形界面交互  
✅ 医学图像显示与调窗  
✅ 医学图像标注与编辑  
✅ SAM模型支持的智能标注分割  

## 安装教程
首先要自行下载SAM的配置文件 `sam_vit_b_01ec64.pth` 和MobileSAM的配置文件 `mobile_sam.pt`，并把他们放在model文件夹下。

### 环境要求
确保您的系统满足以下条件：
- Python 3.7+
- PySide6 >=5.15
- 推荐使用开发工具：PyCharm 或 VSCode 配合 Qt Designer 使用

### 快速开始
请按照以下步骤设置您的环境并运行SAMS：

```cmd
# 克隆仓库到本地
git clone https://github.com/cjf128/SAMS.git
cd SAMS

# 创建并激活虚拟环境（以conda为例）
conda create -n SAMS python=3.9
conda activate SAMS

# 安装依赖包
pip install -r requirements.txt

# 安装额外的SAM和MobileSAM依赖
pip install git+https://github.com/facebookresearch/segment-anything.git
pip install git+https://github.com/ChaoningZhang/MobileSAM.git

# 下载必要的模型配置文件，并将其放置在项目的model目录下

# 运行程序
python SAMS.py
```
