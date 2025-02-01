"""Setup file."""

import pathlib
import os
import setuptools

PARENT: pathlib.Path = pathlib.Path(__file__).parent

def _read_requirements():
    requirement_path: str = PARENT / 'requirements.txt'
    packages = open(requirement_path, encoding='utf-8').readlines()
    return [package.removesuffix('\n') for package in packages]

def _read_version():
    init_path: str = os.path.join(PARENT, 'LocalAssistant', '__init__.py')
    return open(init_path, encoding='utf-8').read().split()[-1][1:-1]

setuptools.setup(
    name="LocalAssistant",
    version=_read_version(),
    description="LocalAssistant (locas) is an AI designed to be used in CLI. \
(Currently in development)",
    long_description=pathlib.Path('README.md').read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Linos",
    project_urls={
        "Source": "https://github.com/Linos1391/LocalAssistant",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Environment :: Console",
        "Environment :: GPU :: NVIDIA CUDA",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
    ],
    python_requires=">=3.10",
    install_requires=_read_requirements(),
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["locas = LocalAssistant.main:main"]},
)
