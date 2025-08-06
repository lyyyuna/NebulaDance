import os
import sys
from urllib.parse import urlparse
from pathlib import Path

def resource_path(relative_path):
    """ 适配 macOS App Bundle 的资源路径 """
    if getattr(sys, 'frozen', False):
        # 1. 先尝试 _MEIPASS（PyInstaller 临时目录）
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
            path = os.path.join(base_path, relative_path)
            if os.path.exists(path):
                return path
        
        # 2. 尝试 Contents/Resources（macOS App Bundle）
        app_bundle_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
        resources_path = os.path.join(app_bundle_path, 'Resources')
        path = os.path.join(resources_path, relative_path)
        if os.path.exists(path):
            return path
    
    # 3. 默认返回当前目录（开发环境）
    return os.path.join(os.path.abspath("."), relative_path)


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