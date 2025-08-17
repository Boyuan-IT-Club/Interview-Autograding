#!/bin/bash

# 检查是否提供了要打包的文件
if [ -z "$1" ]; then
    echo "Error: No Python file specified."
    echo "Usage: ./pack.sh <your_script.py>"
    exit 1
fi

# 检查文件是否存在
if [ ! -f "$1" ]; then
    echo "Error: File not found: $1"
    exit 1
fi

# 定义要打包的 Python 文件
PYTHON_SCRIPT="$1"
# 定义输出的可执行文件名（去掉.py后缀）
EXECUTABLE_NAME=$(basename "$PYTHON_SCRIPT" .py)
# 获取源文件所在的目录
DEST_DIR=$(dirname "$PYTHON_SCRIPT")

echo "Starting to pack $PYTHON_SCRIPT..."

# 使用 PyInstaller 打包
pyinstaller --onefile "$PYTHON_SCRIPT"

# 检查 PyInstaller 是否成功
if [ $? -ne 0 ]; then
    echo "PyInstaller failed. Exiting."
    exit 1
fi

# 将生成的可执行文件移动到源文件所在的目录
mv "dist/$EXECUTABLE_NAME" "$DEST_DIR/"

# 清理所有 PyInstaller 生成的临时目录和文件
rm -rf dist build *.spec

echo "Packing completed successfully!"
echo "Executable saved as $DEST_DIR/$EXECUTABLE_NAME"