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


class SettingsBase(BaseModel):
    cryo_mode: bool = False
    cryo_voltage: float = 2.5
    regular_voltage: float = 5.0
    tree_memory_mode: bool = False
    # UI configuration
    title_label: str = "Title Here"
    # Pulse generator persistence/config
    pulse_generator_kind: str = "dev"  # one of: dev | keysight | client
    pulse_generator_ip: Optional[str] = None


# Pulse generator API models
class PulseGenRequest(BaseModel):
    kind: str
    ip: Optional[str] = None


class PulseGenInfo(BaseModel):
    requested_kind: Optional[str] = None
    requested_ip: Optional[str] = None
    active_kind: str
    created: bool = True
    message: Optional[str] = None
