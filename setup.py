from setuptools import setup, find_packages

VERSION = "0.0.4"
DESCRIPTION = "Easyly post good looking slack messages about your operations"
LONG_DESCRIPTION = "Post process information to the slack without clogging up the channel with a bunch of messages. Easyly update status, see when oreration started / finished and how much time it took."

setup(
    name="slackops",
    version=VERSION,
    author="Alexey Eremin",
    author_email="haru.eaa@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["pytz", "slack_sdk"],
)
