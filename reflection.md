# PawPal+ Project Reflection

## 1. System Design
- The user should be able to have these core functions at the minimum: add a pet, schedule a walk, and see all of the daily tasks for the pet.

**a. Initial design**

- Briefly describe your initial UML design.
- The initial UML design should have classes such as "Pet", "Tasks", and maybe another one for "Schedule". The pet class will have all of the information to do with the pet like the pet_name, pet_id, its breed, the tricks it can do and the food it eats. The Tasks class can have everything to do with the tasks the owner has to complete for its pet, it can be things such as walking the pet, feeding the pet, playing with it, etc. The schedule class can be basic and can just include date_times and things like that, that the user cannot do specific things or most things unless their schedule is open.
- What classes did you include, and what responsibilities did you assign to each?
The Pet class should have the attributes of: "id": unique primary key, "pet_name": string, "pet_tricks": array of strings, "walked": boolean, and "fed": boolean.
The Tasks class can have the attributes of: "id": unique primary key, "tasks": array of strings, "pet_id": which is a foreign key that links to the Pet class. It can have methods such as: walk_pet(), feed_pet().
The Schedule class can have attributes such as: "id": primary key integer unique, and this schedule can also have timeslots that are either booked or open (boolean). The user can then open up their schedule to complete more tasks for their pet.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
- The design DID change during implementation after I had claude review the draft and reflect on the UML diagram. It turned out that there were a lot of missing relationships and logic bottlenecks. There was no link in between Pet -> Tasks, Schedule -> Tasks, and also Tasks had not schedule_id or timeslot. Since there were no references I would of had to make additional logic in the future to look most things up. A lot of other logic from the first iteration didnt handle edge cases and certain conditions, which would've broke the logic eventually.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
- The scheduler considers time the most, then pet identity uniqueness, feeding frequency, task reccurrence / frequency
- I decided the time constraint matters the most because of all of the logic that is dependent on it, such as conflict detection, reccurence, filtering, and more. Its all built around the timeslot field. The schedule is useless without a valid and non-conflicting timeslot.

**b. Tradeoffs**

The scheduler only flags conflicts when two tasks share an **exact** start time — it does not account for task duration or overlapping windows. For example, if Buddy has a 30-minute walk scheduled at 8:00 AM and a vet appointment is booked at 8:15 AM, no conflict is raised because the timeslots are different datetime values even though the two events overlap in real life.

This is a reasonable tradeoff for the current scope of the app for a few reasons. First, tasks in PawPal+ do not carry a duration field, so the scheduler has no data to compare against — detecting overlaps would require guessing or hard-coding durations per task type, which adds complexity without a clear source of truth. Second, for most everyday pet care routines (feeding, short walks, grooming), tasks are typically short and discrete enough that exact-time matching catches the most common scheduling mistake: accidentally booking two things at the identical hour and minute. Third, keeping conflict detection simple means the logic stays in one place (`check_conflicts` in `Schedule`) and is easy to reason about, test, and extend later — adding duration-aware overlap detection would be a natural next iteration once a `duration` field is added to the `Tasks` dataclass.

**Smarter Scheduling**
- The core scheduling methods (is_slot_open, book_slot, free_slot, add_pet, remove_pet) were all implemented from scratch, including a duplicate-pet guard and orphan-task cleanup on removal. A filter_tasks method was added to Schedule so tasks can be queried by pet name, completion status, or both — always returned in chronological order using sorted(). Recurring task support was built via complete_task, which uses Python's timedelta to auto-book the next occurrence (+1 day for daily, +7 days for weekly) the moment a task is marked done. Finally, lightweight conflict detection was introduced through check_conflicts and a redesigned book_slot — rather than blocking a booking outright, the scheduler always accepts the task but returns a descriptive warning string that distinguishes same-pet double-bookings from cross-pet scheduling collisions, keeping the app usable while still surfacing the problem to the owner.



---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
