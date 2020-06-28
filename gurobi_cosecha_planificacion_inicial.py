from gurobipy import *
from poblacion_datos import poblar_lotes, poblar_uvas, poblar_recetas, poblar_vinos
import re
import pandas as pd

# Diccionarios de datos
lotes = poblar_lotes("docs/vitivinicola.xlsx")
uvas = poblar_uvas("docs/vitivinicola.xlsx")
vinos = poblar_vinos("docs/vitivinicola.xlsx")
recetas = poblar_recetas("docs/vitivinicola.xlsx")


# Conjuntos
"""
D: días
L: lotes
J: uvas
V: vinos
R: recetas
"""
D = [i for i in range(-6, 93)]
L = [lote for lote in lotes]
J = [uva for uva in uvas]
V = [vino for vino in vinos]
R = [receta for receta in recetas]

# Modelo
"""
NOTA: el e es para que corra una cantidad de segundos específica. Si se corta antes no llega al óptimo, 
pero si el gap es bajo está cerca del óptimo.
"""
e = gurobipy.Env()
e.setParam("TimeLimit", 30)
m = Model("planificacion_cosecha", env=e)
# m= Model('planificacion_cosecha')

# Variables
""" 
x_ld : binaria que toma valor 1 si se decide comprar el lote l el día d
w_jld: cantidad de uva j del lote l cosechada el día d en kilogramos
y_jlrv: cantidad de uva j  del lote l que se usa para hacer la receta r del vino v
b_vr: cantidad de vino v hecho con la receta r
t_v: cantidad total del vino v producida 
"""
x = m.addVars(L, D, vtype=GRB.BINARY, name="x_ld")
w = m.addVars(J, L, D, vtype=GRB.CONTINUOUS, name="w_jld")
y = m.addVars(J, L, R, V, vtype=GRB.CONTINUOUS, name="y_jlrv")
b = m.addVars(V, R, vtype=GRB.CONTINUOUS, name="b_vr")
t = m.addVars(V, vtype=GRB.CONTINUOUS, name="t_v")

# Parámetros
lambda_1= 0.999999999999999999995 #probar con 0.1, 0.2, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9 y 1. Elegir el mejor resultado
M = 1000000000000000  # número muy grande
porcentaje_post_merma = 0.498
porcentaje_post_merma_2 = 0.52  # hasta clarificación
y_max = (10000 / porcentaje_post_merma_2) * 15  # capacidad máxima de fábrica en un día, calibrable (15 horas de producción)
relacion = {}  # 1 si la uva j esta en el lote l
for uva in uvas:
    for lote in lotes:
        if uva == lote[0:3]:
            relacion[uva, lote] = 1
        else:
            relacion[uva, lote] = 0
demanda_a= vinos["A"].volumen * 1333 / porcentaje_post_merma
demanda_b= vinos["B"].volumen * 1333 / porcentaje_post_merma
demanda_c= vinos["C"].volumen * 1333 / porcentaje_post_merma
demanda_d= vinos["D"].volumen * 1333 / porcentaje_post_merma
demanda_e= vinos["E"].volumen * 1333 / porcentaje_post_merma

# Función Objetivo
m.setObjective((2.8 * t["A"] + 3.1 * t["B"] + 3.05 * t["C"] + 2.7 * t["D"] + 2.4 * t["E"]
    - sum(lotes[l].precio * lotes[l].tn * 1000 * x[l, d] for l in L for d in D)) - sum(lotes[l].calcular_costo(d) * x[l, d] for l in L for d in D), GRB.MAXIMIZE)


# Restricciones
# Definición variable w
m.addConstrs(x[l, d] * lotes[l].tn * 1000 * relacion[j, l] == w[j, l, d]for j in J for l in L for d in D)

# Definición variable y
m.addConstrs(sum(w[j, l, d] for d in D) == sum(y[j, l, r, v] for r in R for v in V) for j in J for l in L)

# Cada tipo de vino solo se puede hacer con sus recetas
for receta in recetas:
    for vino in vinos:
        if receta[0] != vino:  
            m.addConstrs(y[j, l, receta,vino] == 0 for j in J for l in L)

# Un lote puede ser comprado máximo una vez
m.addConstrs(sum(x[l, d] for d in D) <= 1 for l in L)

# Cantidad cosechada en un día no puede superar el máximo de la fábrica al día
m.addConstrs(sum(w[j, l, d] for j in J for l in L) <= y_max for d in D)

# El total de un vino es la suma de sus recetas, definición de variable t
m.addConstr(t["A"] == b["A", "A1"] + b["A", "A2"])
m.addConstr(t["B"] == b["B", "B1"] + b["B", "B2"] + b["B", "B3"])
m.addConstr(t["C"] == b["C", "C1"])
m.addConstr(t["D"] == b["D", "D1"] + b["D", "D2"])
m.addConstr(t["E"] == b["E", "E1"] + b["E", "E2"])

# Si no se hace una receta, no se debería usar uva para esta
m.addConstrs(b[v, r] * M >= y[j, l, r , v] for j in J for r in R for v in V for l in L)

# Un lote se puede cosechar solo entre día óptimo +7 y día óptimo -7
for l in lotes:
    for d in D:
        if d not in range(lotes[l].opt-7,lotes[l].opt + 8):
            m.addConstr(x[l, d] == 0)

# Máximo se produce la demanda (incluyendo mermas) por vino
m.addConstr(t["A"] <= demanda_a)
m.addConstr(t["B"] <= demanda_b)
m.addConstr(t["C"] <= demanda_c)
m.addConstr(t["D"] <= demanda_d)
m.addConstr(t["E"] <= demanda_e)

# Se debe producir el mismo porcentaje de la demanda de todos los tipos de vino
m.addConstr(t["A"]/demanda_a == t["B"]/demanda_b)
m.addConstr(t["B"]/demanda_b == t["C"]/demanda_c)
m.addConstr(t["C"]/demanda_c == t["D"]/demanda_d)
m.addConstr(t["D"]/demanda_d == t["E"]/demanda_e)

# Satisfacción de demanda vino A
##Receta 1
m.addConstr(sum(y["J_1", l, "A1", "A"] for l in L) == 0.1 * b["A", "A1"])
m.addConstr(sum(y["J_2", l, "A1", "A"] for l in L) == 0.2 * b["A", "A1"])
m.addConstr(sum(y["J_4", l, "A1", "A"] for l in L) == 0.2 * b["A", "A1"])
m.addConstr(sum(y["J_6", l, "A1", "A"] for l in L) == 0.4 * b["A", "A1"])
m.addConstr(sum(y["J_7", l, "A1", "A"] for l in L) == 0.1 * b["A", "A1"])

##Receta 2
m.addConstr(sum(y["J_2", l, "A2", "A"] for l in L) == 0.3 * b["A", "A2"])
m.addConstr(sum(y["J_3", l, "A2", "A"] for l in L) == 0.1 * b["A", "A2"])
m.addConstr(sum(y["J_4", l, "A2", "A"] for l in L) == 0.1 * b["A", "A2"])
m.addConstr(sum(y["J_6", l, "A2", "A"] for l in L) == 0.2 * b["A", "A2"])
m.addConstr(sum(y["J_7", l, "A2", "A"] for l in L) == 0.2 * b["A", "A2"])
m.addConstr(sum(y["J_8", l, "A2", "A"] for l in L) == 0.1 * b["A", "A2"])

# Satisfacción de demanda vino B
##Receta 1
m.addConstr(sum(y["J_1", l, "B1", "B"] for l in L) == 0.1 * b["B", "B1"])
m.addConstr(sum(y["J_2", l, "B1", "B"] for l in L) == 0.1 * b["B", "B1"])
m.addConstr(sum(y["J_4", l, "B1", "B"] for l in L) == 0.2 * b["B", "B1"])
m.addConstr(sum(y["J_5", l, "B1", "B"] for l in L) == 0.2 * b["B", "B1"])
m.addConstr(sum(y["J_6", l, "B1", "B"] for l in L) == 0.2 * b["B", "B1"])
m.addConstr(sum(y["J_7", l, "B1", "B"] for l in L) == 0.2 * b["B", "B1"])

##Receta 2
m.addConstr(sum(y["J_1", l, "B2", "B"] for l in L) == 0.2 * b["B", "B2"])
m.addConstr(sum(y["J_2", l, "B2", "B"] for l in L) == 0.1 * b["B", "B2"])
m.addConstr(sum(y["J_3", l, "B2", "B"] for l in L) == 0.1 * b["B", "B2"])
m.addConstr(sum(y["J_4", l, "B2", "B"] for l in L) == 0.2 * b["B", "B2"])
m.addConstr(sum(y["J_5", l, "B2", "B"] for l in L) == 0.2 * b["B", "B2"])
m.addConstr(sum(y["J_6", l, "B2", "B"] for l in L) == 0.2 * b["B", "B2"])

##Receta 3
m.addConstr(sum(y["J_1", l, "B3", "B"] for l in L) == 0.2 * b["B", "B3"])
m.addConstr(sum(y["J_3", l, "B3", "B"] for l in L) == 0.2 * b["B", "B3"])
m.addConstr(sum(y["J_5", l, "B3", "B"] for l in L) == 0.1 * b["B", "B3"])
m.addConstr(sum(y["J_6", l, "B3", "B"] for l in L) == 0.1 * b["B", "B3"])
m.addConstr(sum(y["J_7", l, "B3", "B"] for l in L) == 0.2 * b["B", "B3"])
m.addConstr(sum(y["J_8", l, "B3", "B"] for l in L) == 0.2 * b["B", "B3"])

# Satisfacción de demanda vino C
##Receta 1
m.addConstr(sum(y["J_1", l, "C1", "C"] for l in L) == 0.5 * b["C", "C1"])
m.addConstr(sum(y["J_3", l, "C1", "C"] for l in L) == 0.1 * b["C", "C1"])
m.addConstr(sum(y["J_5", l, "C1", "C"] for l in L) == 0.1 * b["C", "C1"])
m.addConstr(sum(y["J_6", l, "C1", "C"] for l in L) == 0.2 * b["C", "C1"])
m.addConstr(sum(y["J_7", l, "C1", "C"] for l in L) == 0.1 * b["C", "C1"])

# Satisfacción de demanda vino D
##Receta 1
m.addConstr(sum(y["J_1", l, "D1", "D"] for l in L) == 0.1 * b["D", "D1"])
m.addConstr(sum(y["J_2", l, "D1", "D"] for l in L) == 0.1 * b["D", "D1"])
m.addConstr(sum(y["J_3", l, "D1", "D"] for l in L) == 0.1 * b["D", "D1"])
m.addConstr(sum(y["J_4", l, "D1", "D"] for l in L) == 0.2 * b["D", "D1"])
m.addConstr(sum(y["J_5", l, "D1", "D"] for l in L) == 0.3 * b["D", "D1"])
m.addConstr(sum(y["J_6", l, "D1", "D"] for l in L) == 0.2 * b["D", "D1"])

##Receta 2
m.addConstr(sum(y["J_1", l, "D2", "D"] for l in L) == 0.2 * b["D", "D2"])
m.addConstr(sum(y["J_2", l, "D2", "D"] for l in L) == 0.2 * b["D", "D2"])
m.addConstr(sum(y["J_6", l, "D2", "D"] for l in L) == 0.2 * b["D", "D2"])
m.addConstr(sum(y["J_7", l, "D2", "D"] for l in L) == 0.3 * b["D", "D2"])
m.addConstr(sum(y["J_8", l, "D2", "D"] for l in L) == 0.1 * b["D", "D2"])


# Satisfacción de demanda vino E
##Receta 1
m.addConstr(sum(y["J_1", l, "E1", "E"] for l in L) == 0.15 * b["E", "E1"])
m.addConstr(sum(y["J_2", l, "E1", "E"] for l in L) == 0.15 * b["E", "E1"])
m.addConstr(sum(y["J_3", l, "E1", "E"] for l in L) == 0.15 * b["E", "E1"])
m.addConstr(sum(y["J_4", l, "E1", "E"] for l in L) == 0.15 * b["E", "E1"])
m.addConstr(sum(y["J_5", l, "E1", "E"] for l in L) == 0.1 * b["E", "E1"])
m.addConstr(sum(y["J_6", l, "E1", "E"] for l in L) == 0.1 * b["E", "E1"])
m.addConstr(sum(y["J_7", l, "E1", "E"] for l in L) == 0.1 * b["E", "E1"])
m.addConstr(sum(y["J_8", l, "E1", "E"] for l in L) == 0.1 * b["E", "E1"])

##Receta 2
m.addConstr(sum(y["J_1", l, "E2", "E"] for l in L) == 0.12 * b["E", "E2"])
m.addConstr(sum(y["J_2", l, "E2", "E"] for l in L) == 0.15 * b["E", "E2"])
m.addConstr(sum(y["J_3", l, "E2", "E"] for l in L) == 0.08 * b["E", "E2"])
m.addConstr(sum(y["J_4", l, "E2", "E"] for l in L) == 0.1 * b["E", "E2"])
m.addConstr(sum(y["J_5", l, "E2", "E"] for l in L) == 0.1 * b["E", "E2"])
m.addConstr(sum(y["J_6", l, "E2", "E"] for l in L) == 0.25 * b["E", "E2"])
m.addConstr(sum(y["J_7", l, "E2", "E"] for l in L) == 0.15 * b["E", "E2"])
m.addConstr(sum(y["J_8", l, "E2", "E"] for l in L) == 0.05 * b["E", "E2"])

m.optimize()

print(f"Obj: {m.objVal}")

# para mostrar el valor de todas las variables distintas de cero
var_dict = {}
recetas_dict = {}
vinos_dict = {}
for v in m.getVars():
  if round(v.x) != 0: 
    print(v.varName, v.X)
    if round(v.x) != 0 and 'x_ld' in v.varName:
      lote_dia = re.search("(?<=\[)(.*)(?=\])", v.varName).group()
      lote_y_dia = lote_dia.split(',')
      var_dict[lote_y_dia[0]] = {'dia': lote_y_dia[1]}
    if round(v.x) != 0 and 'w_jld' in v.varName: 
      cant_uva = re.search("(?<=\[)(.*)(?=\])", v.varName).group()
      uva_lote_dia = cant_uva.split(',')
      var_dict[uva_lote_dia[1]]['cantidad'] = v.X
    if round(v.x) != 0 and 'y_jlrv' in v.varName: 
      cant_receta = re.search("(?<=\[)(.*)(?=\])", v.varName).group()
      uva_lote_receta_vino = cant_receta.split(',')
      if 'cantidad_x_receta' in var_dict[uva_lote_receta_vino[1]]:
        var_dict[uva_lote_receta_vino[1]]['cantidad_x_receta'][uva_lote_receta_vino[2]] = v.X
      else: 
         var_dict[uva_lote_receta_vino[1]]['cantidad_x_receta'] = {uva_lote_receta_vino[2]: v.X}
    if round(v.x) != 0 and 'b_vr' in v.varName: 
        cant_vino_r = re.search("(?<=\[)(.*)(?=\])", v.varName).group()
        vino_receta = cant_vino_r.split(',')
        recetas_dict[vino_receta[1]] = v.X
    if round(v.X) != 0 and 't_v' in v.varName: 
        cant_vino = re.search("(?<=\[)(.*)(?=\])", v.varName).group()
        vino_receta = cant_vino.split(',')
        vinos_dict[vino_receta[0]] = v.X

resultados_lotes = []
for var in var_dict:
  recetas = {'A1': 6, 'A2': 7, 'B1': 8, 'B2': 9, 'B3': 10, 'C1': 11, 'D1': 12, 'D2': 13, 'E1': 14, 'E2': 15}
  resultado = [var, lotes[var].opt, var_dict[var]['dia'], lotes[var].p_alcoholico(int(var_dict[var]['dia'])), lotes[var].calidad_precio(int(var_dict[var]['dia'])), var_dict[var]['cantidad'], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  for receta in var_dict[var]['cantidad_x_receta']: 
    resultado[recetas[receta]] = var_dict[var]['cantidad_x_receta'][receta]
  resultados_lotes.append(resultado)
resultados_lotes.sort(key=lambda x: x[2])
lotes_df = pd.DataFrame(resultados_lotes, columns = ['Lote', 'Dia Optimo', 'Dia Cosechado', 'Potencial Alcoholico','Ponderador', 'Cantidad Producida', 'A1', 'A2', 'B1', 'B2', 'B3', 'C1', 'D1', 'D2', 'E1', 'E2'])
lotes_df.to_excel('docs/resultados_lotes.xlsx', sheet_name="resultados_lotes")  

resultados_receta = []
for receta in recetas_dict: 
  resultado = [receta, recetas_dict[receta]]
  resultados_receta.append(resultado)
recetas_df = pd.DataFrame(resultados_receta, columns = ['Receta', 'Cantidad'])
recetas_df.to_excel('docs/resultados_recetas.xlsx', sheet_name="resultados_receta")  

resultados_vinos = []
for vino in vinos_dict: 
  resultado = [vino, vinos_dict[vino]]
  resultados_vinos.append(resultado)
vinos_df = pd.DataFrame(resultados_vinos, columns = ['Vino', 'Cantidad'])
vinos_df.to_excel('docs/resultados_vinos.xlsx', sheet_name="resultados_vinos")  


