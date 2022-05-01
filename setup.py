import os
import re
from setuptools import setup, find_packages


def get_pyproject_version():
    """Read the version name in pyproject.toml"""
    pyproject_toml = os.path.join(os.path.dirname(__file__), "pyproject.toml")
    with open(pyproject_toml) as f:
        for line in f.readlines():
            m = re.match('version = "([0-9]\\.[0-9]\\.[0-9])"', line)
            if m is not None:
                return m.group(1)


def get_readme_file():
    """
    Open this project's README.md
    """
    readme_md = os.path.join(os.path.dirname(__file__), "README.md")
    with open(readme_md) as f:
        return f.read()


setup(
    name="thermopi",
    version=get_pyproject_version(),
    author="Adrian Ciobanita",
    author_email="aciokkan@gmail.com",
    include_package_data=True,
    maintainer="Adrian Ciobanita",
    maintainer_email="aciokkan@gmail.com",
    license="MIT - Crown Copyright",
    url="https://github.com/ciobania/thermopi",
    description="ThermoPi is a smart thermostat using RPi Zero 2 W",
    long_description=get_readme_file(),
    long_description_content_type='text/markdown',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["configs/*", "images/*", "fonts/*"]},
    python_requires=">=3.8",
    entry_points={"pytest11": ["thermopi = thermopi.thermopi"]},
    classifiers=["Framework :: Pytest"],
)
