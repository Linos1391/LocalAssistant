"""Setup file."""

import pathlib
import setuptools

setuptools.setup(
    name="LocalAssistant",
    version="1.1.0",
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
    install_requires=[
        "transformers[torch]",
        "bitsandbytes",
        "sentence-transformers",
        "PyMuPDF",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["locas = LocalAssistant.main:main"]},
)
