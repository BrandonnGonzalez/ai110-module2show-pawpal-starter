import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from pawpal_system import Owner, Pet, Schedule, Tasks


def test_mark_complete_changes_task_status():
    """Calling mark_complete() should flip completed from False to True."""
    task = Tasks(id=1, pet_id=1, tasks=["Walk dog"])

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a pet's task list should increase the count by 1."""
    pet = Pet(id=1, pet_name="Buddy", breed="Golden Retriever")
    task = Tasks(id=1, pet_id=pet.id, tasks=["Morning walk"])

    initial_count = len(pet.tasks)
    pet.tasks.append(task)

    assert len(pet.tasks) == initial_count + 1


# ---------------------------------------------------------------------------
# book_slot tests
# ---------------------------------------------------------------------------

def test_book_slot_clean_returns_none_and_stores_task():
    """Booking an empty slot returns None and registers the task."""
    schedule = Schedule(id=1)
    timeslot = datetime(2026, 3, 30, 8, 0)
    task = Tasks(id=1, pet_id=1, timeslot=timeslot)

    warning = schedule.book_slot(timeslot, task)

    assert warning is None
    assert task in schedule.tasks
    assert 1 in schedule.slots[timeslot]


def test_book_slot_same_pet_returns_warning_and_still_books():
    """Same pet booked twice at the same time triggers a warning but both entries are stored."""
    schedule = Schedule(id=1)
    timeslot = datetime(2026, 3, 30, 9, 0)
    task1 = Tasks(id=1, pet_id=1, timeslot=timeslot)
    task2 = Tasks(id=2, pet_id=1, timeslot=timeslot)

    schedule.book_slot(timeslot, task1)
    warning = schedule.book_slot(timeslot, task2)

    assert warning is not None and len(warning) > 0
    assert task2 in schedule.tasks
    assert schedule.slots[timeslot].count(1) == 2  # pet #1 appears twice


def test_book_slot_cross_pet_returns_warning_and_still_books():
    """A different pet at an occupied slot triggers a warning but the new task is still booked."""
    schedule = Schedule(id=1)
    timeslot = datetime(2026, 3, 30, 10, 0)
    task1 = Tasks(id=1, pet_id=1, timeslot=timeslot)
    task2 = Tasks(id=2, pet_id=2, timeslot=timeslot)

    schedule.book_slot(timeslot, task1)
    warning = schedule.book_slot(timeslot, task2)

    assert warning is not None and len(warning) > 0
    assert task2 in schedule.tasks
    assert 2 in schedule.slots[timeslot]


def test_book_slot_multiple_pets_all_succeed():
    """Three different pets at the same slot all get booked; all pet IDs appear in slots."""
    schedule = Schedule(id=1)
    timeslot = datetime(2026, 3, 30, 11, 0)
    tasks = [Tasks(id=i, pet_id=i, timeslot=timeslot) for i in range(1, 4)]

    for t in tasks:
        schedule.book_slot(timeslot, t)

    assert len(schedule.tasks) == 3
    assert schedule.slots[timeslot] == [1, 2, 3]


# ---------------------------------------------------------------------------
# complete_task tests
# ---------------------------------------------------------------------------

def test_complete_task_daily_produces_next_day():
    """A daily task completed at 08:00 creates a new task at 08:00 the next day."""
    schedule = Schedule(id=1)
    base_dt = datetime(2026, 3, 30, 8, 0)
    task = Tasks(id=1, pet_id=1, timeslot=base_dt, frequency="daily")
    schedule.book_slot(base_dt, task)

    next_task = schedule.complete_task(1)

    assert next_task is not None
    assert next_task.timeslot == datetime(2026, 3, 31, 8, 0)
    assert next_task.completed is False
    assert next_task.frequency == "daily"
    assert next_task in schedule.tasks


def test_complete_task_weekly_produces_seven_days_later():
    """A weekly task creates a new task exactly 7 days out at the same time."""
    schedule = Schedule(id=1)
    base_dt = datetime(2026, 3, 30, 8, 0)
    task = Tasks(id=1, pet_id=1, timeslot=base_dt, frequency="weekly")
    schedule.book_slot(base_dt, task)

    next_task = schedule.complete_task(1)

    assert next_task is not None
    assert next_task.timeslot == datetime(2026, 4, 6, 8, 0)


def test_complete_task_one_off_returns_none_and_creates_nothing():
    """Completing a one-off task (frequency=None) returns None and adds no new task."""
    schedule = Schedule(id=1)
    base_dt = datetime(2026, 3, 30, 8, 0)
    task = Tasks(id=1, pet_id=1, timeslot=base_dt, frequency=None)
    schedule.book_slot(base_dt, task)

    result = schedule.complete_task(1)

    assert result is None
    assert len(schedule.tasks) == 1  # no new task added


def test_complete_task_unknown_frequency_returns_none():
    """An unsupported frequency string (e.g. 'monthly') returns None and creates no task."""
    schedule = Schedule(id=1)
    base_dt = datetime(2026, 3, 30, 8, 0)
    task = Tasks(id=1, pet_id=1, timeslot=base_dt, frequency="monthly")
    schedule.book_slot(base_dt, task)

    result = schedule.complete_task(1)

    assert result is None
    assert len(schedule.tasks) == 1


def test_complete_task_missing_id_returns_none():
    """Calling complete_task with an id that doesn't exist returns None without raising."""
    schedule = Schedule(id=1)

    result = schedule.complete_task(99)

    assert result is None


def test_complete_task_no_timeslot_returns_none():
    """A recurring task with timeslot=None cannot compute a next slot; returns None."""
    schedule = Schedule(id=1)
    task = Tasks(id=1, pet_id=1, timeslot=None, frequency="daily")
    schedule.tasks.append(task)  # add directly — book_slot requires a timeslot key

    result = schedule.complete_task(1)

    assert result is None


def test_complete_task_new_id_is_max_plus_one():
    """The next task's id is always max(existing ids) + 1."""
    schedule = Schedule(id=1)
    base_dt = datetime(2026, 3, 30, 8, 0)
    task = Tasks(id=5, pet_id=1, timeslot=base_dt, frequency="daily")
    schedule.book_slot(base_dt, task)

    next_task = schedule.complete_task(5)

    assert next_task.id == 6


# ---------------------------------------------------------------------------
# filter_tasks tests
# ---------------------------------------------------------------------------

def test_filter_tasks_no_filters_returns_all_sorted():
    """Tasks added out of chronological order come back sorted ascending by timeslot."""
    schedule = Schedule(id=1)
    late = Tasks(id=1, pet_id=1, timeslot=datetime(2026, 3, 30, 10, 0))
    early = Tasks(id=2, pet_id=1, timeslot=datetime(2026, 3, 30, 8, 0))
    schedule.book_slot(late.timeslot, late)
    schedule.book_slot(early.timeslot, early)

    results = schedule.filter_tasks()

    assert results[0].timeslot < results[1].timeslot


def test_filter_tasks_completed_false_excludes_done_tasks():
    """completed=False returns only pending tasks."""
    schedule = Schedule(id=1)
    pending = Tasks(id=1, pet_id=1, timeslot=datetime(2026, 3, 30, 8, 0))
    done = Tasks(id=2, pet_id=1, timeslot=datetime(2026, 3, 30, 9, 0), completed=True)
    schedule.book_slot(pending.timeslot, pending)
    schedule.book_slot(done.timeslot, done)

    results = schedule.filter_tasks(completed=False)

    assert pending in results
    assert done not in results


def test_filter_tasks_completed_true_excludes_pending_tasks():
    """completed=True returns only completed tasks."""
    schedule = Schedule(id=1)
    pending = Tasks(id=1, pet_id=1, timeslot=datetime(2026, 3, 30, 8, 0))
    done = Tasks(id=2, pet_id=1, timeslot=datetime(2026, 3, 30, 9, 0), completed=True)
    schedule.book_slot(pending.timeslot, pending)
    schedule.book_slot(done.timeslot, done)

    results = schedule.filter_tasks(completed=True)

    assert done in results
    assert pending not in results


def test_filter_tasks_pet_name_excludes_other_pets():
    """pet_name filter returns only tasks belonging to that pet."""
    schedule = Schedule(id=1)
    buddy = Pet(id=1, pet_name="Buddy", breed="Labrador")
    max_pet = Pet(id=2, pet_name="Max", breed="Poodle")
    owner = Owner(id=1, schedule=schedule)
    owner.add_pet(buddy)
    owner.add_pet(max_pet)

    buddy_task = Tasks(id=1, pet_id=1, timeslot=datetime(2026, 3, 30, 8, 0))
    max_task = Tasks(id=2, pet_id=2, timeslot=datetime(2026, 3, 30, 9, 0))
    schedule.book_slot(buddy_task.timeslot, buddy_task)
    schedule.book_slot(max_task.timeslot, max_task)

    results = schedule.filter_tasks(pet_name="Buddy", owner=owner)

    assert buddy_task in results
    assert max_task not in results


def test_filter_tasks_all_three_combined():
    """pet_name + completed=False + owner returns only pending tasks for that pet."""
    schedule = Schedule(id=1)
    buddy = Pet(id=1, pet_name="Buddy", breed="Labrador")
    max_pet = Pet(id=2, pet_name="Max", breed="Poodle")
    owner = Owner(id=1, schedule=schedule)
    owner.add_pet(buddy)
    owner.add_pet(max_pet)

    buddy_pending = Tasks(id=1, pet_id=1, timeslot=datetime(2026, 3, 30, 8, 0))
    buddy_done = Tasks(id=2, pet_id=1, timeslot=datetime(2026, 3, 30, 9, 0), completed=True)
    max_pending = Tasks(id=3, pet_id=2, timeslot=datetime(2026, 3, 30, 10, 0))
    for t in [buddy_pending, buddy_done, max_pending]:
        schedule.book_slot(t.timeslot, t)

    results = schedule.filter_tasks(pet_name="Buddy", completed=False, owner=owner)

    assert results == [buddy_pending]


def test_filter_tasks_pet_with_no_tasks_returns_empty():
    """A pet that exists but has no scheduled tasks produces an empty list."""
    schedule = Schedule(id=1)
    buddy = Pet(id=1, pet_name="Buddy", breed="Labrador")
    owner = Owner(id=1, schedule=schedule)
    owner.add_pet(buddy)

    results = schedule.filter_tasks(pet_name="Buddy", owner=owner)

    assert results == []


def test_filter_tasks_none_timeslot_sorts_last():
    """A task with timeslot=None sorts to the end of the result list."""
    schedule = Schedule(id=1)
    timed = Tasks(id=1, pet_id=1, timeslot=datetime(2026, 3, 30, 8, 0))
    no_time = Tasks(id=2, pet_id=1, timeslot=None)
    schedule.book_slot(timed.timeslot, timed)
    schedule.tasks.append(no_time)  # add directly — no timeslot key for book_slot

    results = schedule.filter_tasks()

    assert results[-1] is no_time


def test_filter_tasks_pet_name_without_owner_skips_filter():
    """Passing pet_name without owner silently skips the filter and returns all tasks."""
    schedule = Schedule(id=1)
    t1 = Tasks(id=1, pet_id=1, timeslot=datetime(2026, 3, 30, 8, 0))
    t2 = Tasks(id=2, pet_id=2, timeslot=datetime(2026, 3, 30, 9, 0))
    schedule.book_slot(t1.timeslot, t1)
    schedule.book_slot(t2.timeslot, t2)

    # No owner supplied — name_to_id is {} so the if-guard is falsy and filter is skipped
    results = schedule.filter_tasks(pet_name="Buddy")

    assert t1 in results
    assert t2 in results
