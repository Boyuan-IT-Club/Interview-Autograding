# Task 1: 配置运行环境

对于学习计算机科学的学生来说, Linux 是必修技能, 之后我们的评测都会在 Linux 环境下进行. 所以配置一个趁手的 Linux 环境, 不仅能顺利通过我们的测试, 也为之后在计算机领域深入学习打下一个基础.

> 如果你现在使用的是 **macOS** 或者**原生运行 Linux**, 你可以选择跳过使用 WSL2, 直接开始完成任务2与任务3.

大多数同学使用 Windows, 好在 **WSL2 (Windows Subsystem for Linux)** 可以轻松提供 Linux 环境, 无需在硬盘上单独安装系统. 安装 WSL2 的教程, 可以参阅微软官方链接 [*How to install Linux on Windows with WSL*](https://learn.microsoft.com/en-us/windows/wsl/install). 在这里, 我们不给出详细的安装过程, 你可以在网上搜寻到很多关于 WSL 的安装教程, 甚至可以使用 AI 辅助你安装, 我们相信这同样也是锻炼你解决问题能力的机会.

我们推荐你安装的[发行版](https://zh.wikipedia.org/zh-cn/Linux%E5%8F%91%E8%A1%8C%E7%89%88)是 **Ubuntu**, 这是因为后继的 README 当中有相当一部分都是以 **Debian/Ubuntu**  作为参考, 使用我们推荐的环境可以省去很多麻烦. 当然, **我们也鼓励你尝试使用不同的发行版**.

## 任务

1. 检测你的运行环境 (**50pts**):

    - 如果你运行的是**原生 Linux / macOS**, 你将直接获得 50pts.

    - 如果你运行的是 **WSL**:
      - **WSL2**: 获得 50pts.
      - **WSL1**: 获得 25pts.

2. 检测是否安装了 **Git** (**25pts**)
3. 检测是否安装了 **Python3** (**25pts**)

## 提示

我们假设你已经完成了运行环境的安装. 如果你对于完成这一步感到困难, 可以尽你所能寻求解决方案, 包括但不限于b站甚至是 AI 工具.

接下来的操作可能需要**特定的网络环境**. 如果你正在使用 WSL2 与 Clash, 请打开**TUN模式**, 否则你的代理不会在 WSL2 中生效. 如果你感觉到下载很慢, 那么这一步可能是必要的.

对于不同的操作系统, 安装`Git`和`Python3`的方法不一样, 我们将以`Ubuntu`与`macOS`为例.

### Ubuntu

首先很有必要介绍 **[APT](https://en.wikipedia.org/wiki/APT_(software))** , 这类似于你手机上的"应用商店".

> Advanced Package Tool (APT) is a free-software user interface that works with core libraries to handle the installation and removal of software on Debian and Debian-based Linux distributions. APT simplifies the process of managing software on Unix-like computer systems by automating the retrieval, configuration and installation of software packages, either from precompiled files or by compiling source code.

你可以输入如下的命令并按下回车:

```bash
sudo apt update
```

并且输入你在安装过程中设置的密码. 请注意, **你的密码并不会显示出来**. `update`会做如下的事情:

1. 访问 `/etc/apt/sources.list` 和 `/etc/apt/sources.list.d/` 中定义的软件源。

2. 下载最新的**软件包列表** (包括版本号、依赖信息等).

3. 更新本地缓存, 让系统知道哪些软件包有更新.

> 你可以自己尝试着更换软件源.

之后, 你的软件包列表会更新到最新. 这个时候键入:

```bash
sudo apt upgrade
```

这个时候会提示你有哪些软件可以被更新或者修改, 你可以一路回车.

当你想要安装某个软件包, 你可以输入:

```bash
sudo apt install <软件包名>
```

软件包名通常是小写, 这也提醒了你如何安装`Git`和`Python3`.

你也可以键入:

```bash
apt
```

会列出`apt`的用法, 你可以自己尝试使用不同的命令. 但是请记住, 在绝大多数情况下, 你需要在`apt`前面加上`sudo`. 在这里, 我们暂时不对`sudo`进行解释, 我们会在`task3`详细展开 Linux 的基本命令. 

### macOS

我们强烈推荐你使用 **[Homebrew](https://brew.sh/)**.

> Homebrew is a free and open-source software package management system that simplifies the installation of software on Apple's operating system, macOS, as well as Linux.

使用 Homebrew 的方法和 APT 类似, 但是你需要手动安装这个软件. 你可以在 macOS 的终端输入如下指令来安装:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew --version
```

若展示了版本号, 即说明安装成功.

> 如果出现网络问题, 请确保你已经科学上网.

```bash
brew install <软件包名>
```

软件包名通常是小写, 这也提醒了你如何安装`Git`和`Python3`.

## 评测

```bash
# In Interview-Autograding
cd ./tasks/task1 # 进入到 task1 文件夹
./task1
```

进行以上操作之后, 命令行会显示出你的得分情况, 并且你会得到一份`autograding_report`. 请提交这一份报告作为你完成该任务的证明.
