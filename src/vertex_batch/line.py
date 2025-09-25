from .db import Db

class Line:

    def __init__(
        self,
        db: Db,
        custom_id: str,
        user_prompt: str,
        sys_prompt: str,
        top_p: float = 0.9,
        temperature: float = 0.1,
        max_output_tokens: int = 1024,
        **kwargs
    ):
        self.custom_id = custom_id
        self.user_prompt = user_prompt
        self.sys_prompt = sys_prompt
        self.top_p = top_p
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.db = db
        self.extra_fields = kwargs  # Store extra fields

    def save(self) -> bool:
        payload = {
            "custom_id": self.custom_id,
            "user_prompt": self.user_prompt,
            "sys_prompt": self.sys_prompt,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "status": "pending",
        }
        payload.update(self.extra_fields)  # Merge extra fields into payload
        return self.db.save_payload(**payload)