from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lucifer-ml",
    version="0.0.1-alpha",
    description="Automated ML by d4rk-lucif3r",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/d4rk-lucif3r/LuciferML",
    download_url= "https://github.com/d4rk-lucif3r/LuciferML/archive/v_01.tar.gz",
    author="Arsh Anwar",
    author_email="lucifer78908@gmail.com",
    license="MIT",
    packages=find_packages(
        exclude=["*.examples"]),
    install_requires=open("requirements.txt").readlines(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords=[
        "automated ML",
        "classification",
        "luciferML"
    ],
)
