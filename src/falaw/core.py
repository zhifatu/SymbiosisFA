import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, ClassVar


@dataclass
class Element:
    """秩法图八元素定义"""
    id: int
    name: str
    symbol: str
    description: str = ""

    # 类变量定义八元素常量
    ELEMENTS: ClassVar[Dict[int, 'Element']] = None

    @classmethod
    def _init_elements(cls):
        """初始化八元素常量"""
        if cls.ELEMENTS is None:
            cls.ELEMENTS = {
                1: cls(1, "乾定", "QD", "目标设定与持久化"),
                2: cls(2, "射", "S", "观察与扫描"),
                3: cls(3, "陷", "X", "沉浸与原力场"),
                4: cls(4, "离", "L", "退出与脱离"),
                5: cls(5, "界", "J", "边界与反馈"),
                6: cls(6, "散", "SA", "扩散与消散"),
                7: cls(7, "换", "H", "交换与可能性拓展"),
                8: cls(8, "坤转", "KZ", "革命与重建")
            }

    @classmethod
    def get_all(cls) -> List['Element']:
        cls._init_elements()
        return list(cls.ELEMENTS.values())

    @classmethod
    def get_name(cls, id: int) -> str:
        cls._init_elements()
        return cls.ELEMENTS[id].name

    @classmethod
    def get_by_id(cls, id: int) -> 'Element':
        cls._init_elements()
        return cls.ELEMENTS[id]


@dataclass
class SystemState:
    """系统状态容器"""
    # 元素强度向量 (ψ₁, ..., ψ₈)
    psi: np.ndarray  # shape: (8,)
    # 可能性场 (简化为一维标量)
    E_field: float = 0.5
    # 权力场 (收敛与发散)
    P_converge: float = 0.6
    P_diverge: float = 0.4
    # 时间
    time: float = 0.0

    def __post_init__(self):
        if self.psi.shape != (8,):
            raise ValueError(f"psi must have shape (8,), got {self.psi.shape}")

    @property
    def total_primal_force(self) -> float:
        """总原力 Φ = Σψᵢ (公理M1)"""
        return np.sum(self.psi)

    @property
    def mean_intensity(self) -> float:
        """平均强度 ψ̄ = Φ/8"""
        return self.total_primal_force / 8

    @property
    def coordination_degree(self) -> float:
        """共生度 S (公理S2)"""
        if self.mean_intensity == 0:
            return 0.0
        # 简化的共生度：1 - 变异系数
        std = np.std(self.psi)
        cv = std / self.mean_intensity if self.mean_intensity > 0 else 1.0
        return max(0.0, 1.0 - cv)

    @property
    def power_ratio(self) -> float:
        """权力比 r = P_d / P_c (公理D5)"""
        if self.P_converge == 0:
            return float('inf')
        return self.P_diverge / self.P_converge

    def normalize(self, target_total: float = 1.0):
        """归一化总原力到指定值"""
        current_total = self.total_primal_force
        if current_total > 0:
            self.psi = self.psi * (target_total / current_total)


class DynamicsParameters:
    """动力学参数容器 (对应我们之前估计的所有参数)"""

    def __init__(self):
        # 元素基础激发系数 γ_i (表1)
        self.gamma = np.array([0.05, 0.1, 0.08, 0.12, 0.06, 0.07, 0.15, 0.01])

        # 转移矩阵 α_ij (表2): 行i接收，列j给出
        self.transfer_matrix = np.array([
            [0, 0.15, 0.05, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.10, 0, 0.03, 0.02, 0.00, 0.00, 0.08, 0.00],
            [0.20, 0.03, 0, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.02, 0.25, 0, 0.05, 0.00, 0.00, 0.03],
            [0.00, 0.00, 0.00, 0.03, 0, 0.10, 0.04, 0.00],
            [0.00, 0.00, 0.00, 0.00, 0.07, 0, 0.12, 0.05],
            [0.00, 0.05, 0.00, 0.00, 0.02, 0.10, 0, 0.00],
            [0.00, 0.00, 0.00, 0.02, 0.00, 0.03, 0.00, 0]
        ])

        # 平衡敏感性 β (表3)
        self.beta = 2.0

        # 元素强度上限 (表1)
        self.psi_max = np.full(8, 0.5)

        # 射元素参数 (表4)
        self.I_max = 0.3  # 最大内在能力
        self.kappa = 1.0  # 可能性场耦合系数

        # 散元素参数 (表4)
        self.k_dissipate = 0.2  # 消散率
        self.k_coalesce = 0.1  # 凝聚率

        # 坤转阈值 (表5)
        self.theta_immerse = 0.05  # ψ₃ 陷场消散阈值
        self.theta_target = 0.01  # |∇ψ₁| 目标瓦解阈值
        self.theta_order = 0.2  # λ_max 秩序崩溃阈值
        self.theta_conflict = 0.5  # 冲突指数阈值

        # 权力动力学参数 (表6)
        self.c0 = 0.05  # 收敛贡献基础率
        self.d0 = 0.03  # 发散耗散基础率
        self.kappa_power = 1.5  # 收敛敏感性
        self.lambda_power = 2.0  # 发散敏感性
        self.r_critical = 1.0  # 临界权力比

        # 激发函数自抑制系数 (稳定性分析用)
        self.excitation_self_inhibit = -0.2

    def validate(self):
        """验证参数合理性"""
        assert self.gamma.shape == (8,)
        assert self.transfer_matrix.shape == (8, 8)
        assert np.all(np.diag(self.transfer_matrix) == 0), "转移矩阵对角线应为0"
        return True


class FALawDynamics:
    """秩法图动力学引擎"""

    def __init__(self, params: Optional[DynamicsParameters] = None):
        self.params = params or DynamicsParameters()
        self.params.validate()

    def compute_excitation(self, state: SystemState, i: int) -> float:
        """计算第i个元素的激发项 I_i (方程具体化)"""
        psi = state.psi

        if i == 0:  # 乾定 (1)
            # I₁ = |∇G|² · (1 - ψ₁/ψ₁_max)
            # 简化：目标梯度与系统协调度正相关
            target_gradient = state.coordination_degree
            return target_gradient ** 2 * (1 - psi[0] / self.params.psi_max[0])

        elif i == 1:  # 射 (2)
            # I₂ = H(R - T)
            # R = 内部能力，简化：与ψ₂和可能性场E正相关
            R = 0.5 * psi[1] + 0.5 * state.E_field
            # T = I_max * exp(-κ * E / I_internal)
            I_internal = psi[1] + 0.01  # 避免除零
            T = self.params.I_max * np.exp(-self.params.kappa * state.E_field / I_internal)
            return 1.0 if R > T else 0.0

        elif i == 2:  # 陷 (3)
            # I₃ = D(专注度) · [1 - B(边界感知)]
            # 专注度与乾定ψ₁正相关，边界感知与界ψ₅正相关（注意：界是第5个元素，索引4）
            focus = 0.8 * psi[0] + 0.2  # 确保正值
            boundary = min(1.0, psi[4] * 2)  # ψ₅是界
            return focus * (1 - boundary)

        elif i == 3:  # 离 (4)
            # I₄ = -dψ₃/dt|_陷 + ∇ψ₅·n
            # 简化：当陷场过强或边界压力大时激发
            immerse_strength = psi[2]
            boundary_pressure = psi[4]  # ψ₅是界
            if immerse_strength > 0.3:  # 陷过深
                return 0.5 * (immerse_strength - 0.3) + 0.1 * boundary_pressure
            return 0.1 * boundary_pressure

        elif i == 4:  # 界 (5)
            # I₅ = ρ_F · (B_hard - B_soft)
            # 简化：反馈密度与系统不协调度正相关
            feedback_density = 1.0 - state.coordination_degree
            boundary_diff = 0.5  # 常数差
            return feedback_density * boundary_diff

        elif i == 5:  # 散 (6)
            # I₆ = -k_diss·ψ_凝·f(S) + k_pol·ψ_散·g(∇Φ)
            # 简化：与系统原力分布均匀度相关
            uniformity = 1.0 - np.std(psi) / (np.mean(psi) + 1e-6)
            dissipate_term = -self.params.k_dissipate * psi[5] * uniformity
            coalesce_term = self.params.k_coalesce * (1 - psi[5]) * (1 - uniformity)
            return dissipate_term + coalesce_term

        elif i == 6:  # 换 (7)
            # I₇ = Σ η_ij Δψ_ij · Diversity(Ψ)
            # 简化：与系统多样性和总交换潜力相关
            diversity = len(set(np.round(psi * 10))) / 10  # 简单多样性度量
            exchange_potential = np.mean(psi) * diversity
            return 0.8 * exchange_potential  # η=0.8

        elif i == 7:  # 坤转 (8)
            # I₈ = H(∏ (C_k > θ_k))
            # 检查坤转条件是否满足
            conditions_met = self.check_kunzhuan_conditions(state)
            return 1.0 if conditions_met >= 3 else 0.0  # 至少3个条件

        else:
            raise ValueError(f"元素索引超出范围: {i}")

    def compute_transfer_coeff(self, state: SystemState, i: int, j: int) -> float:
        """计算转移系数 T_ij = α_ij * exp(-β * |ψ_i - ψ_j|)"""
        alpha = self.params.transfer_matrix[i, j]
        psi_diff = abs(state.psi[i] - state.psi[j])
        return alpha * np.exp(-self.params.beta * psi_diff)

    def compute_flow_term(self, state: SystemState, i: int) -> float:
        """计算流动项：Σ_j [T_ji ψ_j - T_ij ψ_i]"""
        flow = 0.0
        psi = state.psi
        for j in range(8):
            if i == j:
                continue
            T_ji = self.compute_transfer_coeff(state, j, i)  # j → i
            T_ij = self.compute_transfer_coeff(state, i, j)  # i → j
            flow += T_ji * psi[j] - T_ij * psi[i]
        return flow

    def compute_power_dynamics(self, state: SystemState) -> Tuple[float, float]:
        """计算权力动力学：dΦ/dt = γΦ [C(r) - D(r)]"""
        r = state.power_ratio

        # 收敛贡献项
        if r <= self.params.r_critical:
            C = self.params.c0
        else:
            excess = r - self.params.r_critical
            C = self.params.c0 * np.exp(-self.params.kappa_power * excess)

        # 发散耗散项
        if r <= self.params.r_critical:
            D = self.params.d0
        else:
            excess = r - self.params.r_critical
            D = self.params.d0 * np.exp(self.params.lambda_power * excess)

        dPhi_dt = 0.05 * state.total_primal_force * (C - D)  # γ=0.05
        return dPhi_dt, r

    def check_kunzhuan_conditions(self, state: SystemState) -> int:
        """检查坤转条件，返回满足的条件数量"""
        conditions = 0

        # 1. 陷场消散：ψ₃ < θ₃
        if state.psi[2] < self.params.theta_immerse:
            conditions += 1

        # 2. 目标瓦解：|∇ψ₁| < θ₁
        # 简化：用乾定强度的变化率近似梯度
        if state.psi[0] < self.params.theta_target:
            conditions += 1

        # 3. 秩序崩溃：λ_max(Cov(Ψ)) > θ_λ
        # 简化：用元素强度的方差代替
        if np.var(state.psi) > self.params.theta_order:
            conditions += 1

        # 4. 元素冲突：冲突指数 > θ_conflict
        # 简化：用最大最小元素强度比
        if np.max(state.psi) / (np.min(state.psi) + 1e-6) > 5.0:
            conditions += 1

        return conditions

    def compute_dpsi_dt(self, state: SystemState) -> np.ndarray:
        """计算状态向量导数：dΨ/dt = γ·I + Flow"""
        dpsi = np.zeros(8)

        # 激发项 + 流动项
        for i in range(8):
            excitation = self.params.gamma[i] * self.compute_excitation(state, i)
            flow = self.compute_flow_term(state, i)
            dpsi[i] = excitation + flow

        return dpsi

    def integrate_step(self, state: SystemState, dt: float = 0.01) -> SystemState:
        """单步积分：欧拉法"""
        # 计算导数
        dpsi = self.compute_dpsi_dt(state)

        # 更新元素强度
        new_psi = state.psi + dpsi * dt
        new_psi = np.clip(new_psi, 0, self.params.psi_max)  # 边界约束

        # 更新可能性场（简化：缓慢变化）
        dE = 0.01 * (state.coordination_degree - state.E_field) * dt
        new_E = state.E_field + dE

        # 更新权力场（简化：与权力比相关）
        dPhi_dt, r = self.compute_power_dynamics(state)
        # 权力场演化：收敛权力增长使发散权力相对减少
        new_Pc = state.P_converge + 0.01 * (1 - r) * dt
        new_Pd = state.P_diverge + 0.01 * (r - 1) * dt
        new_Pc = np.clip(new_Pc, 0.1, 0.9)
        new_Pd = np.clip(new_Pd, 0.1, 0.9)

        # 创建新状态
        new_state = SystemState(
            psi=new_psi,
            E_field=new_E,
            P_converge=new_Pc,
            P_diverge=new_Pd,
            time=state.time + dt
        )

        # 检查坤转
        if self.check_kunzhuan_conditions(new_state) >= 3:
            new_state = self.apply_kunzhuan(new_state)

        return new_state

    def apply_kunzhuan(self, state: SystemState) -> SystemState:
        """应用坤转变换：摧毁与重建"""
        print(f"[坤转] 在 t={state.time:.2f} 触发系统重建")

        # 1. 摧毁：指数衰减偏离均衡的部分
        psi_eq = np.full(8, state.total_primal_force / 8)  # 理想均衡
        psi_destroyed = 0.7 * state.psi + 0.3 * psi_eq  # 向均衡回归70%

        # 2. 重建：随机扰动创造新结构
        random_shift = np.random.normal(0, 0.1, 8)
        psi_rebuilt = psi_destroyed + random_shift
        psi_rebuilt = np.clip(psi_rebuilt, 0, self.params.psi_max)

        # 3. 重置权力场（更均衡）
        new_Pc = 0.7
        new_Pd = 0.3

        return SystemState(
            psi=psi_rebuilt,
            E_field=0.5,  # 重置可能性场
            P_converge=new_Pc,
            P_diverge=new_Pd,
            time=state.time
        )