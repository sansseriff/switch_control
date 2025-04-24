from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import (
    BaseModel as PydanticBaseModel,
)  # Import Pydantic's BaseModel for the base class


# Define a base Pydantic model for the labels (used for request/response structure)
class ButtonLabelsBase(PydanticBaseModel):
    label_0: str = "Ch 1"
    label_1: str = "Ch 2"
    label_2: str = "Ch 3"
    label_3: str = "Ch 4"
    label_4: str = "Ch 5"
    label_5: str = "Ch 6"
    label_6: str = "Ch 7"
    label_7: str = "Ch 8"


# Define the SQLModel for the database, inheriting from the base and adding the ID
class ButtonLabels(SQLModel, ButtonLabelsBase, table=True):
    id: Optional[int] = Field(
        default=1, primary_key=True
    )  # Use a fixed ID for the single row


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # Ensure the default label row exists
    with Session(engine) as session:
        # Use the DB model (ButtonLabels) here
        statement = select(ButtonLabels).where(ButtonLabels.id == 1)
        results = session.exec(statement)
        db_labels = results.first()
        if not db_labels:
            # Use the DB model (ButtonLabels) here
            default_labels = ButtonLabels(
                id=1
            )  # Use default values defined in the model
            session.add(default_labels)
            session.commit()
            print("Default button labels created.")
