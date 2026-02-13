
import os

def list_directory(path, indent=0, max_depth=3):
    """列出目录结构"""
    prefix = "  " * indent
    if indent >= max_depth:
        return

    try:
        items = os.listdir(path)
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                print(f"{prefix}📁 {item}/")
                if item not in [".venv", "__pycache__", ".git"]:
                    list_directory(item_path, indent+1, max_depth)
            elif item.endswith(".py"):
                print(f"{prefix}📄 {item}")
    except PermissionError:
        print(f"{prefix}⛔ 无权限访问")

current_dir = os.path.dirname(__file__) or "."
print(f"目录结构: {current_dir}")
print("=" * 50)
list_directory(current_dir)
