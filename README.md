# vertex_batch Library Documentation

`vertex_batch` is a Python library designed for batch processing and management of payloads. It provides abstractions for database operations, batch file handling, and callback server management, enabling scalable and robust batch processing pipelines.

## Features

- **Batch Database Management**: Store, update, and retrieve conversational payloads for batch processing.
- **Batch File Generation**: Write payloads to batch files for LLM processing (e.g., Gemini).
- **Callback Server**: Receive and process batch results via HTTP callbacks.
- **Integration with LLM Workflows**: Easily integrate with Celery tasks and main application logic.

## Installation

Add `vertex_batch` to your project (ensure it's in your Python path):

```sh
pip install vertex_batch
```

## Usage

### 1. Database Operations

Use [`vertex_batch.db.Db`](vertex_batch/db.py) to interact with the batch database.

```python
from vertex_batch.db import Db

db = Db(
    host="mongo",
    port=27017,
    db_name="batchs",
    batch_collection_name="voc"
)

# Save, update, and retrieve payloads
db.save_payload(payload)
db.update_payload(custom_id="...", status="done")
payloads = db.get_payloads(status="PENDING")
```

### 2. Batch File Generation

Use [`vertex_batch.file.File`](vertex_batch/file.py) to write payloads to batch files and process them with LLMs.

```python
from vertex_batch.file import File
from pathlib import Path
from datetime import datetime

file = File(
    db=db,
    folder_path=Path("batchs_files/input"),
    file_name_format=f"voc_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_batch.jsonl",
    gemini_model="publishers/google/models/gemini-2.5-flash"
)

payloads = db.get_payloads(status="PENDING")
file.write(paylods=payloads)
file.process()
```

### 3. Line Management

Use [`vertex_batch.line.Line`](vertex_batch/line.py) to save individual batch lines for LLM processing.

```python
from vertex_batch.line import Line

line = Line(
    db=db,
    custom_id="conversationId-vocId",
    user_prompt="User prompt text",
    sys_prompt="System prompt text",
    action="extract_feedbacks"
)
line.save()
```

### 4. Callback Server

Use [`vertex_batch.callback.Callback`](vertex_batch/callback.py) to start a callback server that receives batch results and processes them.

```python
from vertex_batch.callback import Callback
from pathlib import Path

def treat_answers(payloads, file_path):
    # Custom logic to process batch results
    pass

callback = Callback(
    db=db,
    port=8010,
    destination_dir=Path("batchs_files/output"),
    func=treat_answers
)

callback.start_server()
```

You can run the callback server in a separate thread:

```python
import threading

threading.Thread(target=callback.start_server, daemon=True).start()
```

## Example Workflow

1. **Save payloads** to the batch database using `Db`.
2. **Generate batch files** for LLM processing using `File`.
3. **Process batch results** via the callback server (`Callback`), which calls your custom handler (`treat_answers`).
4. **Update payloads** and send results to downstream systems (e.g., Kafka).

## Integration with Celery

You can use `vertex_batch` in Celery tasks for asynchronous batch processing:

```python
from vertex_batch.db import Db
from vertex_batch.line import Line
from vertex_batch.file import File

@celery_app.task(name="send_voc_batch")
def send_voc_batch():
    db = Db(...)
    file = File(...)
    payloads = db.get_payloads(status="PENDING")
    file.write(paylods=payloads)
    file.process()
```

## API Reference

### Db

- `Db.save_payload(payload)`
- `Db.update_payload(custom_id, status=None, answer=None)`
- `Db.get_payloads(status)`
- `Db.get_payload(custom_id)`
- `Db.flag_payloads(file_path, flag)`

### File

- `File.write(paylods, is_relaunch=False)`
- `File.process()`

### Line

- `Line.save()`

### Callback

- `Callback(db, port, destination_dir, func)`
- `Callback.start_server()`

### DO NOT FORGET TO SET THOSE OS ENV VARIABLES
- GOOGLE_STORAGE_BUCKET
- GOOGLE_PROJECT_NAME
- GOOGLE_PROJECT_LOCATION
- BATCH_FILE_SIZE_LIMIT

## License

MIT License : AYOUB ERRKHIS

## Contributing

Contributions are welcome! Please submit issues or pull requests via GitHub.

## Contact

For support or questions, contact the maintainers or open an issue on the repository.