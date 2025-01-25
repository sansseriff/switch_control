from pydantic import BaseModel


class Verification(BaseModel):
    verified: bool
    timestamp: int
    userConfirmed: bool
