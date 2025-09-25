# Batch Processing Module

This project provides a batch processing module that facilitates the management of batch file processing, uploading to Google Cloud Storage, and tracking status in MongoDB. It is designed to handle batch requests efficiently and integrates with FastAPI for callback handling.

## Features

- **Batch Processing**: Manage and process batch files with ease.
- **Google Cloud Storage Integration**: Upload and manage files in Google Cloud Storage.
- **MongoDB Tracking**: Keep track of file statuses and metadata in MongoDB.
- **FastAPI Callbacks**: Handle file processing via FastAPI callbacks.

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

1. **Set Up Environment Variables**: Ensure the following environment variables are set:
   - `MONGO_DB_URI`: MongoDB connection URI.
   - `GOOGLE_STORAGE_BUCKET`: Google Cloud Storage bucket name.
   - `GOOGLE_PROJECT_NAME`: Google Cloud project name.
   - `GOOGLE_PROJECT_LOCATION`: Google Cloud project location (default: "us-central1").
   - `FILE_SIZE_LIMIT`: Maximum file size in bytes for batch processing (default: 10485760).

2. **Run the Application**: Start the FastAPI application by running the `callback.py` module.

3. **Create Batch Lines**: Use the `Batch_line` class to create and write batch lines to a file.

4. **Process Batch Files**: Use the `Batch` class to manage and process batch files.