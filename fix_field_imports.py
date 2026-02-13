import os
import re

fields_dir = r'D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\core\fields'
fix_count = 0

for filename in os.listdir(fields_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(fields_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 修复所有错误的相对导入
        new_content = re.sub(
            r'from \.\.models\.entities',
            'from falaw.models.entities',
            content
        )
        new_content = re.sub(
            r'from \.\.models\.primal_value',
            'from falaw.models.primal_value',
            new_content
        )
        new_content = re.sub(
            r'from \.\.models\.life_state',
            'from falaw.models.life_state',
            new_content
        )

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'✅ 修复: {filename}')
            fix_count += 1

print(f'\n修复完成，共修改 {fix_count} 个文件')