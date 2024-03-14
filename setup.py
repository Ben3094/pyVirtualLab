from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-16") as fh:
    install_requires = [line.strip() for line in fh.readlines()]

with open("tests_requirements.txt", "r", encoding="utf-16") as fh:
    test = [line.strip() for line in fh.readlines()]

setup(
    name='pyVirtualLab',
    version='0.1.8',
    author='Benjamin SAGGIN',
    description='An abstraction library for laboratory instruments',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Ben3094/pyNewportController',
    project_urls = {
        "Bug Tracker": "https://github.com/Ben3094/pyNewportController/issues"
    },
    license='MIT',
    packages=find_packages(),
    install_requires=install_requires,
)