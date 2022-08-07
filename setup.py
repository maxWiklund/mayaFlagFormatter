# Copyright (C) 2022  Max Wiklund
#
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import find_packages, setup

import mayaff

setup(
    name="mayaff",
    version=mayaff.__version__,
    packages=find_packages(exclude=("test*", "tests*")),
    url="https://github.com/maxWiklund/mayaFlagFormatter",
    license="Apache License, Version 2.0",
    author="Max Wiklund",
    author_email="",
    classifiers=[
        # Get classifiers from: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    scripts=["bin/mayaff"],
    package_data={"mayaff.maya_configs": ["*.json"]},
    description="Format maya command flags",
)
