from setuptools import setup, find_packages

setup(
    name="falaw",
    version="1.0.0",
    author="秩法图理论研究组",
    author_email="example@zhifatu.org",
    description="基于原力激发宇宙观的完整秩法图实现框架",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",

    packages=find_packages(where="src"),
    package_dir={"": "src"},

    install_requires=[
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
        "networkx>=3.0",
        "matplotlib>=3.5.0",
    ],

    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=0.991",
            "pylint>=2.15.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ]
    },

    python_requires=">=3.9",

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],

    keywords="philosophy, complex systems, social dynamics, primal theory",

    project_urls={
        "Documentation": "https://zhifatu.github.io/primal-framework/",
        "Source Code": "https://github.com/zhifatu/primal-framework",
        "Bug Tracker": "https://github.com/zhifatu/primal-framework/issues",
    },
)