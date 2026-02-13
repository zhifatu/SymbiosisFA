@echo off
echo 正在从 zhifatu-FA2 同步秩法图系统文件...
echo.
echo 源项目: D:\Users\Administrator\Documents\GitHub\zhifatu-FA2
echo 目标项目: D:\Users\Administrator\Documents\GitHub\SymbiosisFA
echo.
echo 警告: 这将覆盖目标项目中的文件！
pause

echo.
echo 1. 同步 models 目录...
xcopy "D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\falaw\models\*.py" "D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\models\" /Y

echo.
echo 2. 同步 core 目录...
xcopy "D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\falaw\core\*.py" "D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\core\" /Y

echo.
echo 3. 同步 core\fields 目录...
xcopy "D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\falaw\core\fields\*.py" "D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\core\fields\" /Y

echo.
echo 4. 同步 simulator.py...
xcopy "D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\falaw\simulator.py" "D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\simulator.py" /Y

echo.
echo 5. 同步 __init__.py...
xcopy "D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\falaw\__init__.py" "D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\__init__.py" /Y

echo.
echo 6. 同步 core\__init__.py...
xcopy "D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\falaw\core\__init__.py" "D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\core\__init__.py" /Y

echo.
echo 7. 同步 core\fields\__init__.py...
xcopy "D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\falaw\core\fields\__init__.py" "D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\core\fields\__init__.py" /Y

echo.
echo 8. 同步 core\base\__init__.py...
xcopy "D:\Users\Administrator\Documents\GitHub\zhifatu-FA2\src\falaw\core\base\__init__.py" "D:\Users\Administrator\Documents\GitHub\SymbiosisFA\src\falaw\core\base\__init__.py" /Y

echo.
echo 同步完成！
echo.
echo 正在重新安装 SymbiosisFA...
cd /d D:\Users\Administrator\Documents\GitHub\SymbiosisFA
pip uninstall falaw -y
pip install -e .

echo.
echo 测试导入...
python -c "from falaw import FALawSimulator; sim = FALawSimulator(); print('✅ 同步成功！系统已就绪！')"

echo.
pause