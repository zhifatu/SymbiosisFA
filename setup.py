from setuptools import setup, find_packages

setup(
    name="falaw",
    version="1.0.0",
    author="秩法图理论研究组",
    description="秩法图理论模拟框架",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
    ],
    python_requires=">=3.8",
)