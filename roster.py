# ---- The restaurant: staff and shifts ----
# A small café open Mon-Sun, with a lunch and a dinner shift each day.

# Our staff. Each has an hourly pay rate (NZD).
workers = {
    "Aroha":  26,   # supervisor
    "Ben":    24,   # supervisor
    "Chloe":  23,
    "Daniel": 23,
    "Esi":    22,
    "Finn":   22,
}

# Who can act as a supervisor (needed for skill constraint later)
supervisors = ["Aroha", "Ben"]

# The shifts. We'll label them by day + period.
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
periods = ["Lunch", "Dinner"]

# Build the list of all shifts, e.g. ("Fri", "Dinner")
shifts = []
for d in days:
    for p in periods:
        shifts.append((d, p))

# How long each shift is, in hours (used to compute cost)
shift_hours = {"Lunch": 5, "Dinner": 6}

# How many staff each shift needs (coverage requirement).
# Weekends and dinners are busier.
required = {}
for d in days:
    for p in periods:
        if d in ["Fri", "Sat", "Sun"] and p == "Dinner":
            required[(d, p)] = 3   # busy weekend dinners
        elif p == "Dinner":
            required[(d, p)] = 2   # weekday dinners
        else:
            required[(d, p)] = 1   # lunches are quiet

# ---- Quick check: print what we've set up ----
print("Workers:", list(workers.keys()))
print("Total shifts in the week:", len(shifts))
print("Staff needed on Fri Dinner:", required[("Fri", "Dinner")])
print("Staff needed on Mon Lunch:", required[("Mon", "Lunch")])