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


@dataclass
class Tasks:
    id: int
    pet_id: int
    tasks: list[str] = field(default_factory=list)

    def walk_pet(self) -> None:
        pass

    def feed_pet(self) -> None:
        pass

    def play_with_pet(self) -> None:
        pass


class Schedule:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.timeslots: list[datetime] = []
        self.is_booked: list[bool] = []

    def is_slot_open(self, timeslot: datetime) -> bool:
        pass

    def book_slot(self, timeslot: datetime) -> None:
        pass

    def free_slot(self, timeslot: datetime) -> None:
        pass


class Owner:
    def __init__(self, id: int, schedule: Schedule) -> None:
        self.id: int = id
        self.pets: list[Pet] = []
        self.schedule: Schedule = schedule
