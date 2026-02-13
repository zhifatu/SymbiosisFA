import sys
import importlib


def import_module_safe(module_path, class_name=None):
    """安全导入模块或类"""
    try:
        module = importlib.import_module(module_path)
        if class_name:
            return getattr(module, class_name)
        return module
    except (ImportError, AttributeError) as e:
        print(f"警告: 无法导入 {module_path}.{class_name if class_name else ''}: {e}")
        return None


# 动态导入所有模块
primal_field = import_module_safe('src.falaw.core.primal_field')
target_field = import_module_safe('src.falaw.core.target_field')
mechanism_field = import_module_safe('src.falaw.core.mechanism_field')
coordination_field = import_module_safe('src.falaw.core.coordination_field')
chaos_field = import_module_safe('src.falaw.core.chaos_field')
entities = import_module_safe('src.falaw.models.entities')
simulator = import_module_safe('src.falaw.simulator')


# 提供统一的接口类
class UnifiedInterface:
    """统一的秩法图接口"""

    @staticmethod
    def get_primal_field():
        """获取原力场类"""
        if primal_field:
            # 尝试获取类名
            for attr in ['PrimalField', 'PrimalForceField']:
                if hasattr(primal_field, attr):
                    return getattr(primal_field, attr)
        return None

    @staticmethod
    def get_target_field():
        """获取目标场类"""
        if target_field:
            for attr in ['TargetField', 'GoalField']:
                if hasattr(target_field, attr):
                    return getattr(target_field, attr)
        return None

    @staticmethod
    def get_simulator():
        """获取模拟器类"""
        if simulator:
            for attr in ['FALawSimulator', 'Simulator', 'FaSimulator']:
                if hasattr(simulator, attr):
                    return getattr(simulator, attr)
        return None

    @staticmethod
    def create_default_simulator():
        """创建默认模拟器"""
        SimulatorClass = UnifiedInterface.get_simulator()
        if SimulatorClass:
            try:
                return SimulatorClass()
            except Exception as e:
                print(f"创建模拟器失败: {e}")
                return None
        return None

    @staticmethod
    def list_available_modules():
        """列出所有可用模块"""
        modules = []
        for name, module in [
            ('primal_field', primal_field),
            ('target_field', target_field),
            ('mechanism_field', mechanism_field),
            ('coordination_field', coordination_field),
            ('chaos_field', chaos_field),
            ('entities', entities),
            ('simulator', simulator)
        ]:
            if module:
                classes = [attr for attr in dir(module) if not attr.startswith('_')]
                modules.append((name, classes[:5]))  # 只显示前5个
        return modules


# 导出
UnifiedSimulator = UnifiedInterface.get_simulator()