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

# Who can act as a supervisor (needed for skill constraint)
supervisors = ["Aroha", "Ben", "Chloe"]

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

# Shifts each worker cannot work (study, second job, etc.)
unavailable = {
    "Aroha":  [("Sun", "Lunch"), ("Sun", "Dinner")],
    "Ben":    [("Mon", "Lunch"), ("Tue", "Lunch")],
    "Chloe":  [("Wed", "Dinner"), ("Thu", "Dinner")],
    "Daniel": [("Sat", "Lunch")],
    "Esi":    [("Fri", "Lunch"), ("Fri", "Dinner")],
    "Finn":   [],
}

# Maximum hours any one worker can be rostered in the week
MAX_HOURS = 30

# ---- The optimisation model ----
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, value, PULP_CBC_CMD, LpStatus

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

# --- Availability: a worker cannot be assigned a shift they can't work ---
for w in workers:
    for s in unavailable[w]:
        prob += x[(w, s)] == 0

# --- Coverage: each shift needs enough staff ---
for s in shifts:
    prob += lpSum(x[(w, s)] for w in workers) >= required[s]

# --- Max hours: nobody works more than MAX_HOURS in the week ---
for w in workers:
    prob += lpSum(shift_hours[s[1]] * x[(w, s)] for s in shifts) <= MAX_HOURS

# --- Skill mix: at least one supervisor on every shift ---
for s in shifts:
    prob += lpSum(x[(w, s)] for w in supervisors) >= 1

# --- Rest: no worker does both lunch and dinner on the same day ---
for w in workers:
    for d in days:
        prob += x[(w, (d, "Lunch"))] + x[(w, (d, "Dinner"))] <= 1

prob.solve(PULP_CBC_CMD(msg=0))

# ---- Results ----
status = LpStatus[prob.status]
print(f"Status: {status}")
print(f"Total weekly cost: ${value(prob.objective):,.2f}\n")

# Weekly roster grid: staff down the side, shifts across the top
header = f"{'':<8}" + "".join(f"{d[:3]:>12}" for d in days)
print(header)
print(f"{'':<8}" + "".join(f"{'L / D':>12}" for d in days))
print("-" * len(header))
for w in workers:
    row = f"{w:<8}"
    for d in days:
        l = "L" if x[(w, (d, "Lunch"))].value() == 1 else "."
        dn = "D" if x[(w, (d, "Dinner"))].value() == 1 else "."
        row += f"{l + ' / ' + dn:>12}"
    print(row)

# Hours and pay per worker
print("\nPer-worker summary")
print(f"{'Worker':<8}{'Hours':>8}{'Rate':>8}{'Pay':>10}")
for w in workers:
    hrs = sum(shift_hours[s[1]] for s in shifts if x[(w, s)].value() == 1)
    print(f"{w:<8}{hrs:>8}{workers[w]:>8}{hrs * workers[w]:>10.2f}")

# ---- Chart: cost per day ----
import matplotlib.pyplot as plt

daily_cost = []
for d in days:
    c = sum(cost(w, s) * x[(w, s)].value()
            for w in workers for s in shifts if s[0] == d)
    daily_cost.append(c)

plt.figure(figsize=(8, 4))
plt.bar(days, daily_cost, color="#4a7ba7")
plt.title(f"Optimised labour cost by day (total ${value(prob.objective):,.0f})")
plt.ylabel("Cost (NZD)")
plt.tight_layout()
plt.savefig("roster_cost.png", dpi=150)
print("\nChart saved to roster_cost.png")
plt.show()