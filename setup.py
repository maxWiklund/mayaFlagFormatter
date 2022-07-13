from setuptools import find_packages, setup

import mayaff

setup(
    name="mayaff",
    version=mayaff.__version__,
    packages=find_packages(exclude=("test*", "tests*")),
    url="https://github.com/maxWiklund/mayaFlagFormatter",
    license="Apache License, Version 2.0",
    author="max-wi",
    author_email="",
    scripts=["bin/mayaff"],
    package_data={"mayaff.maya_configs": ["*.json"]},
    description="Format maya command flags",
)
