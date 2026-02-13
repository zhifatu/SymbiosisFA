from .enums import ElementType
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import numpy as np


class Entity:
    """实体基类"""

    def __init__(self, id: str = "", name: str = ""):
        self.id = id
        self.name = name
        self.life_state = LifeState.ALIVE

    @property
    def is_alive(self) -> bool:
        return self.life_state == LifeState.ALIVE


class LifeState(Enum):
    """生命状态"""
    ALIVE = "alive"
    DORMANT = "dormant"
    EXTINCT = "extinct"


class TargetType(Enum):
    """目标类型"""
    ETERNAL = "eternal"
    COLLECTIVE = "collective"
    INDIVIDUAL = "individual"
    IMMEDIATE = "immediate"


@dataclass
class PrimalValue:
    """原力值"""
    value: float
    unit: str = "primal_unit"
    certainty: float = 0.8
    timestamp: float = 0.0

    def __post_init__(self):
        self.value = max(0.0, min(1.0, self.value))
        self.certainty = max(0.0, min(1.0, self.certainty))

    @property
    def effective_value(self) -> float:
        return self.value * self.certainty

    @property
    def is_significant(self) -> bool:
        return self.value > 0.1

    def increase(self, amount: float) -> float:
        self.value = min(1.0, self.value + amount)
        return self.value

    def to_dict(self) -> Dict:
        return {
            'value': self.value,
            'certainty': self.certainty,
            'effective': self.effective_value
        }


@dataclass
class Individual(Entity):
    """个体"""
    id: str
    name: str = ""
    life_state: LifeState = LifeState.ALIVE
    primal_strength: PrimalValue = field(default_factory=lambda: PrimalValue(0.5))
    excitation_capacity: float = 0.7
    current_targets: List[Dict] = field(default_factory=list)
    target_history: List[Dict] = field(default_factory=list)
    attributes: Dict[str, float] = field(default_factory=lambda: {
        'resilience': 0.6,
        'adaptability': 0.5,
        'cooperation': 0.4,
        'aggression': 0.3
    })

    def __post_init__(self):
        if not hasattr(self, 'id'):
            self.id = ""

    def excite_primal(self) -> Dict:
        """原力激发"""
        excitation = self.primal_strength.value * self.excitation_capacity
        self.primal_strength.increase(excitation * 0.1)
        return {
            'entity': self.id,
            'excitation_generated': excitation,
            'new_primal': self.primal_strength.value
        }

    def pursue_targets(self) -> List[Dict]:
        """追求目标"""
        results = []
        for target in self.current_targets[:]:
            results.append({
                'type': target.get('type', 'unknown'),
                'target': target.get('content', ''),
                'status': 'pursuing'
            })
        return results

    def check_survival(self) -> Dict:
        """检查生存状态"""
        if self.primal_strength.value <= 0.1:
            self.life_state = LifeState.EXTINCT
            return {'alive': False, 'reason': 'primal_depletion'}
        return {'alive': True}

    def eliminate(self, other: 'Individual', reason: str) -> Dict:
        """消灭其他个体"""
        if not self.is_alive or not other.is_alive:
            return {'success': False, 'reason': 'not_excitable'}

        target = {
            'type': 'elimination',
            'target': other.id,
            'reason': reason,
            'justification': 'primal_excitation_maximization'
        }
        self.current_targets.append(target)
        other.life_state = LifeState.EXTINCT

        return {
            'success': True,
            'eliminator': self.id,
            'eliminated': other.id,
            'reason': reason,
            'as_target_pursuit': True,
            'type': 'elimination',
            'eliminated_entity': other.id,
            'justification': 'primal_excitation_maximization',
            'target_based': True
        }


@dataclass
class Collective(Entity):
    """集体"""
    id: str
    name: str = ""
    members: List[Individual] = field(default_factory=list)
    collective_primal: PrimalValue = field(default_factory=lambda: PrimalValue(0.6))
    collective_targets: List[Dict] = field(default_factory=list)
    field_cohesion: float = 0.6
    field_fragmentation: float = 0.2

    def __post_init__(self):
        if not hasattr(self, 'id'):
            self.id = ""
        self.life_state = LifeState.ALIVE

    @property
    def size(self) -> int:
        return len(self.members)

    @property
    def average_primal(self) -> float:
        if not self.members:
            return 0.0
        return np.mean([m.primal_strength.effective_value for m in self.members])

    def pursue_targets(self) -> List[Dict]:
        """追求集体目标"""
        results = []
        for target in self.collective_targets[:]:
            results.append({
                'type': 'collective_pursuit',
                'target': target.get('content', ''),
                'status': 'pursuing'
            })
        return results

    def construct_target(self, target_content: str) -> Dict:
        """构建集体目标"""
        target = {
            'type': 'collective',
            'content': target_content,
            'constructors': [m.id for m in self.members],
            'timestamp': 0.0
        }
        self.collective_targets.append(target)

        for member in self.members:
            increase = 0.05 * member.excitation_capacity
            member.primal_strength.increase(increase)

        return {
            'collective': self.id,
            'target': target,
            'field_cohesion_increase': 0.1,
            'primal_boost': True
        }

    def lose_target(self, target_index: int) -> Dict:
        """丧失目标"""
        if 0 <= target_index < len(self.collective_targets):
            lost_target = self.collective_targets.pop(target_index)
            self.field_cohesion -= 0.2
            self.field_fragmentation += 0.3
            return {
                'event': 'target_lost',
                'collective': self.id,
                'lost_target': lost_target,
                'field_cohesion': self.field_cohesion,
                'field_fragmentation': self.field_fragmentation,
                'kunzhuan_risk': 'high' if self.field_cohesion < 0.4 else 'medium'
            }
        return {'event': 'no_such_target'}


@dataclass
class Environment:
    """环境"""
    pressure_level: float = 0.3
    resource_abundance: float = 0.7
    stability: float = 0.6
    chaos_potential: float = 0.2
    novelty_potential: float = 0.4

    def apply_pressure(self, individual: Individual) -> float:
        pressure_factor = self.pressure_level * (1 - individual.attributes['resilience'])
        return pressure_factor

    def is_changing(self, threshold: float = 0.7) -> bool:
        return (self.chaos_potential + self.novelty_potential) > threshold


@dataclass
class Phenomenon:
    """现象"""
    name: str
    description: str
    intensity: float
    participants: List[Union[Individual, Collective]]
    involves_elimination: bool = False
    target_related: bool = True
    field_impact: float = 0.5

    @property
    def primal_intensity(self) -> float:
        participant_primal = np.mean([
            p.primal_strength.effective_value
            for p in self.participants
            if hasattr(p, 'primal_strength')
        ]) if self.participants else 0.0
        return self.intensity * participant_primal


__all__ = [
    'Entity',
    'LifeState',
    'TargetType',
    'PrimalValue',
    'Individual',
    'Collective',
    'Environment',
    'Phenomenon',
    'ElementType'
]