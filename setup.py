from setuptools import setup, find_packages
from pathlib import Path

VERSION = "0.1.5"
DESCRIPTION = "Easyly post good looking slack messages about your operations"
LONG_DESCRIPTION = (Path(__file__).parent / "README.md").read_text()

setup(
    name="slackops",
    version=VERSION,
    author="Alexey Eremin",
    author_email="haru.eaa@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["pytz", "slack_sdk"],
)
