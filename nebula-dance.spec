# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 移除 WebEngine 相关文件的函数
def remove_webengine_files():
    # 要排除的二进制文件关键字
    webengine_binaries = [
        'QtWebEngine',
        'QtWebView',
        'QtWebChannel',
        'WebEngine.framework',
        'libQt6WebEngine'
    ]
    
    # 要排除的资源文件路径
    webengine_resources = [
        'PySide6/Qt/resources',
        'PySide6/Qt/translations/qtwebengine',
        'PySide6/Qt/lib/QtWebEngine'
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
    if not any(key in b[0] for key in webengine_bins):
        filtered_binaries.append(b)
a.binaries = filtered_binaries

# 关键步骤 2: 从收集的数据文件中移除 WebEngine 资源
filtered_datas = []
for d in a.datas:
    if not any(key in d[0] for key in webengine_ress):
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
    filter=lambda *args: None if any(key in args[0] for key in webengine_bins + webengine_ress) else args
)

app = BUNDLE(
    coll,
    name='nebula-dance.app',
    icon=None,
    bundle_identifier='com.lyyyuna.www',
)