import re
import ast
from pathlib import Path


def scan_file_for_hardcoded_values(filepath):
    """扫描单个文件，返回所有可疑的数字常量"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 只检查赋值语句中的数字
    pattern = r'(\w+)\s*[=:]\s*(\d+\.?\d*)'
    matches = re.findall(pattern, content)

    suspicious = []
    for var_name, value in matches:
        # 过滤明显不是阈值的变量
        if any(kw in var_name.lower() for kw in ['theta', 'threshold', 'limit', 'max', 'min', 'bound']):
            suspicious.append((var_name, value, filepath))

    return suspicious


# 运行扫描
for py_file in Path('src/falaw/core/fields').glob('*.py'):
    results = scan_file_for_hardcoded_values(py_file)
    for var, val, path in results:
        print(f"{path}: {var} = {val}")