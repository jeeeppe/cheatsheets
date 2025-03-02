from setuptools import setup, find_packages

setup(
    name="cheatsheet-collection",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "fuzzywuzzy>=0.18.0",
        "python-Levenshtein>=0.12.0",  # Optional dependency for faster fuzzy matching
    ],
    entry_points={
        "console_scripts": [
            "cheatsheet=src.main:cli",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A command-line tool for managing and accessing personal cheat sheets",
    keywords="cheatsheet, cli, collection",
    url="https://github.com/yourusername/cheatsheet-collection",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.9",
)
