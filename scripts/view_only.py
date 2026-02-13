import os

print("查看当前文件状态")
print("=" * 60)

files_to_view = [
    ('src/falaw/__init__.py', '主包初始化'),
    ('src/falaw/core/__init__.py', 'core初始化'),
    ('src/falaw/core/fields/__init__.py', 'fields初始化'),
]

for filepath, description in files_to_view:
    print(f"\n{description}: {filepath}")
    print("-" * 50)

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"大小: {len(content)} 字符")
        print("内容:")
        print(content[:500])  # 只显示前500字符
        if len(content) > 500:
            print("... (省略余下内容)")
    else:
        print("文件不存在")

print("\n" + "=" * 60)