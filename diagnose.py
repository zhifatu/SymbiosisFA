import sys
import os

print("="*50)
print("系统诊断")
print("="*50)

print(f"\n1. 当前目录: {os.getcwd()}")
print(f"2. Python路径: {sys.executable}")

print("\n3. sys.path:")
for p in sys.path:
    print(f"   - {p}")

print("\n4. 检查包结构:")
try:
    import falaw
    print(f"   ✅ falaw 已安装: {falaw.__file__}")
    print(f"   📦 版本: {falaw.__version__}")
    
    print("\n5. 检查 core 模块:")
    from falaw import core
    print(f"   ✅ falaw.core: {core.__file__}")
    print(f"   📦 core 导出: {dir(core)}")
    
    print("\n6. 检查 fields 模块:")
    from falaw.core import fields
    print(f"   ✅ falaw.core.fields: {fields.__file__}")
    print(f"   📦 fields 导出: {[f for f in dir(fields) if not f.startswith('_')]}")
    
    print("\n7. 尝试导入场类:")
    from falaw.core.fields import PrimalField
    pf = PrimalField()
    print(f"   ✅ PrimalField 创建成功: {pf}")
    
except Exception as e:
    print(f"   ❌ 失败: {e}")

print("\n" + "="*50)
print("诊断完成")
print("="*50)
