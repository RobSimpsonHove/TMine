import sys
from cx_Freeze import setup, Executable

## This script needs to be run >python3 setup3.py build
# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["tkinter"],"include_files": ["C:\\Users\\ro020si\\Python36\\DLLs\\tcl86t.dll", "C:\\Users\\ro020si\\Python36\DLLs\\tk86t.dll", "C:\\Users\\ro020si\\Documents\\Python\\TextMine\\src\\utils", "C:\\Users\\ro020si\\Documents\\Python\\TextMine\\src\\README.txt", "C:\\Users\\ro020si\\Documents\\Python\\TextMine\\src\\icon.ico"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

import os

os.environ['TCL_LIBRARY'] = "C:\\Users\\ro020si\\Python36\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Users\\ro020si\\Python36\\tcl\\tk8.6"

setup(  name = "TMine",
        version = "3.40",
        description = "TMine42",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Tmine42.py", base=base,icon="icon.ico")])

