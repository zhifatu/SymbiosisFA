import os
import re

fields_dir = r'D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\core\fields'
fix_count = 0

for filename in os.listdir(fields_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(fields_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否使用 BaseField 但没有导入
        if 'BaseField' in content and 'from falaw.core.base.field_base' not in content:
            # 在文件开头添加导入
            lines = content.split('\n')
            import_line = 'from falaw.core.base.field_base import FieldBase as BaseField\n'

            # 找到第一个 import 之后的位置插入
            for i, line in enumerate(lines):
                if line.startswith('import') or line.startswith('from'):
                    lines.insert(i, import_line)
                    break
            else:
                # 如果没有找到 import，在文件开头添加
                lines.insert(0, import_line)

            new_content = '\n'.join(lines)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'✅ 修复: {filename} (添加 BaseField 导入)')
            fix_count += 1

print(f'\n修复完成，共修改 {fix_count} 个文件')