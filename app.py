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

# --- View Schedule ---
st.subheader("Current Schedule")

if st.button("Generate Schedule"):
    if not schedule.tasks:
        st.info("No tasks scheduled yet.")
    else:
        # Sort chronologically, then group by date
        sorted_tasks = sorted(
            schedule.tasks,
            key=lambda t: t.timeslot if t.timeslot else datetime.max,
        )
        by_date: dict = defaultdict(list)
        for t in sorted_tasks:
            key = t.timeslot.date() if t.timeslot else "No date"
            by_date[key].append(t)

        for date, tasks in by_date.items():
            st.markdown(f"**{date}**")
            rows = [
                {
                    "time": t.timeslot.strftime("%H:%M") if t.timeslot else "—",
                    "pet_id": t.pet_id,
                    "tasks": ", ".join(t.tasks),
                    "completed": t.completed,
                }
                for t in tasks
            ]
            st.table(rows)
