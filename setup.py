from setuptools import setup, find_packages

setup(
    name="modernizeiq",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "sentence-transformers>=2.0.0",
        "torch>=2.0.0",
        "numpy>=1.21.0",
    ],
    python_requires=">=3.8",
)
