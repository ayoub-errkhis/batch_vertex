from setuptools import setup, find_packages

setup(
    name="vertex_batch",
    version="0.1.1",
    author="AYOUB ERRKHIS",
    author_email="ayoub.errkhis.dev@gmail.com",
    description="A module for batch processing with Google Cloud Storage and MongoDB integration.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi==0.116.1",
        "pymongo==4.13.2",
        "google-cloud-storage==3.2.0",
        "uvicorn==0.35.0",
        "google-genai==1.28.0",
        "json-repair==0.48.0",
        "redis==6.4.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)