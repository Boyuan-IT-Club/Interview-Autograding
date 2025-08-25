#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: No Python file specified."
    echo "Usage: ./pack.sh <path/to/your_script.py>"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Error: File not found: $1"
    exit 1
fi

PYTHON_SCRIPT="$1"
DEST_DIR=$(dirname "$PYTHON_SCRIPT")
SCRIPT_BASENAME=$(basename "$PYTHON_SCRIPT")
EXECUTABLE_NAME=$(basename "$SCRIPT_BASENAME" .py)

echo "--> Changing directory to ${DEST_DIR}"
pushd "$DEST_DIR" > /dev/null

if [ -f "build_quiz.py" ] && [ -f "questions.qmd" ]; then
    echo "--> Found quiz components. Generating quiz_data.py..."
    python3 build_quiz.py --qmd questions.qmd --output quiz_data.py

    if [ $? -ne 0 ]; then
        echo "✗ Error: build_quiz.py failed. Exiting."
        popd > /dev/null
        exit 1
    fi
    echo "✓ quiz_data.py generated successfully."
else
    echo "--> No quiz components found. Proceeding with standard packing."
fi

echo "--> Starting to pack ${SCRIPT_BASENAME} with PyInstaller..."
pyinstaller --onefile --clean --noconfirm "$SCRIPT_BASENAME"

if [ $? -ne 0 ]; then
    echo "✗ Error: PyInstaller failed. Exiting."
    rm -f quiz_data.py
    popd > /dev/null
    exit 1
fi

echo "--> Cleaning up build artifacts..."
mv "dist/$EXECUTABLE_NAME" .
rm -rf dist build *.spec
if [ -f "quiz_data.py" ]; then
    echo "--> Cleaning up generated quiz module..."
    rm quiz_data.py
fi

popd > /dev/null

echo "✓ Packing completed successfully!"
echo "✓ Executable saved as ${DEST_DIR}/${EXECUTABLE_NAME}"

