from pydantic import BaseModel


class DuckDBSettings(BaseModel):
    database_url: str
