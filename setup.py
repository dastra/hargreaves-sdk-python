from setuptools import setup, find_packages
import os


def get_version():
    # Get version number from VERSION file
    with open(os.path.join(os.path.dirname(__file__), "hargreaves", "__init__.py")) \
            as version_file:
        # File has format: __version__ = '{version_number}'
        line = version_file.read().split("=")
        version_number = line[1].strip().replace("'", "")
        return version_number


setup(
    name="hargreaves",
    version=get_version(),
    author="Dan Straw",
    url="https://github.com/dastra/hargreaves-sdk-python",
    license="MIT",
    description="Unofficial Python SDK for the Hargreaves Lansdown",
    long_description="Unofficial Python-Client which uses the Hargreaves Lansdown website as though it were an API.",
    test_suite="tests",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "requests",
        "setuptools",
        "beautifulsoup4",
        "argparse",
        "requests-tracker @ git+https://github.com/eladeon/requests-tracker-python@v1.0.3#egg=requests-tracker",
    ]
)
