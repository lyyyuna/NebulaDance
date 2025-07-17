import os
import sys
from urllib.parse import urlparse
from pathlib import Path

def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发环境和PyInstaller打包后环境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时文件夹
        base_path = sys._MEIPASS
    else:
        # 开发环境下的当前目录
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def handle_file_url(file_url):
    # 解析 file:// URL
    parsed = urlparse(file_url)
    path = parsed.path
    
    # 处理 Windows 路径（如 /C:/... → C:/...）
    if parsed.netloc:  # 例如 file://hostname/path（较少见）
        path = f"//{parsed.netloc}{path}"
    elif path.startswith("/") and len(path) > 3 and path[2] == ":":
        path = path[1:]  # 移除开头的斜杠（file:///C:/ → C:/）
    
    # 统一转换为系统路径格式
    return Path(path).resolve()  # 自动处理路径分隔符