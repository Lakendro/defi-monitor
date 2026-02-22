from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="defi-monitor",
    version="1.0.0",
    author="DeFi Monitor Team",
    author_email="your-email@example.com",
    description="DeFi protocol monitoring tool with TVL, yield, and price tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/defi-monitor",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/defi-monitor/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "web3>=6.11.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
    entry_points={
        "console_scripts": [
            "defi-monitor=monitor:main",
        ],
    },
)
