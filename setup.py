from setuptools import setup, find_packages

setup(
    name="pythonOBIEE",
    version="1.0.0",
    description="A Python package for working with OBIEE via the Web Services SOAP API",
    author="Justin Ostrowsky",
    packages=find_packages(),
    install_requires=["zeep >= 4.2.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
