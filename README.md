# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors


### Testing PawPal+
- Baseline (2 tests)
Basic Tasks behavior — mark_complete() flips the completed flag, and appending a task increments a pet's task list.

book_slot — conflict detection (4 tests)
Verifies that every booking always succeeds (task lands in schedule.tasks and schedule.slots) regardless of conflicts, and that the return value is None for a clean slot, a non-empty warning string for a same-pet collision, and a different warning string for a cross-pet collision.

complete_task — recurrence logic (7 tests)
Confirms daily recurrence advances exactly 1 day, weekly advances exactly 7 days, the new task has completed=False and the same frequency, and its id is max + 1. Also guards the failure paths: frequency=None, unknown frequency ("monthly"), missing task_id, and timeslot=None all return None without raising.

filter_tasks — sorting and filtering (8 tests)
Covers every filter in isolation (completed=False, completed=True, pet_name) and all three combined. Edge cases include a pet with no tasks returning [], a timeslot=None task sorting last via the datetime.max sentinel, and passing pet_name without an owner silently skipping the filter (a subtle no-op in the implementation).

Confidence Level: 5 Stars ☆

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
