import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Tasks


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
