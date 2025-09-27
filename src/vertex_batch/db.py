from pymongo import MongoClient
from datetime import datetime
from pathlib import Path


class Db:
    def __init__(self, url: str, db_name: str, batch_collection_name: str, file_collection_name: str = "file_infos"):
        self.url = url
        self.db_name = db_name
        self.batch_collection_name = batch_collection_name
        self.file_collection_name = file_collection_name

    def _connect(self):
        try:
            client = MongoClient(self.url)
            return client
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def _close(self, client: MongoClient):
        if client:
            client.close()
        
    def flag_payloads(self, file_path: Path, flag: str):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                result = collection.update_many(
                    {"file_name": file_path.name},
                    {"$set": {"status": flag, "updated_at": datetime.now()}}
                )
                if result.matched_count:
                    print(f"All payloads for file {file_path.name} flagged as {flag}.")
                else:
                    print(f"No payloads found for file {file_path.name}.")
            except Exception as e:
                print(f"Error flagging payloads: {e}")
            finally:
                self._close(client)
        else:
            print("Failed to connect to the database.")
        
    def save_file(self, **kwargs):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.file_collection_name]
                file_data = dict(kwargs)
                file_data["created_at"] = datetime.now()
                collection.insert_one(file_data)
                print("File data saved to database.")
            except Exception as e:
                print(f"Error saving file data to database: {e}")
            finally:
                self._close(client)
        else:
            print("Failed to connect to the database.")
        
    def save_payload(self, **kwargs)->bool:
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                payload = dict(kwargs)
                payload["status"] = "PENDING"
                payload["created_at"] = datetime.now()
                collection.insert_one(payload)
                print("Payload saved to database.")
                return True
            except Exception as e:
                print(f"Error saving payload to database: {e}")
                return False
            finally:
                self._close(client)
        else:
            print("Failed to connect to the database.")
            return False

    def get_file(self, file_path: Path):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.file_collection_name]
                file_info = collection.find_one({"file_name": file_path.name})
                return file_info
            except Exception as e:
                print(f"Error retrieving file info: {e}")
                return None
            finally:
                self._close(client)
        else:
            print("Failed to connect to the database.")
            return None

    def update_file(self, file_path: Path, **kwargs):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.file_collection_name]
                update_fields = {k: v for k, v in kwargs.items()}
                update_fields["updated_at"] = datetime.now()
                result = collection.update_one(
                    {"file_path": file_path.name},
                    {"$set": update_fields}
                )
                if result.matched_count:
                    print(f"File {file_path.name} updated with fields {list(kwargs.keys())}.")
                else:
                    print(f"No file info found with file_name {file_path.name}.")
            except Exception as e:
                print(f"Error updating file info: {e}")
            finally:
                self._close(client)
        else:
            print("Failed to connect to the database.")
        
    def get_payload(self, custom_id: str):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                payload = collection.find_one({"custom_id": custom_id})
                return payload
            except Exception as e:
                print(f"Error retrieving payload by custom_id: {e}")
                return None
            finally:
                self._close(client)
        else:
            print("Failed to connect to the database.")
            return None
        
    def get_payloads(self, status:str)->list:
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                payloads = list(collection.find({"status": status}))
                return payloads
            except Exception as e:
                print(f"Error retrieving payloads from database: {e}")
                return []
            finally:
                self._close(client)
        else:
            print("Failed to connect to the database.")
            return []
        
    def update_payload(self, custom_id: str, **kwargs):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                update_fields = {k: v for k, v in kwargs.items()}
                update_fields["updated_at"] = datetime.now()
                result = collection.update_one(
                    {"custom_id": custom_id},
                    {"$set": update_fields}
                )
                if result.matched_count:
                    print(f"Payload {custom_id} updated with fields {list(kwargs.keys())}.")
                else:
                    print(f"No payload found with custom_id {custom_id}.")
            except Exception as e:
                print(f"Error updating payload: {e}")
            finally:
                self._close(client)
        else:
            print("Failed to connect to the database.")