# util

`pack.sh` 是一个用于将 Python 脚本打包为独立可执行文件的便捷脚本。本指南将详细说明如何使用它。

## 先决条件

在运行此脚本之前，请确保你的系统已安装以下工具和依赖：

1. **Python 3**:

   * 请确保你的系统安装了 Python 3。

   * 为了方便，我们强烈建议你设置 `python` 别名指向 `python3`。

2. **`pyinstaller`**:

   * 这是一个用于打包 Python 脚本的工具。

   * 请使用 `pip` 命令进行安装：

     ```bash
     pip install pyinstaller
     ```

3. **`pycryptodome`**:

   * 这是一个用于数据加密的 Python 库。

   * 请使用 `pip` 命令进行安装：

     ```bash
     pip install pycryptodome
     ```

## 使用方法

`pack.sh` 脚本的用法非常简单，它接受一个参数：你想要打包的 Python 文件的路径。

**语法：**

````bash
./pack.sh \<your\_script.py\>
```

**示例：**
假设你的项目结构如下：

```bash
.
├── etc/
├── tasks/
│   └── task1/
│       └── task1.py
└── pack.sh
```

要打包 `task1.py`，你需要在项目根目录执行以下命令：

```bash
./pack.sh tasks/task1/task1.py
```

脚本执行后，将在 `tasks/task1/` 目录下生成一个名为 `task1` 的可执行文件，并自动清理所有临时文件。
