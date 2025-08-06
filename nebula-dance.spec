# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 移除 WebEngine 相关文件的函数
def remove_webengine_files():
    # 要排除的二进制文件关键字 (适用于不同平台)
    webengine_binaries = [
        'QtWebEngine',
        'QtWebView',
        'QtWebChannel',
        'WebEngine.framework',  # macOS
        'libQt6WebEngine',      # Linux
        'Qt6WebEngine',         # Windows/Linux
        'webengine'             # 通用匹配
    ]
    
    # 要排除的资源文件路径 (适用于不同平台)
    webengine_resources = [
        'PySide6/Qt/resources',
        'PySide6/Qt/translations/qtwebengine',
        'PySide6/Qt/lib/QtWebEngine',
        'PySide6/Qt/plugins/webengine',     # Windows/Linux
        'PySide6/Qt/lib/QtWebView',        # macOS
        'PySide6/Qt/lib/QtWebEngineCore',  # 通用
        'webengine'                        # 通用匹配
    ]
    
    return webengine_binaries, webengine_resources

# 获取排除列表
webengine_bins, webengine_ress = remove_webengine_files()

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('main.qml', '.'), ('star2.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebView',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineQuick',
        'PySide6.QtWebChannel',  # 确保添加这个
        'webview',
        'pywebview'
    ],
    noarchive=False,
    optimize=0,
)

# 关键步骤 1: 从收集的二进制文件中移除 WebEngine 组件
filtered_binaries = []
for b in a.binaries:
    # 转换为小写进行匹配，提高跨平台兼容性
    binary_path_lower = b[0].lower()
    if not any(key.lower() in binary_path_lower for key in webengine_bins):
        filtered_binaries.append(b)
a.binaries = filtered_binaries

# 关键步骤 2: 从收集的数据文件中移除 WebEngine 资源
filtered_datas = []
for d in a.datas:
    # 转换为小写进行匹配，提高跨平台兼容性
    data_path_lower = d[0].lower()
    if not any(key.lower() in data_path_lower for key in webengine_ress):
        filtered_datas.append(d)
a.datas = filtered_datas

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='nebula-dance',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 关键步骤 3: 在 COLLECT 阶段再次过滤
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='nebula-dance',
    # 添加文件过滤回调
    filter=lambda *args: None if any(key.lower() in args[0].lower() for key in webengine_bins + webengine_ress) else args
)

import sys
if sys.platform == 'darwin':  # macOS
    app = BUNDLE(
        coll,
        name='nebula-dance.app',
        icon=None,
        bundle_identifier='com.lyyyuna.www',
    )