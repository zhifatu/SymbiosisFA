@echo off
echo 正在完整修复 SymbiosisFA...
echo.

set SRC=D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\primal_framework
set DST=D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw

echo 1. 复制 models 文件...
copy "%SRC%\models\primal_value.py" "%DST%\models\" /Y
copy "%SRC%\models\entities.py" "%DST%\models\" /Y
copy "%SRC%\models\life_state.py" "%DST%\models\" /Y

echo 2. 复制 core 文件...
copy "%SRC%\core\chaos_field.py" "%DST%\core\fields\" /Y
copy "%SRC%\core\mechanism_field.py" "%DST%\core\fields\" /Y
copy "%SRC%\core\target_field.py" "%DST%\core\fields\" /Y
copy "%SRC%\core\primal_field.py" "%DST%\core\fields\" /Y
copy "%SRC%\core\coordination_field.py" "%DST%\core\fields\" /Y

echo 3. 复制 simulator...
copy "%SRC%\simulator.py" "%DST%\simulator.py" /Y

echo 4. 复制 __init__...
copy "%SRC%\__init__.py" "%DST%\__init__.py" /Y

echo 5. 重新安装...
cd /d D:\Users\Administrator\Documents\GitHub\SymbiosisFA
pip uninstall falaw -y
pip install -e .

echo 6. 测试导入...
python -c "from falaw import FALawSimulator; print('✅ 修复完成！')"

echo.
pause