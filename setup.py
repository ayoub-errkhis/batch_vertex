from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vertex_batch",
    version="0.0.1",
    author="AYOUB ERRKHIS",
    author_email="ayoub.errkhis@aol.com",
    description="A module for batch processing with Google Cloud Storage and MongoDB integration.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi==0.116.1",
        "pymongo==4.13.2",
        "google-cloud-storage==2.19.0",
        "uvicorn==0.35.0",
        "google-genai==1.28.0",
        "json-repair==0.25.3",
        "redis==4.5.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type="text/markdown",
)