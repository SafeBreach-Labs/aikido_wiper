from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()
setup(
    name="Aikido Wiper", 
    version="1.0", 
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),  # Required
    console=["wiper_tool/wiper.py"], 
    install_requires=required)
