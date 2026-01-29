import numpy as np
from typing import List, Dict, Any, Optional, Callable
from .core import SystemState, FALawDynamics, DynamicsParameters


class FALawSimulator:
    """秩法图模拟器"""

    def __init__(self,
                 initial_state: Optional[SystemState] = None,
                 params: Optional[DynamicsParameters] = None):
        """
        初始化模拟器

        Args:
            initial_state: 初始系统状态，默认使用理想协调态
            params: 动力学参数，默认使用预设参数
        """
        self.params = params or DynamicsParameters()
        self.dynamics = FALawDynamics(self.params)

        # 设置初始状态
        if initial_state is None:
            # 默认：理想协调态
            psi_ideal = np.full(8, 0.125)  # 总原力=1.0
            self.initial_state = SystemState(psi=psi_ideal)
        else:
            self.initial_state = initial_state

        # 模拟历史记录
        self.history: List[SystemState] = []
        self.time_points: List[float] = []

        # 重置模拟器
        self.reset()

    def reset(self):
        """重置模拟器到初始状态"""
        self.history = [self.initial_state]
        self.time_points = [self.initial_state.time]
        self.current_state = self.initial_state

    def run(self,
            duration: float = 100.0,
            dt: float = 0.01,
            progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        运行模拟

        Args:
            duration: 模拟时长
            dt: 时间步长
            progress_callback: 进度回调函数

        Returns:
            包含模拟结果的字典
        """
        num_steps = int(duration / dt)

        print(f"开始模拟: 时长={duration}, 步数={num_steps}, dt={dt}")

        for step in range(num_steps):
            # 积分一步
            new_state = self.dynamics.integrate_step(self.current_state, dt)

            # 记录历史
            self.history.append(new_state)
            self.time_points.append(new_state.time)

            # 更新当前状态
            self.current_state = new_state

            # 进度回调
            if progress_callback and step % 100 == 0:
                progress = step / num_steps
                progress_callback(progress, new_state)

            # 坤转发生后重置历史记录（新纪元开始）
            if step > 0 and self.check_kunzhuan_occurred(step):
                print(f"纪元结束于 t={new_state.time:.2f}")
                # 可以在这里保存当前纪元的数据

        print(f"模拟完成. 最终时间: {self.current_state.time:.2f}")

        return self.get_results()

    def check_kunzhuan_occurred(self, current_step: int) -> bool:
        """检查最近是否发生了坤转"""
        if len(self.history) < 2:
            return False

        # 检查最后两步的坤转倾向
        prev_state = self.history[-2]
        curr_state = self.history[-1]

        # 如果坤转元素强度突然增加，可能发生了坤转
        if curr_state.psi[7] > prev_state.psi[7] + 0.5:
            return True

        return False

    def get_results(self) -> Dict[str, Any]:
        """整理模拟结果"""
        # 提取时间序列数据
        time_series = self.time_points

        # 元素强度时间序列
        psi_history = np.array([state.psi for state in self.history])  # (T, 8)

        # 关键指标时间序列
        coordination_history = [state.coordination_degree for state in self.history]
        total_force_history = [state.total_primal_force for state in self.history]
        power_ratio_history = [state.power_ratio for state in self.history]

        # 坤转事件检测
        kunzhuan_events = []
        for i, state in enumerate(self.history):
            conditions = self.dynamics.check_kunzhuan_conditions(state)
            if conditions >= 3 and state.psi[7] > 0.8:  # 坤转强度高
                kunzhuan_events.append({
                    'time': state.time,
                    'conditions': conditions,
                    'state_before': self.history[i-1].psi if i > 0 else None,
                    'state_after': state.psi
                })

        return {
            'time_series': time_series,
            'psi_history': psi_history,
            'coordination_history': coordination_history,
            'total_force_history': total_force_history,
            'power_ratio_history': power_ratio_history,
            'kunzhuan_events': kunzhuan_events,
            'final_state': self.current_state,
            'num_steps': len(self.history)
        }

    def run_multiple_trials(self,
                           num_trials: int = 10,
                           duration: float = 50.0,
                           dt: float = 0.01) -> List[Dict[str, Any]]:
        """运行多次试验，返回结果列表"""
        results = []

        for trial in range(num_trials):
            print(f"\n试验 {trial+1}/{num_trials}")

            # 每次试验使用不同的随机初始状态
            random_psi = np.random.dirichlet(np.ones(8))  # 总和为1的随机向量
            initial_state = SystemState(
                psi=random_psi,
                E_field=np.random.uniform(0.3, 0.7),
                P_converge=np.random.uniform(0.4, 0.8),
                P_diverge=np.random.uniform(0.2, 0.6)
            )

            # 创建新模拟器
            simulator = FALawSimulator(initial_state=initial_state, params=self.params)
            result = simulator.run(duration=duration, dt=dt)
            results.append(result)

        return results

    def set_parameter(self, param_name: str, value: Any):
        """动态设置参数"""
        if hasattr(self.params, param_name):
            setattr(self.params, param_name, value)
            print(f"参数 {param_name} 已更新为 {value}")
        else:
            raise AttributeError(f"参数 {param_name} 不存在")