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
    tasks=["Walk Buddy for 30 minutes", "Morning feeding"]
)

task2 = Tasks(
    id=2,
    pet_id=luna.id,
    timeslot=datetime(today.year, today.month, today.day, 12, 0),
    schedule_id=schedule.id,
    tasks=["Feed Luna", "Practice tricks"]
)

task3 = Tasks(
    id=3,
    pet_id=buddy.id,
    timeslot=datetime(today.year, today.month, today.day, 17, 30),
    schedule_id=schedule.id,
    tasks=["Walk Buddy", "Evening feeding", "Play fetch"]
)

task4 = Tasks(
    id=4,
    pet_id=luna.id,
    timeslot=datetime(today.year, today.month, today.day, 19, 0),
    schedule_id=schedule.id,
    tasks=["Walk Luna", "Grooming session"]
)

# Register tasks
all_tasks = [task1, task2, task3, task4]
schedule.tasks.extend(all_tasks)

pet_lookup = {pet.id: pet for pet in owner.pets}
for task in all_tasks:
    pet_lookup[task.pet_id].tasks.append(task)

# --- Print Today's Schedule ---
print("=" * 40)
print("        PawPal - Today's Schedule")
print(f"        {today.strftime('%A, %B %d, %Y')}")
print("=" * 40)

sorted_tasks = sorted(schedule.tasks, key=lambda t: t.timeslot)

for task in sorted_tasks:
    pet = pet_lookup[task.pet_id]
    time_str = task.timeslot.strftime("%I:%M %p")
    print(f"\n[{time_str}] {pet.pet_name} ({pet.breed})")
    for item in task.tasks:
        print(f"  - {item}")

print("\n" + "=" * 40)
print(f"Total pets: {len(owner.pets)}")
print(f"Total tasks scheduled: {len(schedule.tasks)}")
print("=" * 40)
