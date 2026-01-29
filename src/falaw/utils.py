import numpy as np
import json
from typing import Dict, Any
from .core import SystemState


def create_initial_state(mode: str = 'ideal', **kwargs) -> SystemState:
    """
    创建初始状态

    Args:
        mode: 'ideal'(理想均衡), 'random'(随机), 'crisis'(危机), 'dominant'(某个元素主导)
        **kwargs: 自定义参数
    """
    if mode == 'ideal':
        # 理想均衡态
        psi = np.full(8, 0.125)  # 总原力=1.0
        return SystemState(psi=psi)

    elif mode == 'random':
        # 随机分布
        psi = np.random.dirichlet(np.ones(8))  # 总和为1
        E = np.random.uniform(0.3, 0.7)
        Pc = np.random.uniform(0.4, 0.8)
        Pd = np.random.uniform(0.2, 0.6)
        return SystemState(psi=psi, E_field=E, P_converge=Pc, P_diverge=Pd)

    elif mode == 'crisis':
        # 危机状态：低共生度，高权力比
        psi = np.random.dirichlet([1, 1, 0.5, 0.5, 2, 2, 1, 1])  # 某些元素弱
        psi = psi / np.sum(psi)  # 确保总和为1
        return SystemState(psi=psi, E_field=0.2, P_converge=0.3, P_diverge=0.7)

    elif mode == 'dominant':
        # 某个元素主导
        dominant_idx = kwargs.get('element', 0)  # 默认乾定主导
        psi = np.ones(8) * 0.05
        psi[dominant_idx] = 0.6  # 该元素占60%
        psi = psi / np.sum(psi)  # 重新归一化
        return SystemState(psi=psi)

    else:
        raise ValueError(f"未知模式: {mode}")


def save_results(results: Dict[str, Any], filename: str):
    """保存模拟结果到文件"""
    # 转换numpy数组为列表以便JSON序列化
    serializable = {}
    for key, value in results.items():
        if isinstance(value, np.ndarray):
            serializable[key] = value.tolist()
        elif isinstance(value, SystemState):
            serializable[key] = {
                'psi': value.psi.tolist(),
                'E_field': value.E_field,
                'P_converge': value.P_converge,
                'P_diverge': value.P_diverge,
                'time': value.time
            }
        else:
            serializable[key] = value

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)

    print(f"结果已保存到 {filename}")


def load_results(filename: str) -> Dict[str, Any]:
    """从文件加载模拟结果"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 恢复SystemState对象
    if 'final_state' in data:
        state_data = data['final_state']
        final_state = SystemState(
            psi=np.array(state_data['psi']),
            E_field=state_data['E_field'],
            P_converge=state_data['P_converge'],
            P_diverge=state_data['P_diverge'],
            time=state_data['time']
        )
        data['final_state'] = final_state

    # 恢复numpy数组
    for key in ['psi_history', 'time_series', 'coordination_history',
                'total_force_history', 'power_ratio_history']:
        if key in data:
            data[key] = np.array(data[key])

    return data


def analyze_stability(psi_history: np.ndarray, window: int = 100) -> Dict[str, Any]:
    """
    分析系统稳定性

    Args:
        psi_history: 元素强度历史 (T, 8)
        window: 滑动窗口大小

    Returns:
        稳定性分析结果
    """
    T, n = psi_history.shape

    # 1. 计算每个元素的变异系数
    cv_per_element = np.std(psi_history, axis=0) / (np.mean(psi_history, axis=0) + 1e-6)

    # 2. 滑动窗口共生度
    coordination_window = []
    for i in range(0, T - window, window//2):
        window_data = psi_history[i:i+window]
        mean_intensity = np.mean(window_data)
        if mean_intensity > 0:
            cv = np.std(window_data) / mean_intensity
            coordination = max(0, 1 - cv)
            coordination_window.append(coordination)

    # 3. 自相关分析
    autocorr_times = []
    for i in range(n):
        if len(psi_history[:, i]) > 1:
            # 简单自相关：与滞后一步的相关性
            if np.std(psi_history[:, i]) > 0:
                corr = np.corrcoef(psi_history[:-1, i], psi_history[1:, i])[0, 1]
                autocorr_times.append(-1 / np.log(abs(corr)) if abs(corr) < 0.99 else 1000)

    return {
        'cv_per_element': cv_per_element,  # 各元素波动性
        'avg_coordination': np.mean(coordination_window) if coordination_window else 0,
        'stability_index': 1 / (np.mean(cv_per_element) + 1e-6),
        'avg_autocorrelation_time': np.mean(autocorr_times) if autocorr_times else 0,
        'is_stable': np.mean(cv_per_element) < 0.3  # 经验阈值
    }