from datetime import datetime
from pawpal_system import Owner, Pet, Schedule, Tasks

# --- Setup ---
schedule = Schedule(id=1)
owner = Owner(id=1, schedule=schedule)

# --- Create Pets ---
buddy = Pet(id=1, pet_name="Buddy", breed="Golden Retriever",
            pet_tricks=["sit", "shake", "fetch"],
            food=["kibble", "carrots"])

luna = Pet(id=2, pet_name="Luna", breed="Siberian Husky",
           pet_tricks=["roll over", "high five"],
           food=["salmon kibble", "blueberries"])

# Add pets to owner
owner.pets.extend([buddy, luna])

# --- Create Tasks ---
today = datetime.today().date()

task1 = Tasks(
    id=1,
    pet_id=buddy.id,
    timeslot=datetime(today.year, today.month, today.day, 8, 0),
    schedule_id=schedule.id,
    tasks=["Walk Buddy for 30 minutes", "Morning feeding"],
    frequency="daily",
)

task2 = Tasks(
    id=2,
    pet_id=luna.id,
    timeslot=datetime(today.year, today.month, today.day, 12, 0),
    schedule_id=schedule.id,
    tasks=["Feed Luna", "Practice tricks"],
    frequency="weekly",
)

task3 = Tasks(
    id=3,
    pet_id=buddy.id,
    timeslot=datetime(today.year, today.month, today.day, 17, 30),
    schedule_id=schedule.id,
    tasks=["Walk Buddy", "Evening feeding", "Play fetch"],
    frequency="daily",
)

task4 = Tasks(
    id=4,
    pet_id=luna.id,
    timeslot=datetime(today.year, today.month, today.day, 19, 0),
    schedule_id=schedule.id,
    tasks=["Walk Luna", "Grooming session"],
    frequency=None,  # one-off task
)

# Register tasks via book_slot so slots dict is populated correctly
all_tasks = [task4, task2, task3, task1]
pet_lookup = {pet.id: pet for pet in owner.pets}
for task in all_tasks:
    schedule.book_slot(task.timeslot, task)
    pet_lookup[task.pet_id].tasks.append(task)

def print_schedule(label: str, tasks: list) -> None:
    print("\n" + "=" * 44)
    print(f"  {label}")
    print("=" * 44)
    if not tasks:
        print("  (no tasks)")
        return
    for task in tasks:
        pet = pet_lookup[task.pet_id]
        time_str = task.timeslot.strftime("%a %b %d  %I:%M %p")
        status = "✓" if task.completed else "○"
        freq = f"  [{task.frequency}]" if task.frequency else "  [one-off]"
        print(f"\n  {status} {time_str}{freq}")
        print(f"     {pet.pet_name} ({pet.breed})")
        for item in task.tasks:
            print(f"       - {item}")


# --- Baseline: today's schedule before any completions ---
print_schedule("TODAY'S SCHEDULE (before completions)", schedule.filter_tasks())

# --- Complete task1 (daily) — should spawn tomorrow's walk ---
next_task = schedule.complete_task(task1.id)
print("\n>>> complete_task(task1)  [daily: Walk Buddy / Morning feeding]")
if next_task:
    print(f"    → Next occurrence auto-booked: {next_task.timeslot.strftime('%a %b %d  %I:%M %p')}")

# --- Complete task2 (weekly) — should spawn same time next week ---
next_task = schedule.complete_task(task2.id)
print("\n>>> complete_task(task2)  [weekly: Feed Luna / Practice tricks]")
if next_task:
    print(f"    → Next occurrence auto-booked: {next_task.timeslot.strftime('%a %b %d  %I:%M %p')}")

# --- Complete task4 (one-off) — should NOT spawn anything ---
next_task = schedule.complete_task(task4.id)
print("\n>>> complete_task(task4)  [one-off: Walk Luna / Grooming]")
print(f"    → Next occurrence: {next_task}")  # expected: None

# --- Full schedule after completions (shows new recurring entries) ---
print_schedule("FULL SCHEDULE (after completions)", schedule.filter_tasks())

# --- Pending tasks only ---
print_schedule("PENDING TASKS ONLY", schedule.filter_tasks(completed=False))

# --- Buddy's full task history ---
print_schedule("BUDDY'S TASKS (all)", schedule.filter_tasks(pet_name="Buddy", owner=owner))

print(f"\n  Total tasks in schedule: {len(schedule.tasks)}")
print("=" * 44)

# -------------------------------------------------------
# CONFLICT DETECTION TESTS
# -------------------------------------------------------
print("\n" + "=" * 44)
print("  CONFLICT DETECTION TESTS")
print("=" * 44)

# Conflict A: same pet (Buddy) booked again at 08:00 AM
conflict_a = Tasks(
    id=10,
    pet_id=buddy.id,
    timeslot=datetime(today.year, today.month, today.day, 8, 0),
    schedule_id=schedule.id,
    tasks=["Buddy vet checkup"],
)
print("\n>>> Booking Buddy at 08:00 AM (Buddy already has a task there):")
warning = schedule.book_slot(conflict_a.timeslot, conflict_a)
print(f"    {warning}")

# Conflict B: different pet (Luna) booked at 08:00 AM (Buddy is already there)
conflict_b = Tasks(
    id=11,
    pet_id=luna.id,
    timeslot=datetime(today.year, today.month, today.day, 8, 0),
    schedule_id=schedule.id,
    tasks=["Luna morning walk"],
)
print("\n>>> Booking Luna at 08:00 AM (Buddy already has a task there):")
warning = schedule.book_slot(conflict_b.timeslot, conflict_b)
print(f"    {warning}")

# Clean booking: a free timeslot — no conflict expected
conflict_c = Tasks(
    id=12,
    pet_id=luna.id,
    timeslot=datetime(today.year, today.month, today.day, 10, 0),
    schedule_id=schedule.id,
    tasks=["Luna midmorning snack"],
)
print("\n>>> Booking Luna at 10:00 AM (slot is free):")
warning = schedule.book_slot(conflict_c.timeslot, conflict_c)
print(f"    {warning if warning else 'No conflict — booked successfully.'}")
