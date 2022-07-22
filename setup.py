from setuptools import setup
import os

VERSION = "2.2.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="fosslight_reuse",
    license='GPL-3.0-only',
    description="fosslight_reuse is now fosslight_prechecker",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=VERSION,
    install_requires=["fosslight_prechecker"],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"],
)
