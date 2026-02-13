from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import uuid
from datetime import datetime


class FieldBase(ABC):
    """所有场类的抽象基类"""

    def __init__(self, field_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        初始化基础场
        
        Args:
            field_id: 场ID，如果不提供则自动生成
            config: 配置字典
        """
        self.field_id = field_id or f"field_{uuid.uuid4().hex[:8]}"
        self.config = config or {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.name = self.__class__.__name__
        
        # 基础属性
        self.field_strength: float = 0.5  # 场强度 [0,1]
        self.active: bool = True  # 是否激活
        self.metadata: Dict[str, Any] = {}  # 元数据

    @abstractmethod
    def update(self, dt: float = 0.01) -> None:
        """更新场状态（子类必须实现）"""
        pass

    @abstractmethod
    def calculate(self, *args, **kwargs) -> Any:
        """执行场的主要计算（子类必须实现）"""
        pass

    def activate(self) -> None:
        """激活场"""
        self.active = True
        self._update_timestamp()

    def deactivate(self) -> None:
        """停用场"""
        self.active = False
        self._update_timestamp()

    def set_strength(self, strength: float) -> None:
        """设置场强度"""
        self.field_strength = max(0.0, min(1.0, strength))
        self._update_timestamp()

    def get_state(self) -> Dict[str, Any]:
        """获取场的完整状态"""
        return {
            "field_id": self.field_id,
            "name": self.name,
            "field_strength": self.field_strength,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "config": self.config,
            "metadata": self.metadata
        }

    def _update_timestamp(self) -> None:
        """更新时间戳"""
        self.updated_at = datetime.now()

    def __repr__(self) -> str:
        return f"<{self.name}(id={self.field_id}, strength={self.field_strength:.2f})>"
