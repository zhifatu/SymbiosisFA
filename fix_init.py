import os

init_path = r'D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\__init__.py'

with open(init_path, 'w', encoding='utf-8') as f:
    f.write('"""falaw - 秩法图理论模拟框架"""\n\n')
    f.write('from .simulator import FALawSimulator\n')
    f.write('from .models.primal_value import PrimalValue, ElementType\n')
    f.write('from .models.entities import Individual, Collective, LifeState\n\n')
    f.write('__all__ = [\n')
    f.write('    "FALawSimulator",\n')
    f.write('    "PrimalValue",\n')
    f.write('    "ElementType",\n')
    f.write('    "Individual",\n')
    f.write('    "Collective",\n')
    f.write('    "LifeState",\n')
    f.write(']\n')

print("✅ __init__.py 已重置为最简版本")