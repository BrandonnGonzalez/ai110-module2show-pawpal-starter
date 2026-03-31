import streamlit as st
from collections import defaultdict
from datetime import datetime
from pawpal_system import Owner, Pet, Schedule, Tasks

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state vault: create Owner + Schedule once ---
if "schedule" not in st.session_state:
    st.session_state.schedule = Schedule(id=1)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(id=1, schedule=st.session_state.schedule)

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

owner: Owner = st.session_state.owner
schedule: Schedule = st.session_state.schedule

# --- Add a Pet ---
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
breed = st.selectbox("Species / Breed", ["dog", "cat", "other"])

if st.button("Add Pet"):
    pet = Pet(
        id=st.session_state.next_pet_id,
        pet_name=pet_name,
        breed=breed,
    )
    added = owner.add_pet(pet)                  # duplicate guard — returns bool
    if added:
        st.session_state.next_pet_id += 1
        st.success(f"Added {pet_name} to {owner.id}'s pet list.")
    else:
        st.warning(f"A pet named '{pet_name}' already exists.")

if owner.pets:
    st.write("Current pets:")
    st.table([{"id": p.id, "name": p.pet_name, "breed": p.breed} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Schedule a Task ---
st.subheader("Schedule a Task")

MIN_FEED_HOURS = 4  # minimum hours between feeding sessions

if not owner.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    pet_options = {p.pet_name: p for p in owner.pets}
    selected_pet_name = st.selectbox("Select pet", list(pet_options.keys()))
    selected_pet = pet_options[selected_pet_name]

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_date = st.date_input("Date")
    with col3:
        task_time = st.time_input("Time")

    if st.button("Add Task"):
        timeslot = datetime.combine(task_date, task_time)

        # Feeding interval check — warn if a feed task is too close to an existing one
        is_feed = "feed" in task_title.lower()
        if is_feed:
            feed_times = [
                t.timeslot for t in selected_pet.tasks
                if t.timeslot and "feed" in " ".join(t.tasks).lower()
            ]
            too_soon = any(
                abs((timeslot - ft).total_seconds()) < MIN_FEED_HOURS * 3600
                for ft in feed_times
            )
            if too_soon:
                st.warning(
                    f"'{selected_pet_name}' already has a feeding within {MIN_FEED_HOURS} hours "
                    f"of {timeslot.strftime('%H:%M')}. Consider adjusting the time."
                )

        task = Tasks(
            id=st.session_state.next_task_id,
            pet_id=selected_pet.id,
            timeslot=timeslot,
            tasks=[task_title],
        )
        conflict = schedule.book_slot(timeslot, task)   # always books; returns warning or None
        selected_pet.tasks.append(task)
        st.session_state.next_task_id += 1
        st.success(f"Scheduled '{task_title}' for {selected_pet_name} at {timeslot.strftime('%b %d %H:%M')}.")
        if conflict:
            st.warning(conflict)

st.divider()

# --- Mark Task Complete ---
st.subheader("Mark Task Complete")

pending = [t for t in schedule.tasks if not t.completed]
if not pending:
    st.info("No pending tasks to complete.")
else:
    pet_name_map = {p.id: p.pet_name for p in owner.pets}

    def task_label(t):
        pet = pet_name_map.get(t.pet_id, f"Pet #{t.pet_id}")
        time_str = t.timeslot.strftime("%b %d %H:%M") if t.timeslot else "no time"
        task_str = ", ".join(t.tasks)
        freq = f" [{t.frequency}]" if t.frequency else ""
        return f"[{t.id}] {pet} — {task_str} @ {time_str}{freq}"

    task_options = {task_label(t): t for t in pending}
    selected_label = st.selectbox("Select a task to complete", list(task_options.keys()))
    selected_task = task_options[selected_label]

    if st.button("Mark Complete"):
        next_task = schedule.complete_task(selected_task.id)
        st.success(f"Task '{', '.join(selected_task.tasks)}' marked as complete!")
        if next_task:
            next_time = next_task.timeslot.strftime("%b %d %H:%M") if next_task.timeslot else "unknown"
            st.info(f"Recurring task auto-scheduled: next occurrence at {next_time}.")

st.divider()

# --- View Schedule ---
st.subheader("Current Schedule")

# Filter controls
col_f1, col_f2 = st.columns(2)
with col_f1:
    pet_filter_options = ["All pets"] + [p.pet_name for p in owner.pets]
    filter_pet = st.selectbox("Filter by pet", pet_filter_options, key="filter_pet")
with col_f2:
    filter_status = st.radio(
        "Show tasks",
        ["All", "Pending only", "Completed only"],
        horizontal=True,
        key="filter_status",
    )

pet_name_arg = None if filter_pet == "All pets" else filter_pet
completed_arg = None
if filter_status == "Pending only":
    completed_arg = False
elif filter_status == "Completed only":
    completed_arg = True

if st.button("Generate Schedule"):
    filtered = schedule.filter_tasks(
        pet_name=pet_name_arg,
        completed=completed_arg,
        owner=owner,
    )

    if not filtered:
        st.info("No tasks match the selected filters.")
    else:
        pet_name_map = {p.id: p.pet_name for p in owner.pets}

        # Group by date (filter_tasks already returns them sorted)
        by_date: dict = defaultdict(list)
        for t in filtered:
            key = t.timeslot.date() if t.timeslot else "No date"
            by_date[key].append(t)

        total = len(filtered)
        done = sum(1 for t in filtered if t.completed)
        st.success(f"Showing {total} task(s) — {done} completed, {total - done} pending.")

        for date, tasks in by_date.items():
            st.markdown(f"**{date}**")
            rows = []
            for t in tasks:
                status = "Done" if t.completed else "Pending"
                conflict = schedule.check_conflicts(t.timeslot, t) if not t.completed and t.timeslot else None
                rows.append({
                    "Time": t.timeslot.strftime("%H:%M") if t.timeslot else "—",
                    "Pet": pet_name_map.get(t.pet_id, f"#{t.pet_id}"),
                    "Task(s)": ", ".join(t.tasks),
                    "Repeat": t.frequency or "one-off",
                    "Status": status,
                })
                if conflict:
                    st.warning(conflict)

            st.dataframe(rows, use_container_width=True)
