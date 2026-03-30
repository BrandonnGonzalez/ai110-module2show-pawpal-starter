from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Pet:
    id: int
    pet_name: str
    breed: str
    pet_tricks: list[str] = field(default_factory=list)
    food: list[str] = field(default_factory=list)
    walked: bool = False
    fed: bool = False
    tasks: list[Tasks] = field(default_factory=list)


@dataclass
class Tasks:
    id: int
    pet_id: int
    timeslot: datetime | None = None
    schedule_id: int | None = None
    tasks: list[str] = field(default_factory=list)
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def walk_pet(self, pet: Pet) -> None:
        """Record that the pet has been walked."""
        pass

    def feed_pet(self, pet: Pet) -> None:
        """Record that the pet has been fed."""
        pass

    def play_with_pet(self, pet: Pet) -> None:
        """Record a play session with the pet."""
        pass


class Schedule:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.slots: dict[datetime, bool] = {}  # datetime -> is_booked
        self.tasks: list[Tasks] = []

    def is_slot_open(self, timeslot: datetime) -> bool:
        """Return True if the given timeslot is not yet booked."""
        pass

    def book_slot(self, timeslot: datetime, task: Tasks) -> None:
        """Reserve a timeslot and associate it with a task."""
        pass

    def free_slot(self, timeslot: datetime) -> None:
        """Release a previously booked timeslot."""
        pass


class Owner:
    def __init__(self, id: int, schedule: Schedule) -> None:
        self.id: int = id
        self.pets: list[Pet] = []
        self.schedule: Schedule = schedule

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list of pets."""
        pass

    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet from the owner's list by its ID."""
        pass
