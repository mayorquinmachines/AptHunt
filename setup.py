from setuptools import setup
import sys

sys.path.insert(0, 'scraper')

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='AptHunt',
    version='0.1',
    description='Swipe interface for smart filtered apartment hunting',
    url='https://github.com/mayorquinmachines/AptHunt',
    license='MIT',
    long_description=readme(),
    install_requires=["boto3", "python-crontab", "geopy", "lxml", "requests", "simplejson"]
)
