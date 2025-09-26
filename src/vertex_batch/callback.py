from fastapi import FastAPI, Request
from pathlib import Path
import uvicorn
import json_repair
import asyncio
from .file import File
from .db import Db
import os

class Callback:

    def __init__(self, db:Db, port: int, destination_dir: Path, func: callable = None):
        self.port = port
        self.app = FastAPI()
        self.destination_dir = destination_dir
        self.func = func
        self.db = db

        # register routes
        self.app.post("/callback")(self.callback)

    def _process_file_gemini(self, file_path: Path) -> list:
        try:

            if file_path.suffix != ".jsonl" or not file_path.is_relative_to(Path("output/")):
                raise ValueError("File must be a .jsonl file and starts with output/")

            downloaded_file_path = File.download(
                google_storage_file_path=file_path,
                destination_dir=self.destination_dir
            )
            if not downloaded_file_path:
                raise Exception("Failed to download file from Google Cloud Storage")

            results: list = []

            with open(downloaded_file_path, "r") as file:
                for line in file:
                    data = json_repair.loads(line)

                    response_brut = data.get("response")["candidates"][0]["content"][
                        "parts"
                    ][0]["text"]
                    response = (
                        response_brut.replace("```json", "").replace("```", "").strip()
                    )

                    results.append(
                        {
                            "custom_id": data.get("custom_id", ""),
                            "response": json_repair.loads(response),
                            "tokens": data.get("response")["usageMetadata"].get(
                                "totalTokenCount", 0
                            ),
                        }
                    )

            os.remove(downloaded_file_path)
            
            return results
        except Exception as e:
            print(e)

    async def callback(self, request: Request):
        try:
            custom_function_well_treated = False
            data = await request.json()
            file_path = data.get("name")

            if not file_path:
                raise ValueError("File path is required")

            results = await asyncio.to_thread(
                self._process_file_gemini, Path(file_path)
            )
            
            if not results:
                raise Exception("No results found in the file")
            
            # custom func accepts : results as list and file Path
            if self.func:
                custom_function_well_treated = await asyncio.to_thread(self.func, results, Path(file_path))

            if custom_function_well_treated:
                self.db.update_file(
                    file_path=Path(f"{Path(file_path).parts[2]}.jsonl"),
                    status="DONE"
                )

            local_file_path = self.destination_dir / Path(file_path).name
            local_file_path.unlink(missing_ok=True)

            return {"status": "success"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def start_server(self):
        try:
            uvicorn.run(app=self.app, host="0.0.0.0", port=self.port)
        except Exception as e:
            print(e)
