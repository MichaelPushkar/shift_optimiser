from pulp import LpProblem, LpVariable, LpMinimize, value

# Trivial problem: minimise x + y, subject to x + y >= 10
prob = LpProblem("test", LpMinimize)
x = LpVariable("x", lowBound=0)
y = LpVariable("y", lowBound=0)
prob += x + y          # objective: what we minimise
prob += x + y >= 10    # constraint: the rule that must hold
prob.solve()

print("Status:", prob.status)
print("x =", value(x), " y =", value(y))
print("Total =", value(prob.objective))