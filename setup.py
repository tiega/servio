from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

test_requirements = ["pytest>=3"]

setup(
    author="Tiger Nie",
    author_email="nhl0819@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="",
    keywords="servio",
    long_description=readme,
    name="servio",
    packages=find_packages(include=["servio", "servio.*"]),
    test_requires=test_requirements,
    url="https://github.com/tiega/servio",
    scripts=["bin/servio"],
    version="0.0.2",
    zip_safe=False,
)
