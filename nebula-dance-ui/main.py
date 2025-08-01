import sys
from PySide6.QtWidgets import (QApplication, QPushButton, QWidget, QVBoxLayout, 
                               QHBoxLayout, QFileDialog, QLabel, QSlider, QProgressBar)
from PySide6.QtCore import Slot, Qt, QThread, Signal
from PySide6.QtGui import QPixmap
import time

class Worker(QThread):
    # 定义信号，用于向主线程传递进度信息
    progress = Signal(int)
    finished = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        # 模拟视频生成过程
        for i in range(101):
            time.sleep(0.05)  # 模拟处理时间
            self.progress.emit(i)  # 发送进度信号
        self.finished.emit()  # 发送完成信号

class VideoProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.file_path = None
        self.setup_stylesheet()
        self.worker = None  # 用于保存工作线程实例
        
    def initUI(self):
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("视频处理工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # 文件加载部分
        file_layout = QHBoxLayout()
        self.load_button = QPushButton("加载文件")
        self.load_button.clicked.connect(self.load_file)
        self.load_button.setObjectName("loadButton")
        self.file_label = QLabel("未选择文件")
        self.file_label.setObjectName("fileLabel")
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(self.file_label)
        layout.addLayout(file_layout)
        
        # 文件显示区域
        self.display_label = QLabel("文件内容将在此显示")
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setMinimumSize(400, 300)
        self.display_label.setObjectName("displayArea")
        layout.addWidget(self.display_label)
        
        # 参数滑块部分
        self.param_label = QLabel("参数调整:")
        self.param_label.setObjectName("paramLabel")
        layout.addWidget(self.param_label)
        
        # 滑块1
        slider_layout1 = QHBoxLayout()
        self.slider1_label = QLabel("参数1:")
        self.slider1 = QSlider(Qt.Horizontal)
        self.slider1.setMinimum(0)
        self.slider1.setMaximum(100)
        self.slider1.setValue(50)
        self.slider1.valueChanged.connect(self.update_preview)
        self.slider1.setObjectName("slider1")
        self.slider1_value = QLabel("50")
        self.slider1_value.setObjectName("sliderValue")
        slider_layout1.addWidget(self.slider1_label)
        slider_layout1.addWidget(self.slider1)
        slider_layout1.addWidget(self.slider1_value)
        layout.addLayout(slider_layout1)
        
        # 滑块2
        slider_layout2 = QHBoxLayout()
        self.slider2_label = QLabel("参数2:")
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setMinimum(0)
        self.slider2.setMaximum(100)
        self.slider2.setValue(30)
        self.slider2.valueChanged.connect(self.update_preview)
        self.slider2.setObjectName("slider2")
        self.slider2_value = QLabel("30")
        self.slider2_value.setObjectName("sliderValue")
        slider_layout2.addWidget(self.slider2_label)
        slider_layout2.addWidget(self.slider2)
        slider_layout2.addWidget(self.slider2_value)
        layout.addLayout(slider_layout2)
        
        # 生成视频按钮
        self.generate_button = QPushButton("生成视频")
        self.generate_button.clicked.connect(self.generate_video)
        self.generate_button.setEnabled(False)
        self.generate_button.setObjectName("generateButton")
        layout.addWidget(self.generate_button)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progressBar")
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle("视频处理工具")
        self.setMinimumSize(500, 600)
        
    def setup_stylesheet(self):
        stylesheet = """
        /* 主窗口样式 */
        QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 11pt;
        }
        
        /* 标题样式 */
        QLabel#title {
            font-size: 18pt;
            font-weight: bold;
            color: #64b5f6;
            padding: 10px;
            qproperty-alignment: AlignCenter;
        }
        
        /* 文件标签样式 */
        QLabel#fileLabel {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
            min-height: 20px;
        }
        
        /* 显示区域样式 */
        QLabel#displayArea {
            background-color: #1e1e1e;
            border: 2px solid #555555;
            border-radius: 6px;
            padding: 10px;
            color: #aaaaaa;
            font-size: 10pt;
        }
        
        /* 参数标签样式 */
        QLabel#paramLabel {
            font-size: 12pt;
            font-weight: bold;
            color: #90caf9;
            margin-top: 10px;
        }
        
        /* 滑块值标签样式 */
        QLabel#sliderValue {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 2px 8px;
            min-width: 30px;
            qproperty-alignment: AlignCenter;
        }
        
        /* 按钮通用样式 */
        QPushButton {
            background-color: #2196f3;
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-height: 30px;
        }
        
        QPushButton:hover {
            background-color: #1e88e5;
        }
        
        QPushButton:pressed {
            background-color: #1976d2;
        }
        
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        
        QPushButton#loadButton {
            background-color: #4caf50;
        }
        
        QPushButton#loadButton:hover {
            background-color: #43a047;
        }
        
        QPushButton#loadButton:pressed {
            background-color: #388e3c;
        }
        
        QPushButton#generateButton {
            background-color: #f44336;
            font-size: 12pt;
            padding: 10px;
        }
        
        QPushButton#generateButton:hover {
            background-color: #e53935;
        }
        
        QPushButton#generateButton:pressed {
            background-color: #d32f2f;
        }
        
        /* 滑块样式 */
        QSlider {
            min-height: 20px;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #999999;
            height: 8px;
            background: #3c3c3c;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #64b5f6;
            border: 1px solid #2196f3;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #bbdefb;
        }
        
        QSlider::sub-page:horizontal {
            background: #2196f3;
            border-radius: 4px;
        }
        
        /* 进度条样式 */
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 4px;
            text-align: center;
            height: 25px;
            background-color: #3c3c3c;
        }
        
        QProgressBar::chunk {
            background-color: #4caf50;
            border-radius: 3px;
        }
        """
        self.setStyleSheet(stylesheet)
        
    @Slot()
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"已选择: {file_path}")
            self.display_label.setText(f"文件已加载: {file_path}")
            self.generate_button.setEnabled(True)
            
            # 如果是图片文件，显示图片
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    self.display_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))
            
    @Slot()
    def update_preview(self):
        # 更新滑块值显示
        self.slider1_value.setText(str(self.slider1.value()))
        self.slider2_value.setText(str(self.slider2.value()))
        
        # 实时预览逻辑
        if self.file_path:
            preview_text = f"预览 - 参数1: {self.slider1.value()}, 参数2: {self.slider2.value()}"
            if not isinstance(self.display_label.pixmap(), QPixmap) or self.display_label.pixmap().isNull():
                self.display_label.setText(preview_text)
            
    @Slot()
    def generate_video(self):
        # 禁用生成按钮，显示进度条
        self.generate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 创建并启动工作线程
        self.worker = Worker()
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.video_generation_finished)
        self.worker.start()
        
    @Slot()
    def video_generation_finished(self):
        # 视频生成完成后重新启用按钮并隐藏进度条
        self.generate_button.setEnabled(True)
        self.display_label.setText("视频生成完成！")
        # 可以选择在完成后隐藏进度条
        # self.progress_bar.setVisible(False)

def main():
    app = QApplication(sys.argv)
    window = VideoProcessor()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()