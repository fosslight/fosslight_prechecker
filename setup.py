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
    description="fosslight_reuse is now fosslight_prechecker",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=VERSION,
    install_requires=["fosslight_prechecker"],
    classifiers=["Development Status :: 7 - Inactive"],
)
