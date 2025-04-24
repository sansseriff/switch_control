from typing import Annotated
from typing import Optional
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel
from verification import Verification


class Channel(BaseModel):
    number: int
    verification: Verification


class ToggleRequest(BaseModel):
    number: int
    verification: Verification


class SwitchState(BaseModel):
    pos: bool
    color: bool


class Tree(BaseModel):
    R1: SwitchState
    R2: SwitchState
    R3: SwitchState
    R4: SwitchState
    R5: SwitchState
    R6: SwitchState
    R7: SwitchState
    activated_channel: int


class T(BaseModel):
    tree_state: Tree
    activated_channel: int


class ButtonLabelsBase(BaseModel):
    label_0: str = "Ch 1"
    label_1: str = "Ch 2"
    label_2: str = "Ch 3"
    label_3: str = "Ch 4"
    label_4: str = "Ch 5"
    label_5: str = "Ch 6"
    label_6: str = "Ch 7"
    label_7: str = "Ch 8"
