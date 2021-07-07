import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="femmpy",
    version="0.0.1",
    author="Niklas Sallali",
    description="xfemm python bindings and simple geometry manager",
    url="https://github.com/nikisalli/femmpy",
    project_urls={
        "Bug Tracker": "https://github.com/nikisalli/femmpy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'matplotlib',
        'scipy',
        'fuzzywuzzy',
        'shapely'
    ],
    packages=["femmpy"],
    python_requires=">=3.6",
)
