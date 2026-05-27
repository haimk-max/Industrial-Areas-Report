from setuptools import setup, find_packages

setup(
    name="signalkit",
    version="0.1.0",
    description="Signal analysis toolkit for groundwater quality monitoring: trend detection, severity calculation, forensics.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Industrial Areas Report Team",
    author_email="haimk@water.gov.il",
    url="https://github.com/haimk-max/industrial-areas-report",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "pandas>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Hydrology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
