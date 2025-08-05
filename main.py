import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from backend import Backend, ImageProcessor
from utils import resource_path


app = QGuiApplication(sys.argv)
# 设置使用Material风格
QQuickStyle.setStyle("Material")
engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)

image_processor = ImageProcessor()
engine.addImageProvider("processor", image_processor)

backend = Backend(image_processor=image_processor)
engine.rootContext().setContextProperty("backend", backend)

engine.load(resource_path("main.qml"))

sys.exit(app.exec())