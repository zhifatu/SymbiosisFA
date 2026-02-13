"""
生命状态相关定义
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class LifeState(Enum):
    """生命状态枚举"""
    ALIVE = "alive"           # 活着
    EXTINCT = "extinct"      # 灭绝
    TRANSITIONING = "transitioning"  # 过渡状态
    PSEUDO_ALIVE = "pseudo_alive"    # 伪存活（文化、组织等）


@dataclass
class ExtinctionRecord:
    """灭绝记录"""
    entity_id: str
    extinction_time: float
    cause: str
    primal_value_at_extinction: float
    related_entities: Optional[list] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'entity_id': self.entity_id,
            'extinction_time': self.extinction_time,
            'cause': self.cause,
            'primal_value_at_extinction': self.primal_value_at_extinction,
            'related_entities': self.related_entities or []
        }


def check_life_transition_valid(old_state: LifeState, new_state: LifeState) -> bool:
    """检查生命状态转换是否有效"""
    valid_transitions = {
        LifeState.ALIVE: [LifeState.TRANSITIONING, LifeState.EXTINCT],
        LifeState.TRANSITIONING: [LifeState.ALIVE, LifeState.EXTINCT, LifeState.PSEUDO_ALIVE],
        LifeState.PSEUDO_ALIVE: [LifeState.TRANSITIONING, LifeState.EXTINCT],
        LifeState.EXTINCT: []  # 灭绝是不可逆的
    }

    return new_state in valid_transitions.get(old_state, [])


__all__ = ['LifeState', 'ExtinctionRecord', 'check_life_transition_valid']
