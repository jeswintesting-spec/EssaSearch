from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="essasearch",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A high-performance, full-text distributed search engine written entirely in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/EssaSearch",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "requests",
        "rich",
        "sentence-transformers",
        "torch"
    ],
    entry_points={
        "console_scripts": [
            "essasearch=cli:main",
        ],
    },
)
