import sys
sys.path.insert(0, r'D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src')

from falaw.simulator import FALawSimulator

print(f"FALawSimulator 类型: {type(FALawSimulator)}")
print(f"FALawSimulator 是否可调用: {callable(FALawSimulator)}")

try:
    sim = FALawSimulator()
    print("✅ 模拟器创建成功")
except Exception as e:
    print(f"❌ 创建失败: {e}")