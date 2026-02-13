from enum import Enum


class ElementType(Enum):
    """八个元素的类型定义"""
    QIAN = ("乾定", 0, "目标确立与标准化")
    SHE = ("射", 1, "观察与扫描")
    XIAN = ("陷", 2, "场沉浸与粘滞")
    LI = ("离", 3, "分离与退出")
    JIE = ("界", 4, "边界与限制")
    SAN = ("散", 5, "扩散与消散")
    HUAN = ("换", 6, "交换与转换")
    KUN = ("坤转", 7, "革命与重建")

    def __init__(self, chinese_name, index, description):
        self.chinese_name = chinese_name
        self.index = index
        self.description = description

    @property
    def symbol(self):
        return self.chinese_name[0] if len(self.chinese_name) > 1 else self.chinese_name

    @classmethod
    def get_by_index(cls, idx):
        for elem in cls:
            if elem.index == idx:
                return elem
        return None