import os
import sys

# 添加项目根目录到 Python 路径（关键修复！）
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
project = '秩法图理论 SymbiosisFA'
copyright = '2026, 秩法图理论研究组'
author = '秩法图理论研究组'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # 从 docstring 自动生成文档
    'sphinx.ext.napoleon',     # 支持 Google/NumPy 风格 docstring
    'sphinx.ext.viewcode',     # 添加源代码链接
    'sphinx.ext.todo',         # 支持 TODO 标记
    'sphinx.ext.coverage',     # 文档覆盖率检查
]

# autodoc 配置
autodoc_default_options = {
    'members': True,
    'undoc-members': True,     # 显示没有文档的成员
    'show-inheritance': True,  # 显示继承关系
    'special-members': '__init__',
}

# napoleon 配置（Google 风格 docstring）
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'zh_CN'  # 中文界面

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # 更专业的 ReadTheDocs 主题
html_static_path = ['_static']

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True