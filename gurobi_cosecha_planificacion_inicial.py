from gurobipy import *
from poblacion_datos import poblar_lotes, poblar_uvas, poblar_recetas, poblar_vinos

#Diccionarios de datos
lotes=poblar_lotes('docs/vitivinicola.xlsx')
uvas=poblar_uvas('docs/vitivinicola.xlsx')
vinos=poblar_vinos('docs/vitivinicola.xlsx')
recetas=poblar_recetas('docs/vitivinicola.xlsx')

#Conjuntos
'''
D: días
L: lotes
J: uvas
V: vinos
R: recetas
'''
D=[i for i in range(7)] 
L=[lote for lote in lotes]
J=[uva for uva in uvas]
V=[vino for vino in vinos]
R=[receta for receta in recetas]

#Modelo 
'''
NOTA: el e es para que corra una cantidad de segundos específica. Si se corta antes no llega al óptimo, 
pero si el gap es bajo está cerca del óptimo.
'''
e = gurobipy.Env()
e.setParam('TimeLimit', 60*2)
m= Model('planificacion_cosecha', env=e)
#m= Model('planificacion_cosecha')

#Variables 
''' 
x_ld : binaria que toma valor 1 si se decide comprar el lote l el día d
y_jrv: cantidad de uva j que se usa para hacer la receta r del vino v
w_jd: cantidad de uva j cosechada el día d en kilogramos
b_vr: cantidad de vino v hecho con la receta r
t_v: cantidad total del vino v producida
'''
x = m.addVars(L, D, vtype= GRB.BINARY, name="x_ld")
y = m.addVars(J, R, V,vtype=GRB.CONTINUOUS, name="y_jrv")
w = m.addVars(J, D,vtype=GRB.CONTINUOUS, name="w_jd")
b = m.addVars(V, R,vtype=GRB.CONTINUOUS, name="b_vr")
t = m.addVars(V,vtype=GRB.CONTINUOUS, name="t_v")

#Parámetros
M= 10000000000000 #número muy grande
y_max=150000 #capacidad máxima de fábrica en un día, calibrable (10000kg*15hrs mínimo)
porcentaje_demanda_semana= 0.057 #para cubrir el 80% de la demanda en 14 semanas, calibrable (0.057*14=0.8)
relacion={} # 1 si la uva j esta en el lote l
for uva in uvas:
    for lote in lotes:
        if uva == lote[0:3]:           
            relacion[uva, lote]=1
        else:
            relacion[uva, lote]=0


#Función Objetivo
m.setObjective((2.8*t['A']+3.1*t['B']+3.05*t['C']+2.7*t['D']+2.4*t['E']) - sum(lotes[l].precio * lotes[l].tn *1000 * x[l,d] + lotes[l].calcular_costo(d) * x[l,d] for l in L for d in D), GRB.MAXIMIZE)

#Restricciones
#Definición variable w 
m.addConstrs(sum(x[l,d]* lotes[l].tn *1000* relacion[j,l] for l in L) == w[j,d] for j in J for d in D)

#Definición variable y
m.addConstrs(sum(w[j,d] for d in D) == sum(y[j,r[0], r[1],v] for r in R for v in V) for j in J)

#Relación entre variables x y w
m.addConstrs(sum(x[l,d]* M * relacion[j,l] for l in L) >= w[j,d] for d in D for j in J)

#Un lote puede ser comprado máximo una vez
m.addConstrs(sum(x[l,d] for d in D) <= 1 for l in L)

#Cantidad cosechada en un día no puede superar el máximo de la fábrica al día
m.addConstrs(sum(w[j,d] for j in J) <= y_max for d in D)

#El total de un vino es la suma de sus recetas, definición de variable t
m.addConstr(t['A'] == b['A','A',1]+b['A','A',2])
m.addConstr(t['B'] == b['B','B',1]+b['B','B',2]+ b['B','B',3])
m.addConstr(t['C'] == b['C','C',1])
m.addConstr(t['D'] == b['D','D',1]+b['D','D',2])
m.addConstr(t['E'] == b['E','E',1]+b['E','E',2])

#Un lote se puede cosechar solo entre día óptimo +7 y día óptimo -7
for l in lotes:
    for d in D:
        if not (lotes[l].opt -7 <= d <= lotes[l].opt +7):
            m.addConstr(x[l,d] == 0)

#Satisfacción de demanda vino A
##Receta 1
m.addConstr(y['J_1','A',1, 'A'] == 0.1 * b['A','A',1])
m.addConstr(y['J_2','A',1, 'A'] == 0.2 * b['A','A',1])
m.addConstr(y['J_4','A',1, 'A'] == 0.2 * b['A','A',1])
m.addConstr(y['J_6','A',1, 'A'] == 0.4 * b['A','A',1])
m.addConstr(y['J_7','A',1, 'A'] == 0.1 * b['A','A',1])
##Receta 2
m.addConstr(y['J_2','A',2, 'A'] == 0.3 * b['A','A',2])
m.addConstr(y['J_3','A',2, 'A'] == 0.1 * b['A','A',2])
m.addConstr(y['J_4','A',2, 'A'] == 0.1 * b['A','A',2])
m.addConstr(y['J_6','A',2, 'A'] == 0.2 * b['A','A',2])
m.addConstr(y['J_7','A',2, 'A'] == 0.2 * b['A','A',2])
m.addConstr(y['J_8','A',2, 'A'] == 0.1 * b['A','A',2])

m.addConstr(t['A']<= vinos['A'].volumen* 1000 * porcentaje_demanda_semana)

#Satisfacción de demanda vino B
##Receta 1
m.addConstr(y['J_1','B',1, 'B'] == 0.1 * b['B','B',1])
m.addConstr(y['J_2','B',1, 'B'] == 0.1 * b['B','B',1])
m.addConstr(y['J_4','B',1, 'B'] == 0.2 * b['B','B',1])
m.addConstr(y['J_5','B',1, 'B'] == 0.2 * b['B','B',1])
m.addConstr(y['J_6','B',1, 'B'] == 0.2 * b['B','B',1])
m.addConstr(y['J_7','B',1, 'B'] == 0.2 * b['B','B',1])

##Receta 2
m.addConstr(y['J_1','B',2, 'B'] == 0.2 * b['B','B',2])
m.addConstr(y['J_2','B',2, 'B'] == 0.1 * b['B','B',2])
m.addConstr(y['J_3','B',2, 'B'] == 0.1 * b['B','B',2])
m.addConstr(y['J_4','B',2, 'B'] == 0.2 * b['B','B',2])
m.addConstr(y['J_5','B',2, 'B'] == 0.2 * b['B','B',2])
m.addConstr(y['J_6','B',2, 'B'] == 0.2 * b['B','B',2])

##Receta 3
m.addConstr(y['J_1','B',3, 'B'] == 0.2 * b['B','B',3])
m.addConstr(y['J_3','B',3, 'B'] == 0.2 * b['B','B',3])
m.addConstr(y['J_5','B',3, 'B'] == 0.1 * b['B','B',3])
m.addConstr(y['J_6','B',3, 'B'] == 0.1 * b['B','B',3])
m.addConstr(y['J_7','B',3, 'B'] == 0.2 * b['B','B',3])
m.addConstr(y['J_8','B',3, 'B'] == 0.2 * b['B','B',3])

m.addConstr(t['B']<= vinos['B'].volumen *1000 * porcentaje_demanda_semana)

#Satisfacción de demanda vino C
##Receta 1
m.addConstr(y['J_1','C',1, 'C'] == 0.5 * b['C','C',1])
m.addConstr(y['J_3','C',1, 'C'] == 0.1 * b['C','C',1])
m.addConstr(y['J_5','C',1, 'C'] == 0.1 * b['C','C',1])
m.addConstr(y['J_6','C',1, 'C'] == 0.2 * b['C','C',1])
m.addConstr(y['J_7','C',1, 'C'] == 0.1 * b['C','C',1])

m.addConstr(t['C']<= vinos['C'].volumen *1000 * porcentaje_demanda_semana)

#Satisfacción de demanda vino D
##Receta 1
m.addConstr(y['J_1','D',1, 'D'] == 0.1 * b['D','D',1])
m.addConstr(y['J_2','D',1, 'D'] == 0.1 * b['D','D',1])
m.addConstr(y['J_3','D',1, 'D'] == 0.1 * b['D','D',1])
m.addConstr(y['J_4','D',1, 'D'] == 0.2 * b['D','D',1])
m.addConstr(y['J_5','D',1, 'D'] == 0.3 * b['D','D',1])
m.addConstr(y['J_6','D',1, 'D'] == 0.2 * b['D','D',1])

##Receta 2
m.addConstr(y['J_1','D',2, 'D'] == 0.2 * b['D','D',2])
m.addConstr(y['J_2','D',2, 'D'] == 0.2 * b['D','D',2])
m.addConstr(y['J_6','D',2, 'D'] == 0.2 * b['D','D',2])
m.addConstr(y['J_7','D',2, 'D'] == 0.3 * b['D','D',2])
m.addConstr(y['J_8','D',2, 'D'] == 0.1 * b['D','D',2])

m.addConstr(t['D']<= vinos['D'].volumen*1000 * porcentaje_demanda_semana)

#Satisfacción de demanda vino E
##Receta 1
m.addConstr(y['J_1','E',1, 'E'] == 0.15 * b['E','E',1])
m.addConstr(y['J_2','E',1, 'E'] == 0.15 * b['E','E',1])
m.addConstr(y['J_3','E',1, 'E'] == 0.15 * b['E','E',1])
m.addConstr(y['J_4','E',1, 'E'] == 0.15 * b['E','E',1])
m.addConstr(y['J_5','E',1, 'E'] == 0.1 * b['E','E',1])
m.addConstr(y['J_6','E',1, 'E'] == 0.1 * b['E','E',1])
m.addConstr(y['J_7','E',1, 'E'] == 0.1 * b['E','E',1])
m.addConstr(y['J_8','E',1, 'E'] == 0.1 * b['E','E',1])

##Receta 2
m.addConstr(y['J_1','E',2, 'E'] == 0.12 * b['E','E',2])
m.addConstr(y['J_2','E',2, 'E'] == 0.15 * b['E','E',2])
m.addConstr(y['J_3','E',2, 'E'] == 0.08 * b['E','E',2])
m.addConstr(y['J_4','E',2, 'E'] == 0.1 * b['E','E',2])
m.addConstr(y['J_5','E',2, 'E'] == 0.1 * b['E','E',2])
m.addConstr(y['J_6','E',2, 'E'] == 0.25 * b['E','E',2])
m.addConstr(y['J_7','E',2, 'E'] == 0.15 * b['E','E',2])
m.addConstr(y['J_8','E',2, 'E'] == 0.05 * b['E','E',2])

m.addConstr(t['E'] <= vinos['E'].volumen* 1000 * porcentaje_demanda_semana)

m.optimize()

print(f'Obj: {m.objVal}')
for v in m.getVars():
    if v.x != 0:
        print(v.varName, v.x)
#m.write('example.lp')