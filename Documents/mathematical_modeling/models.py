from ortools.sat.python import cp_model
import json


rooms_data = ["A1001", "A1002", "AI", "A250", "S006", "S008", "AIII", "R110"]
subjects_data = [
    {"code": "INF111", "teacher": "ATSA", "level": "Level 1"},
    {"code": "INF121", "teacher": "KOUOKAM", "level": "Level 1"},
    {"code": "INF211", "teacher": "ABESSOLO", "level": "Level 2"},
    {"code": "INF251", "teacher": "BAYEM", "level": "Level 2"},
    {"code": "INF4017", "teacher": "NDOUNDAM", "level": "Level 4"}
]

num_days = 6  # Mon-Sat
num_periods = 5 # P1-P5
weights = [1, 2, 4, 8, 16] # w1 < w2 < w3 < w4 < w5 to prioritize morning

model = cp_model.CpModel()


x = {}
for s_idx in range(len(subjects_data)):
    for d in range(num_days):
        for p in range(num_periods):
            for r_idx in range(len(rooms_data)):
                x[s_idx, d, p, r_idx] = model.NewBoolVar(f'x_s{s_idx}_d{d}_p{p}_r{r_idx}')


for s_idx in range(len(subjects_data)):
    model.Add(sum(x[s_idx, d, p, r_idx] for d in range(num_days) 
                  for p in range(num_periods) 
                  for r_idx in range(len(rooms_data))) == 1)


for d in range(num_days):
    for p in range(num_periods):
        for r_idx in range(len(rooms_data)):
            model.Add(sum(x[s_idx, d, p, r_idx] for s_idx in range(len(subjects_data))) <= 1)


teachers = list(set(s['teacher'] for s in subjects_data))
for teacher in teachers:
    t_subs = [i for i, s in enumerate(subjects_data) if s['teacher'] == teacher]
    for d in range(num_days):
        for p in range(num_periods):
            model.Add(sum(x[s_idx, d, p, r_idx] for s_idx in t_subs 
                          for r_idx in range(len(rooms_data))) <= 1)


levels = list(set(s['level'] for s in subjects_data))
for lvl in levels:
    lvl_subs = [i for i, s in enumerate(subjects_data) if s['level'] == lvl]
    for d in range(num_days):
        for p in range(num_periods):
            model.Add(sum(x[s_idx, d, p, r_idx] for s_idx in lvl_subs 
                          for r_idx in range(len(rooms_data))) <= 1)


objective_terms = []
for s_idx in range(len(subjects_data)):
    for d in range(num_days):
        for p in range(num_periods):
            for r_idx in range(len(rooms_data)):
                objective_terms.append(x[s_idx, d, p, r_idx] * weights[p])

model.Minimize(sum(objective_terms))


solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Timetable Generated Successfully:\n")
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for d in range(num_days):
        print(f"--- {day_names[d]} ---")
        for p in range(num_periods):
            for s_idx, s in enumerate(subjects_data):
                for r_idx, r in enumerate(rooms_data):
                    if solver.Value(x[s_idx, d, p, r_idx]) == 1:
                        print(f"Period {p+1}: {s['code']} | Teacher: {s['teacher']} | Room: {r} | Class: {s['level']}")
else:
    print("No feasible solution found.")
