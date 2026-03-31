# PawPal+ (Module 2 Project)

#Demo
<img width="1463" height="754" alt="Screenshot 2026-03-30 at 9 19 57 PM" src="https://github.com/user-attachments/assets/5afb1b5f-9ead-431a-9d01-9adbd3f19782" />


You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Features

### Scheduling algorithms
- **Chronological sorting** — `Schedule.filter_tasks()` sorts all tasks ascending by timeslot using a `datetime.max` sentinel so tasks without a timeslot always sort to the end, never crash the sort.
- **Conflict detection** — `Schedule.check_conflicts()` distinguishes two cases before every booking: a *same-pet conflict* (the same pet already has a task at that exact timeslot) and a *cross-pet conflict* (a different pet is booked, meaning the owner may need to be in two places at once). Both surface as warning strings; neither blocks the booking.
- **Daily recurrence** — completing a task with `frequency="daily"` auto-schedules a new copy `+1 day` at the same time via `timedelta(days=1)`. The new task gets `completed=False`, inherits the original's fields, and receives `id = max(existing ids) + 1`.
- **Weekly recurrence** — same as daily but advances `+7 days` with `timedelta(weeks=1)`.
- **Feeding-interval guard** — the UI enforces a minimum 4-hour gap between feeding tasks for the same pet. Any new feeding within that window surfaces a `st.warning` before the task is booked.
- **Task filtering** — `filter_tasks()` supports three independent, composable filters: by pet name (resolved to a `pet_id` via the Owner), by completion status (`True`/`False`/`None`), or any combination of both. Passing `pet_name` without an `owner` silently skips the name filter rather than raising.

### Data management
- **Duplicate pet guard** — `Owner.add_pet()` rejects a second pet with the same name, returning `False` so the UI can show a targeted warning without crashing.
- **Pet removal with slot cleanup** — `Owner.remove_pet()` purges the pet's tasks from both `schedule.tasks` and `schedule.slots`, removing any now-empty slot entries to prevent stale bookings.
- **Daily flag reset** — `Owner.reset_daily_flags()` resets `walked` and `fed` to `False` on every pet, ready for a new day.

### UI (Streamlit)
- Inline conflict warnings appear next to any affected row when viewing the schedule.
- A summary banner (`st.success`) shows total tasks, completed count, and pending count after every schedule generation.
- The schedule view uses `st.dataframe` (sortable, full-width) grouped by date.
- Completing a recurring task shows a confirmation and an `st.info` message with the next scheduled occurrence.

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
