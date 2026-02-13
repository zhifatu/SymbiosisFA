import sys
import os

print("=" * 70)
print("秩法图框架 - Windows Python 3.14 环境测试")
print("=" * 70)

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"📂 当前目录: {current_dir}")
print(f"🐍 Python版本: {sys.version}")


# 方法1：尝试自动发现模块
def discover_module():
    """自动发现模块位置"""

    # 所有可能的位置
    locations = []

    # 1. 当前目录下的 falaw
    primal_in_current = os.path.join(current_dir, "falaw")
    if os.path.exists(primal_in_current):
        locations.append(primal_in_current)

    # 2. src 目录下的 falaw
    src_dir = os.path.join(current_dir, "src")
    if os.path.exists(src_dir):
        primal_in_src = os.path.join(src_dir, "falaw")
        if os.path.exists(primal_in_src):
            locations.append(primal_in_src)
        else:
            # 检查 src 目录下是否有类似名称的目录
            for item in os.listdir(src_dir):
                item_path = os.path.join(src_dir, item)
                if os.path.isdir(item_path) and "primal" in item.lower():
                    locations.append(item_path)

    # 3. 当前目录下的其他可能目录
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if os.path.isdir(item_path) and "primal" in item.lower():
            locations.append(item_path)

    # 4. 当前目录本身就是模块？
    if "primal" in current_dir.lower():
        locations.append(current_dir)

    # 验证每个位置
    valid_locations = []
    for loc in locations:
        init_file = os.path.join(loc, "__init__.py")
        if os.path.exists(init_file):
            valid_locations.append(loc)

    return valid_locations


# 发现模块
print("\n🔍 搜索模块...")
valid_locs = discover_module()

if valid_locs:
    print(f"✅ 找到 {len(valid_locs)} 个可能位置:")
    for i, loc in enumerate(valid_locs, 1):
        print(f"  {i}. {loc}")

    # 选择第一个有效位置
    chosen_loc = valid_locs[0]
    parent_dir = os.path.dirname(chosen_loc)

    print(f"\n📁 使用位置: {chosen_loc}")
    print(f"📁 父目录: {parent_dir}")

    # 添加到Python路径
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        print(f"✅ 已添加到Python路径: {parent_dir}")

    # 尝试导入
    print("\n🔄 尝试导入...")
    try:
        # 确定模块名
        module_name = os.path.basename(chosen_loc)
        print(f"模块名: {module_name}")

        # 动态导入
        import importlib

        module = importlib.import_module(module_name)
        print(f"✅ 导入 {module_name} 成功!")

        # 尝试导入具体类
        try:
            # 注意：这里使用实际的模块名
            exec(f"from {module_name}.models.entities import Individual")
            print("✅ 导入 Individual 成功!")

            # 测试创建对象
            Individual = eval(f"{module_name}.models.entities.Individual")
            person = Individual(
                entity_id="final_test",
                name="最终测试",
                primal_strength=0.8
            )
            print(f"✅ 创建个体: {person.entity_id}")
            print(f"   原力强度: {person.primal_strength.effective_value}")

        except ImportError as e:
            print(f"❌ 导入具体类失败: {e}")
            print("\n尝试备用导入方法...")

            # 备用方法：直接检查模块内容
            print(f"\n模块 {module_name} 的内容:")
            for attr in dir(module):
                if not attr.startswith('_'):
                    print(f"  - {attr}")

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print(f"\n当前Python路径:")
        for i, path in enumerate(sys.path[:5]):
            print(f"  [{i}] {path}")

else:
    print("❌ 未找到有效的 falaw 模块")
    print("\n当前目录内容:")
    for item in os.listdir(current_dir):
        if os.path.isdir(os.path.join(current_dir, item)):
            print(f"  📁 {item}/")
        elif item.endswith('.py'):
            print(f"  📄 {item}")

    print("\n💡 创建正确的目录结构:")
    print('''
# 选项1：创建 src 结构
mkdir src
mkdir src\\falaw
mkdir src\\falaw\\models
mkdir src\\falaw\\core

# 创建 __init__.py 文件
echo. > src\\falaw\\__init__.py
echo. > src\\falaw\\models\\__init__.py
echo. > src\\falaw\\core\\__init__.py

# 复制你的代码文件到相应位置
''')

print("\n" + "=" * 70)
print("手动修复指南")
print("=" * 70)

print('''
# 方法1：如果代码在 src/falaw/
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 方法2：如果代码在 falaw/
import sys
import os  
sys.path.insert(0, os.path.dirname(__file__))

# 方法3：如果代码在其他位置
import sys
import os
sys.path.insert(0, r"D:\\完整\\路径\\到\\falaw\\的\\父目录")
''')