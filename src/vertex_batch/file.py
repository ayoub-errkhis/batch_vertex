from .db import Db
from pathlib import Path
from google.cloud import storage
import os
from google.genai.types import CreateBatchJobConfig, HttpOptions
from google import genai
import logging

logging.basicConfig(
    level=logging.INFO
)


class File:
    def __init__(
        self, db: Db, folder_path: Path, file_name_format: str, gemini_model: str
    ):
        self.folder_path = folder_path
        self.file_name_format = file_name_format
        self.db = db
        self.file_path = None
        self.gemini_model = gemini_model

    def _increment_relaunch_counters(self, custom_id: str):
        try:
            current_data = self.db.get_payload(custom_id=custom_id)
            if current_data and 'relaunched' in current_data:
                self.db.update_payload(
                    custom_id=custom_id,
                    relaunched=current_data['relaunched'] + 1
                )
            else:
                self.db.update_payload(
                    custom_id=custom_id,
                    relaunched=1
                )
        except Exception as e:
            logging.exception(f"Error incrementing relaunch counters: {e}")

    def _create(self) -> None:
        try:
            self.folder_path.mkdir(parents=True, exist_ok=True)
            self.file_path = self.folder_path / self.file_name_format
            if not self.file_path.exists():
                self.file_path.touch()
                self.db.save_file(
                    file_path=str(self.file_path.name),
                    file_size=0,
                    status="created"
                )
                logging.info(f"File {self.file_path} created.")
            else:
                logging.info(f"File {self.file_path} already exists.")
        except Exception as e:
            logging.exception(f"Error creating file: {e}")

    def _delete(self):
        if self.file_path.exists():
            self.file_path.unlink()
            self.file_path = None
            logging.info(f"File successfuly deleted.")
        else:
            logging.info(f"File does not exist.")

    def write(self, paylods: list, is_relaunch:bool= False) -> bool:
        try:

            if not paylods:
                return False

            if self.file_path is None:
                self._create()

            if self.file_size_exceed_limits():
                self.process()
                self._create()

            with open(self.file_path, "a") as file:
                for payload in paylods:
                    custom_id = payload['custom_id']
                    output_schema = payload.get("output_schema", None)
                    
                    if is_relaunch:
                        self._increment_relaunch_counters(custom_id=custom_id)

                    line_content = {
                        "custom_id": payload["custom_id"],
                        "request": {
                            "contents": [
                                {
                                    "role": "user",
                                    "parts": [{"text": payload["user_prompt"]}],
                                }
                            ],
                            "generationConfig": {
                                "temperature": payload["temperature"],
                                "top_p": payload["top_p"],
                                "max_output_tokens": payload["max_output_tokens"],
                            },
                            "systemInstruction": {
                                "parts": [{"text": payload["sys_prompt"]}],
                            },
                        },
                    }

                    if output_schema :
                        line_content["request"]["generationConfig"]["responseMimeType"] = "application/json"
                        line_content["request"]["generationConfig"]["responseSchema"] = output_schema

                    file.write(f"{line_content}\n")

                    self.db.update_payload(
                        custom_id=custom_id,
                        status="WRITTEN",
                        file_name=self.file_path.name
                    )

            self.db.update_file(
                file_path=Path(self.file_path.name),
                file_size=self.file_path.stat().st_size
            )

            return True
        except Exception as e:
            logging.exception(f"Error writing to file: {e}")
            return False

    def _upload(self, file_path: Path) -> str:
        try:
            # Init client
            client = storage.Client()

            # Get bucket
            bucket_name = os.getenv("GOOGLE_STORAGE_BUCKET")
            bucket = client.bucket(bucket_name)

            # Create blob object inside "input/" folder
            blob = bucket.blob(f"input/gemini/{file_path.name}")

            # Upload file from path
            blob.upload_from_filename(str(file_path))

            return f"gs://{bucket_name}/input/gemini/{file_path.name}"

        except Exception as e:
            logging.exception(f"Upload failed: {e}")
            raise

    def process(self):
        try:

            if self.file_path is None:
                logging.info("File not found.")
                return

            google_storage_file = self._upload(self.file_path)

            vertex_client = genai.Client(
                vertexai=True,
                http_options=HttpOptions(api_version="v1"),
                project=os.getenv("GOOGLE_PROJECT_NAME"),
                location=os.getenv("GOOGLE_PROJECT_LOCATION", "us-central1"),
            )

            output_file = f"gs://{os.getenv('GOOGLE_STORAGE_BUCKET')}/output/gemini/{os.path.splitext(os.path.basename(self.file_path))[0]}"

            vertex_client.batches.create(
                model=self.gemini_model,
                src=google_storage_file,
                config=CreateBatchJobConfig(dest=output_file),
            )

            self.db.update_file(
                file_path=Path(self.file_path.name),
                status="processing"
            )

            self.db.flag_payloads(
                file_path=Path(self.file_path.name),
                flag="PROCESSING"
            )

            self._delete()

        except Exception as e:
            logging.exception(e)

    def file_size_exceed_limits(self):
        try:
            if self.file_path is None or not self.file_path.exists():
                logging.info("File does not exist.")
                return False
            file_size = self.file_path.stat().st_size
            max_size = int(os.getenv("BATCH_FILE_SIZE_LIMIT", 2)) * 1024 * 1024  # 10 MB in bytes
            if file_size > max_size:
                logging.info(f"File size {file_size} bytes exceeds limits.")
                return True
            else:
                logging.info(f"File size {file_size} bytes is within the limit.")
                return False
        except Exception as e:
            logging.exception(e)
    
    @staticmethod
    def download(google_storage_file_path: Path, destination_dir: Path) -> Path:
        try:
            client = storage.Client()
            bucket = client.bucket(os.getenv("GOOGLE_STORAGE_BUCKET"))
            blob = bucket.blob(str(google_storage_file_path))

            # Split the GCS path into parts
            blob_parts = str(google_storage_file_path).strip("/").split("/")

            # Get the third part for prefix (index 2)
            folder_name = blob_parts[2] if len(blob_parts) >= 3 else "unknown"

            # Get the original filename
            original_filename = os.path.basename(str(google_storage_file_path))

            # Build the dynamic filename
            dynamic_filename = f"{folder_name}_{original_filename}"

            # Ensure destination directory exists
            os.makedirs(destination_dir, exist_ok=True)

            output_file_path = destination_dir / dynamic_filename

            # Download file
            blob.download_to_filename(output_file_path)

            return output_file_path

        except Exception as e:
            logging.exception(e)
            return None
