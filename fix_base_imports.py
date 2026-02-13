import os
import re

fields_dir = r'D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\core\fields'
fix_count = 0

for filename in os.listdir(fields_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(fields_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 修复所有错误的 .base 导入
        new_content = re.sub(
            r'from \.base import BaseField',
            'from falaw.core.base.field_base import FieldBase',
            content
        )
        new_content = re.sub(
            r'from \.\.base import FieldBase',
            'from falaw.core.base.field_base import FieldBase',
            new_content
        )
        new_content = re.sub(
            r'from \.base\.field_base import FieldBase',
            'from falaw.core.base.field_base import FieldBase',
            new_content
        )

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'✅ 修复: {filename}')
            fix_count += 1

print(f'\n修复完成，共修改 {fix_count} 个文件')