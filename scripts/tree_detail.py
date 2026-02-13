import os
from pathlib import Path
import datetime


def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def print_detailed_tree(root_dir, max_depth=3, current_depth=0, prefix=""):
    """打印详细的目录树"""
    if current_depth > max_depth:
        return

    root = Path(root_dir)

    # 排除的目录
    exclude = {'.git', '__pycache__', '.venv', '.idea', '.vscode',
               'node_modules', '.pytest_cache', '.mypy_cache'}

    try:
        items = []
        for item in root.iterdir():
            if item.name in exclude:
                continue
            # 获取修改时间
            mtime = datetime.datetime.fromtimestamp(item.stat().st_mtime)
            items.append((item, mtime))

        # 按类型和字母排序：目录在前，文件在后
        items.sort(key=lambda x: (not x[0].is_dir(), x[0].name.lower()))

        for i, (item, mtime) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "

            # 图标和颜色
            icon = "📁 " if item.is_dir() else "📄 "
            if item.suffix in ['.py', '.pyc']:
                icon = "🐍 "
            elif item.suffix in ['.md', '.txt']:
                icon = "📝 "
            elif item.suffix in ['.json', '.yaml', '.yml']:
                icon = "⚙️ "

            # 基本信息
            line = prefix + connector + icon + item.name

            # 添加额外信息
            if item.is_file():
                size = format_size(item.stat().st_size)
                line += f" ({size})"
            else:
                line += "/"

            # 添加修改时间（浅色显示）
            time_str = mtime.strftime("%Y-%m-%d %H:%M")
            line += f" \033[90m[{time_str}]\033[0m"

            print(line)

            # 递归处理子目录
            if item.is_dir():
                extension = "    " if is_last else "│   "
                print_detailed_tree(item, max_depth, current_depth + 1, prefix + extension)

    except PermissionError:
        print(prefix + "└── [权限拒绝]")


if __name__ == "__main__":
    project_root = "."  # 当前目录

    print("\033[1;36m" + "=" * 70 + "\033[0m")
    print(f"\033[1;33m项目目录: {os.path.abspath(project_root)}\033[0m")
    print("\033[1;36m" + "=" * 70 + "\033[0m")

    print_detailed_tree(project_root, max_depth=5)

    print("\033[1;36m" + "=" * 70 + "\033[0m")
    print("📁 = 目录, 📄 = 文件, 🐍 = Python文件, 📝 = 文档, ⚙️ = 配置文件")
    print("\033[1;36m" + "=" * 70 + "\033[0m")