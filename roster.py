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

# ---- The optimisation model ----
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, value, PULP_CBC_CMD

prob = LpProblem("staff_rostering", LpMinimize)

# Decision variables: x[(w,s)] = 1 if worker w works shift s
x = {}
for w in workers:
    for s in shifts:
        x[(w, s)] = LpVariable(f"x_{w}_{s[0]}_{s[1]}", cat="Binary")

# Cost of putting worker w on shift s
def cost(w, s):
    day, period = s
    return workers[w] * shift_hours[period]

# Objective: minimise total wage bill
prob += lpSum(cost(w, s) * x[(w, s)] for w in workers for s in shifts)

# Coverage: each shift needs enough staff
for s in shifts:
    prob += lpSum(x[(w, s)] for w in workers) >= required[s]

prob.solve(PULP_CBC_CMD(msg=0))

print("Status:", prob.status)
print("Total weekly cost: $", value(prob.objective))
print()
for s in shifts:
    assigned = [w for w in workers if x[(w, s)].value() == 1]
    print(f"{s[0]} {s[1]:<7} needs {required[s]}  ->  {assigned}")