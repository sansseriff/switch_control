from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel
from models import ButtonLabelsBase, Tree, SettingsBase, SwitchState, PulseGenInfo
import json
from sqlalchemy import text

# Define a base Pydantic model for the labels (used for request/response structure)


# Define the SQLModel for the database, inheriting from the base and adding the ID
class ButtonLabels(SQLModel, ButtonLabelsBase, table=True):
    id: Optional[int] = Field(default=1, primary_key=True)


class InitializationResponse(BaseModel):
    tree_state: Tree
    button_labels: ButtonLabelsBase
    settings: SettingsBase
    pulse_generator: PulseGenInfo


class InitResponse(BaseModel):
    tree_state: Tree
    button_labels: ButtonLabels
    settings: SettingsBase
    pulse_generator: PulseGenInfo


class InitResponsePublic(BaseModel):
    tree_state: Tree
    button_labels: ButtonLabelsBase
    settings: SettingsBase
    pulse_generator: PulseGenInfo


class Settings(SQLModel, SettingsBase, table=True):
    id: Optional[int] = Field(default=1, primary_key=True)


class TreeState(SQLModel, table=True):
    """Persisted tree state stored as JSON for simplicity."""
    id: Optional[int] = Field(default=1, primary_key=True)
    tree_json: str = Field(default_factory=lambda: json.dumps(
        Tree(
            R1=SwitchState(pos=False, color=False),
            R2=SwitchState(pos=False, color=False),
            R3=SwitchState(pos=False, color=False),
            R4=SwitchState(pos=False, color=False),
            R5=SwitchState(pos=False, color=False),
            R6=SwitchState(pos=False, color=False),
            R7=SwitchState(pos=False, color=False),
            activated_channel=0,
        ).model_dump()
    ))


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # Lightweight migrations for SQLite
    with engine.connect() as conn:
        # Ensure title_label exists on settings table
        res = conn.exec_driver_sql("PRAGMA table_info('settings')").fetchall()
        cols = {row[1] for row in res} if res else set()
        if "title_label" not in cols:
            conn.exec_driver_sql(
                "ALTER TABLE settings ADD COLUMN title_label TEXT DEFAULT 'Title Here'"
            )
            print("Added title_label column to settings table.")
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

        # Ensure the default settings row exists
        statement = select(Settings).where(Settings.id == 1)
        results = session.exec(statement)
        db_settings = results.first()
        if not db_settings:
            default_settings = Settings(id=1)
            session.add(default_settings)
            session.commit()
            print("Default settings created.")

        # Ensure the default tree state row exists
        statement = select(TreeState).where(TreeState.id == 1)
        results = session.exec(statement)
        db_tree = results.first()
        if not db_tree:
            default_tree = Tree(
                R1=SwitchState(pos=False, color=False),
                R2=SwitchState(pos=False, color=False),
                R3=SwitchState(pos=False, color=False),
                R4=SwitchState(pos=False, color=False),
                R5=SwitchState(pos=False, color=False),
                R6=SwitchState(pos=False, color=False),
                R7=SwitchState(pos=False, color=False),
                activated_channel=0,
            )
            db_tree = TreeState(id=1, tree_json=json.dumps(default_tree.model_dump()))
            session.add(db_tree)
            session.commit()
            print("Default tree state created.")
