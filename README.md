# Interview-Autograding

> 使用该评测前必读!!! 请你严格按照如下规定进行评测, 否则可能会出现无法预料的问题.

## 解压打包程序

> 请先确保你完成了 **Task 1: 配置运行环境** 的 **第一个任务点: Environment Check** 再进行以下操作, 因为以下操作需要你在 Linux 环境下完成, 请勿在 Windows 下直接操作. 注意: 安装好 Linux 环境之后就能下载本评测程序, 继续后续的测试. 若有不解之处, 请先参阅 `/tasks/task1/README.md`.
> 若使用的是 **macOS**, 请你自行下载[评测程序](https://github.com/Boyuan-IT-Club/Interview-Autograding/releases/latest/download/interview-autograding.tar), 解压到你认为合适的位置, 打开终端. 就可以直接执行`./grade`.

1. 下载到当前目录：

    ```bash
    wget -O interview-autograding.tar \
    "https://github.com/Boyuan-IT-Club/Interview-Autograding/releases/latest/download/interview-autograding.tar"
    ```

2. 解压到当前目录：

    ```bash
    mkdir -p interview-autograding
    tar -xf interview-autograding.tar -C ./interview-autograding
    ```

3. 开始评测：

    ```bash
    cd interview-autograding
    ./grade
    ```

---

## 配置 Git 环境

> 请先确保你完成了 **Task 1: 配置运行环境** 的 **第二个任务点: Git Check** 再进行以下操作, 因为以下操作需要你能够使用 Git 连接 GitHub 完成. 若有不解之处, 请先参阅 `/tasks/task1/README.md`.

### macOS Git 配置

#### 配置用户信息

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git config --list
```

#### 配置 SSH 密钥

1. 生成 SSH 密钥

    ```bash
    ssh-keygen -t ed25519 -C "你的邮箱"
    ```

   * 按回车使用默认路径 `~/.ssh/id_ed25519`
   * 可以设置密码，也可直接回车跳过

2. 启动 SSH Agent 并添加密钥

    ```bash
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    ```

3. 查看并复制公钥

    ```bash
    cat ~/.ssh/id_ed25519.pub
    ```

   * 输出类似：

   ```bash
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBl... 你的邮箱
   ```

   * **复制整行**内容

4. 添加到 GitHub

    * GitHub: [SSH Keys 页面](https://github.com/settings/keys) → New SSH Key → 粘贴 → Add SSH key

5. 测试连接

    ```bash
    ssh -T git@github.com
    ```

    * 成功会显示：

    ```bash
    Hi 用户名! You've successfully authenticated, but GitHub does not provide shell access.
    ```

### Linux Git 配置（Ubuntu/Debian 示例）

#### 配置用户信息

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git config --list
```

#### 配置 SSH 密钥

1. 生成 SSH 密钥

    ```bash
    ssh-keygen -t ed25519 -C "你的邮箱"
    ```

   * 按回车使用默认路径 `~/.ssh/id_ed25519`
   * 可以设置密码，也可直接回车跳过

2. 启动 SSH Agent 并添加密钥

    ```bash
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    ```

3. 查看并复制公钥

    ```bash
    cat ~/.ssh/id_ed25519.pub
    ```

   * 输出类似：

   ```bash
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBl... 你的邮箱
   ```

   * **复制整行**内容

4. 添加到 GitHub

   * GitHub: [SSH Keys 页面](https://github.com/settings/keys) → New SSH Key → 粘贴 → Add SSH key

5. 测试连接

    ```bash
    ssh -T git@github.com   # GitHub
    ```

   * 成功会显示：

   ```bash
   Hi 用户名! You've successfully authenticated, but GitHub does not provide shell access.
   ```

---

## 加入课程

以下先列出所有任务的邀请链接, 只有加入了课程才可以提交评测结果.

* Task 1: 配置运行环境: <https://classroom.github.com/a/rUWTGClc>

* Task 2: 安装 Docker: <https://classroom.github.com/a/Ll_NqVGq>

* Task 3: 基础的 Linux 操作: <https://classroom.github.com/a/_lPiEmCd>

* Task 4: Makefile: <https://classroom.github.com/a/kQFePCsk>

以 **Task 1: 配置运行环境** 为例子, 下面展示如何提交评测报告.

在每一个任务点结束之后, 都会在`task'n'`目录下生成一个加密过的评测报告 (`n`为任务的序号, 请根据实际情况调整, 以下均以`n==1`为例). 假设你的报告位于`~/interview-autograding/tasks/taskn/autograding_report.json`, 并且你已经创建了一个`~/xxx-tasks`的文件夹用于保存你不同任务的报告 (xxx是你的 GitHub 的用户名).

当你加入邀请链接后, GitHub会给你提供一个类似于`https://github.com/Boyuan-Autograder/task-1-xxx`的链接, 请点击进去, 点击绿色的`Code`按钮, 选择 SSH 并且复制下面的 URL. URL 形如`git@github.com:Boyuan-Autograder/task-1-xxx.git`.

这个时候切换到配置好的环境中的命令行:

```bash
cd ~/xxx-tasks

# 将远程仓库克隆到本地
git clone git@github.com:Boyuan-Autograder/task-1-xxx.git 

cd task-1-xxx
```

接下来把你的报告复制到这个文件夹当中. 我们要求你在每一个任务仓库当中新建一个`task'n'`文件夹, 并且在文件夹中放置报告:

```bash
# 新建任务文件夹
mkdir task1

# 复制评测报告到 task1 文件夹
cp ~/interview-autograding/tasks/task1/autograding_report.json ./task1/
```

接着我们提交到远程仓库当中:

```bash
# 添加文件到 Git 暂存区
git add task1/autograding_report.json

# 提交
git commit -m "提交 Task 1 评测报告" # 这里的信息可以修改

# 推送到远程仓库
git push origin main
```

这个时候查看`https://github.com/Boyuan-Autograder/task-1-xxx`, 你会发现 GitHub 正在帮你自动评测你的报告. 你可以点开上边的 `Action` 按钮查看你的得分情况, 正常来说, 这与你执行了`./grade`脚本的得分应该是一致的.

报告提交之后, 管理员可以在后台看到你的得分情况. **你的仓库是不对外公开的**.
