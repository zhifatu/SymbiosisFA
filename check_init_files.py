import os
import glob

root = r'D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src'
init_files = glob.glob(f'{root}/**/__init__.py', recursive=True)

print(f"找到 {len(init_files)} 个 __init__.py 文件")
print("="*60)

for file in init_files:
    with open(file, 'r', encoding='utf-8') as f:
        try:
            content = f.read()
            lines = content.split('\n')
            # 检查是否包含 PowerShell 命令
            if 'Out-File' in content or '@ |' in content:
                print(f"❌ 有问题: {os.path.relpath(file, root)}")
                print(f"   前3行: {lines[:3]}")
                print()
            else:
                print(f"✅ 正常: {os.path.relpath(file, root)}")
        except Exception as e:
            print(f"⚠️ 无法读取: {os.path.relpath(file, root)} - {e}")