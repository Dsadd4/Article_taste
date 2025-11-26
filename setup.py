import sys
from cx_Freeze import setup, Executable

# 依赖包
build_exe_options = {
    "packages": ["os", "sys", "json", "requests", "bs4", "PyQt5", "pystray", 
                "PIL", "win32com", "schedule", "matplotlib", "datetime", "re",
                "threading", "io", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets"],
    "include_files": [
        "config.json",
        "cache.json",
        "favorites.json",
        "achat.png",
        "modules/",
        "utils/"
    ],
    "include_msvcr": True,
    "excludes": ["tkinter", "unittest","PyQt5.QtQml", "PyQt5.QtQuick"],
    "zip_include_packages": ["PyQt5"]
}

# 目标文件
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Article_taste",
    version="1.0",
    description="Article_taste Application",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "current_app.py",
            base=base,
            target_name="Article_taste.exe",
            icon="achat.png"
        )
    ]
)