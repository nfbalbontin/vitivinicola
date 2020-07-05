from gurobipy import *
from poblacion_datos import poblar_lotes, poblar_uvas, poblar_recetas, poblar_vinos, poblar_estanques

# Diccionarios de datos
lotes = poblar_lotes("docs/vitivinicola.xlsx")
uvas = poblar_uvas("docs/vitivinicola.xlsx")
vinos = poblar_vinos("docs/vitivinicola.xlsx")
recetas = poblar_recetas("docs/vitivinicola.xlsx")
estanques = poblar_estanques("docs/vitivinicola.xlsx")

cantidad_lotes = 100
LL = [[lotes[lote],lotes[lote].opt] for lote in lotes]
LL.sort(key=lambda x: x[1])
sel_lotes = {}
L = []
max_dia = 0
for lote in LL[0:cantidad_lotes]: 
  sel_lotes[lote[0].codigo] = lote[0]
  L.append(lote[0].codigo)
  if lote[0].opt > max_dia:
    max_dia = lote[0].opt
D = [i for i in range(-6, max_dia + 7)]
J = [uva for uva in uvas]
V = [vino for vino in vinos]
R = [receta for receta in recetas]
E = [estanque for estanque in estanques]


"""
x_lde : binaria: 1 si se cosecha el lote l el dia d para fermentar en el tanque e
y_ejd : binaria: 1 si el tanque e comienza a fermentar uva j el dia d
z_ed : binaria: 1 si el tanque e esta aun fermentando el dia d
w_ed : binaria: 1 si el tanque e termina el dia d
r_ed : binaria: 1 si el tanque e comienza a fermentar diferentes lotes el dia d
"""

x = m.addVars(L, D, E, vtype=GRB.BINARY, name="x_lde")
y = m.addVars(E, J, D, vtype=GRB.BINARY, name="y_ejd")
z = m.addVars(E, D, vtype=GRB.BINARY, name="z_ed")
w = m.addVars(E, D, vtype=GRB.BINARY, name="w_ed")
r = m.addVars(E, D, vtype=GRB.BINARY, name="r_ed")

m.setObjective(sum(x[l, d, e] for l in L for d in D for e in E), GRB.MAXIMIZE)

# Un lote se puede cosechar solo entre día óptimo +7 y día óptimo -7


# Un lote solamente se puede cosechar 1 vez
m.addConstrs(sum(x[l, d, e] for e in E for d in D) ==  1 for l in L)
for d in D: 
  for j in J: 
    for e in E: 
      for pos in range(len(L_j)):
        # Establece la relacion de la cantidad de lotes cosechados del tipo de uva j en el dia d a ser procesados en el tanque 
        # de fermentacion e al comienzo del proceso de fermentacion del tanque j  
        m.addConstr(sum(x[l.codigo, d, e] for l in L_j[pos]) - len(L_j[pos])*y[e, j, d] <= 0)
        # Los estanques deben llenarse a lo mas a 25% 
        m.addConstr(0.25*estanques[e].capacidad*y[e,j,d]  - sum(x[l.codigo, d, e]*l.tn for l in L_j[pos]) <= 0)
        # Los estanques no pueden superar su capacidad 
        m.addConstr(estanques[e].capacidad*y[e,j,d]  - sum(x[l.codigo, d, e]*l.tn for l in L_j[pos]) >= 0)
        m.addConstr(sum(x[l.codigo, d, e] for l in L_j[pos]) - 1 - len(L_j[pos])*r[e, d] <= 0)
      if d + uvas[j].prom - 1 < max_dia + 7:
        m.addConstr((uvas[j].prom - 1)*y[e,j,d]  - sum(z[e, dd] for dd in range(d + uvas[j].prom - 1)) <= 0)
for d in D: 
  for e in E: 
    if d != -6: 
      m.addConstr(sum(y[e, j, d] for j in J) + z[e, d-1] - w[e, d] - z[e, d] == 0)
      m.addConstr(sum(y[e, j, d] for j in J) + z[e, d-1] <= 1)
    m.addConstr(sum(y[e, j, d]for j in J) <= 1)

m.addConstrs(z[e, -6] == 0 for e in E)

orignumvars = m.NumVars
m.feasRelaxS(2, False, False, True)
m.optimize()

print(f"Obj: {m.objVal}")

for v in m.getVars():
  if round(v.X) != 0:
    print(v.varName, v.X)
