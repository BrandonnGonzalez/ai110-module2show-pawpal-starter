from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta


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
    frequency: str | None = None  # "daily", "weekly", or None for one-off tasks

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def walk_pet(self, pet: Pet) -> None:
        """Record that the pet has been walked."""
        pet.walked = True

    def feed_pet(self, pet: Pet) -> None:
        """Record that the pet has been fed."""
        pet.fed = True

    def play_with_pet(self, pet: Pet) -> None:
        """Record a play session with the pet."""
        pass


class Schedule:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.slots: dict[datetime, list[int]] = {}  # datetime -> [pet_ids booked at that time]
        self.tasks: list[Tasks] = []

    def is_slot_open(self, timeslot: datetime) -> bool:
        """Return True if no tasks are booked at this timeslot.

        Args:
            timeslot: The datetime to check.

        Returns:
            True if the timeslot has no existing bookings, False otherwise.
        """
        return timeslot not in self.slots

    def check_conflicts(self, timeslot: datetime, task: Tasks) -> str | None:
        """Check whether booking task at timeslot would cause a conflict.

        Compares the incoming task's pet_id against the pet IDs already booked
        at that timeslot. Distinguishes two conflict types:
          - Same-pet conflict: the same pet already has a task at this time.
          - Cross-pet conflict: a different pet is already booked, meaning the
            owner may need to be in two places at once.

        Args:
            timeslot: The datetime the new task would be booked at.
            task:     The Tasks instance being considered for booking.

        Returns:
            A warning string describing the conflict, or None if the slot is clear.
        """
        existing_pet_ids = self.slots.get(timeslot)
        if not existing_pet_ids:
            return None

        time_str = timeslot.strftime("%I:%M %p on %b %d")

        if task.pet_id in existing_pet_ids:
            return (
                f"⚠ Conflict: pet #{task.pet_id} already has a task at {time_str}. "
                "A pet cannot be in two places at once."
            )

        others = ", ".join(f"#{pid}" for pid in existing_pet_ids)
        return (
            f"⚠ Conflict: pet(s) {others} are already scheduled at {time_str}. "
            "The owner may not be able to attend to multiple pets simultaneously."
        )

    def book_slot(self, timeslot: datetime, task: Tasks) -> str | None:
        """Book a task into the schedule, always succeeding regardless of conflicts.

        Calls check_conflicts first to detect same-pet or cross-pet collisions.
        The task is booked either way — conflicts surface as a warning string so
        the caller can inform the user without crashing the program.

        Args:
            timeslot: The datetime to book the task at.
            task:     The Tasks instance to add to the schedule.

        Returns:
            A warning string if a conflict was detected, or None if the slot was clear.
        """
        warning = self.check_conflicts(timeslot, task)
        self.slots.setdefault(timeslot, []).append(task.pet_id)
        self.tasks.append(task)
        return warning

    def free_slot(self, timeslot: datetime) -> None:
        """Release a previously booked timeslot."""
        self.slots.pop(timeslot, None)
        self.tasks = [t for t in self.tasks if t.timeslot != timeslot]

    def complete_task(self, task_id: int) -> "Tasks | None":
        """Mark a task complete and auto-schedule the next occurrence for recurring tasks.

        Uses timedelta to calculate the next timeslot: +1 day for "daily" tasks
        and +7 days for "weekly" tasks. The new task is a copy of the original
        with a fresh id, the updated timeslot, and completed set to False.
        One-off tasks (frequency=None) are simply marked done with nothing created.

        Args:
            task_id: The id of the Tasks instance to complete.

        Returns:
            The newly created Tasks instance if the task recurs, or None for
            one-off tasks or if no task with the given id exists.
        """
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            return None

        task.mark_complete()

        if task.frequency is None or task.timeslot is None:
            return None

        _intervals = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        delta = _intervals.get(task.frequency)
        if delta is None:
            return None

        next_timeslot = task.timeslot + delta
        next_id = max(t.id for t in self.tasks) + 1
        next_task = Tasks(
            id=next_id,
            pet_id=task.pet_id,
            timeslot=next_timeslot,
            schedule_id=task.schedule_id,
            tasks=task.tasks.copy(),
            frequency=task.frequency,
        )
        self.book_slot(next_timeslot, next_task)
        return next_task

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        owner: "Owner | None" = None,
    ) -> list[Tasks]:
        """Return a filtered, chronologically sorted list of tasks.

        All three parameters are optional — calling with no arguments returns
        every task sorted by timeslot. Filters are applied in order: pet first,
        then completion status. Tasks with no timeslot sort to the end.

        Args:
            pet_name:  If given, only include tasks for the pet with this name.
                       Requires owner so the name can be resolved to a pet_id.
            completed: If True, return only completed tasks. If False, return only
                       pending tasks. If None (default), return both.
            owner:     The Owner instance used to resolve pet_name to a pet_id.
                       Ignored when pet_name is None.

        Returns:
            A list of Tasks sorted ascending by timeslot.
        """
        # Build a pet_name -> pet_id lookup when an owner is provided
        name_to_id: dict[str, int] = (
            {p.pet_name: p.id for p in owner.pets} if owner else {}
        )

        results = self.tasks

        if pet_name is not None and name_to_id:
            target_id = name_to_id.get(pet_name)
            results = [t for t in results if t.pet_id == target_id]

        if completed is not None:
            results = [t for t in results if t.completed == completed]

        return sorted(results, key=lambda t: t.timeslot if t.timeslot else datetime.max)


class Owner:
    def __init__(self, id: int, schedule: Schedule) -> None:
        self.id: int = id
        self.pets: list[Pet] = []
        self.schedule: Schedule = schedule

    def add_pet(self, pet: Pet) -> bool:
        """Add a pet to the owner's list. Returns False if a pet with the same name already exists."""
        if any(p.pet_name == pet.pet_name for p in self.pets):
            return False
        self.pets.append(pet)
        return True

    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet and clean up all of their associated scheduled tasks.

        Filters the pet from self.pets, removes their tasks from the schedule's
        task list, and clears any now-empty timeslot entries from the slots dict
        to avoid stale slot bookings.

        Args:
            pet_id: The id of the Pet to remove.
        """
        self.pets = [p for p in self.pets if p.id != pet_id]
        self.schedule.tasks = [t for t in self.schedule.tasks if t.pet_id != pet_id]
        for ts in [ts for ts, booked in list(self.schedule.slots.items()) if booked]:
            if not any(t.timeslot == ts for t in self.schedule.tasks):
                self.schedule.slots.pop(ts, None)

    def reset_daily_flags(self) -> None:
        """Reset walked/fed flags on all pets for a new day."""
        for pet in self.pets:
            pet.walked = False
            pet.fed = False
