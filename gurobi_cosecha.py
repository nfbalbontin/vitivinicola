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
K: vinos
M: recetas
'''

D=[i for i in range(100)]
L=[lote for lote in lotes]
J=[uva for uva in uvas]
K=[vino for vino in vinos]
M=[receta for receta in recetas]

#Modelo 
m= Model('planificacion_cosecha')

#Variables
'''
b_jl : binaria que toma valor 1 si se decide comprar el lote l de la uva tipo j el día t, y 0 si no
y_jld: Cantidad de kilos cosechados de la uva tipo j el día t en el lote l (y por lo tanto, transportados a la planta el día t)    
x_km:Metros cúbicos de vino k producidos por receta m.
'''
b = m.addVars(J, L, ub=1, vtype=GRB.BINARY, name="b_jl")
y = m.addVars(J, L, D,vtype=GRB.CONTINUOUS, name="y_jld")
x = m.addVars(K, M,vtype=GRB.CONTINUOUS, name="x_km")
c = m.addVars(J, D, K, M, vtype=GRB.CONTINUOUS, name="c_jdkm")
s = m.addVars(J, K, M, vtype=GRB.CONTINUOUS, name="s_jkm" )
q = m.addVars(J, D, vtype=GRB.CONTINUOUS, name="q_jd")
gc = m.addVars(J, D, K, M, vtype=GRB.CONTINUOUS, name="gc_jdkm")
gs = m.addVars(J, K, M, vtype=GRB.CONTINUOUS, name="gs_jkm")

#Parámetros
'''
c_l:costo del kilo de uva disponible en el lote l
j_jl:dato binario, tiene valor 1 si el tipo de uva j está disponible en el lote l, y 0 si no.
km_l:km de distancia entre el punto de cosecha del lote l y la planta
pl01:probabilidad de lluvia para el día t+1 si en t no ha llovido, para el lote l
pl11:probabilidad de lluvia para el día t+1 si en t no ha llovido, para el lote l
diaopt_l:día óptimo de cosecha del lote l
T_l:toneladas disponibles en el lote l
f_jkm:proporción de vino madre tipo j, que requiere la receta m para hacer el vino k.
s_j:Stock teórico de vinos madres de la uva tipo j, necesarios para producir x_km metros cúbicos de vino.
o_jdl:litros (o m3) de vino tipo j que queda después de la fermentación, por cada kilo de uva cosechado el día d en el lote L.
c0_djl: Costo asociado a la pérdida de calidad por cosechar el día d del tipo de uva j dado un día óptimo de cosecha del lote l.
c1_jl: Costo por kilo asociado a la pérdida de calidad del tipo de uva j que produce trasladar la uva desde el lote l hasta la planta.
c2_djl: Costo asociado a la pérdida de calidad del tipo de uva j, la que produce el tiempo en cola de descarga en la planta dado que se cosechó el día d. 
c3_djl: Costo asociado a la pérdida en calidad en el tipo de uva j que producen las lluvias si se cosecha el día d en el lote l. 
Ymax:Cantidad de kilos de uvas máximos que se pueden cosechar en un día.
Sjmax:Cantidad de kilos de uvas máximos que se pueden cosechar durante un periodo T, dada la capacidad de procesamiento que tienen los estanques de fermentación.
'''
relacion={} # 1 si la uva j esta en el lote l
for uva in uvas:
    for lote in lotes:
        if uva == lote[0:3]:           
            relacion[uva, lote]=1
        else:
            relacion[uva, lote]=0

#Función Objetivo
m.setObjective(sum(lotes[l].precio * 1000 * lotes[l].tn * b[j,l] for l in L for j in J), GRB.MINIMIZE)

#Restricciones
#1: Se debe satisfacer la demanda Dk de vinos
m.addConstrs(sum(x[k, m[0],m[1]] for m in M) >= vinos[k].volumen for k in K)

#2: Se necesitan Cjdkm litros de vino madre tipo j, para producir x litros de vino k mediante la receta m.
m.addConstrs((x[k, m[0], m[1]]*recetas[m].J1)/0.95 == s["J_1", k, m[0], m[1]] for k in K for m in M)

m.addConstrs((x[k, m[0], m[1]]*recetas[m].J2)/0.95 == s["J_2", k, m[0], m[1]] for k in K for m in M)

m.addConstrs((x[k, m[0], m[1]]*recetas[m].J3)/0.95 == s["J_3", k, m[0], m[1]] for k in K for m in M)

m.addConstrs((x[k, m[0], m[1]]*recetas[m].J4)/0.95 == s["J_4", k, m[0], m[1]] for k in K for m in M)

m.addConstrs((x[k, m[0], m[1]]*recetas[m].J5)/0.95 == s["J_5", k, m[0], m[1]] for k in K for m in M)

m.addConstrs((x[k, m[0], m[1]]*recetas[m].J6)/0.95 == s["J_6", k, m[0], m[1]] for k in K for m in M)

m.addConstrs((x[k, m[0], m[1]]*recetas[m].J7)/0.95 == s["J_7", k, m[0], m[1]] for k in K for m in M)

m.addConstrs((x[k, m[0], m[1]]*recetas[m].J8)/0.95 == s["J_8", k, m[0], m[1]] for k in K for m in M)

#3: Se debe cumplir la demanda comprando y kilos de uva tipo j, para producir Sj metros cúbicos de vino madre j
m.addConstrs(sum(c[j, d, k, m[0], m[1]] for m in M for k in K) == 0.55*sum(b[j, l]*y[j, l, d] for l in L) for j in J for d in D)

#4: Restriccion calidad (inicialmente la vamos a hacer 1 para todos los vinos y 
# todos los días)
m.addConstrs(q[j, d] == 1 for j in J for d in D)

#5: Grado alcohólico del vino madre Cjdkm
m.addConstrs(c[j, d, k, m[0], m[1]] == 0.62*uvas[j].brix*q[j, d] for j in J for d in D for k in K for m in M)

#6: Restricción de grados alcohólicos de Sjkm
m.addConstrs(sum(c[j, d, k, m[0], m[1]]*gc[j, d, k, m[0], m[1]] for d in D) == gs[j, k, m[0], m[1]] for j in J for k in K for m in M)

#7: Restricción de masa de Sjkm
m.addConstrs(sum(c[j, d, k, m[0], m[1]] for d in D) == s[j, k, m[0], m[1]] for j in J for k in K for m in M)

#8: Restricción de grados alcohólicos mínimos para producir un vino k mediante la receta m. 
m.addConstrs(recetas[m].J1 * gs['J_1', k, m[0], m[1]] + recetas[m].J2 * gs['J_2', k, m[0], m[1]] + recetas[m].J3 * gs['J_3', k, m[0], m[1]] + recetas[m].J4 * gs['J_4', k, m[0], m[1]] + recetas[m].J5 * gs['J_5', k, m[0], m[1]] + recetas[m].J6 * gs['J_6', k, m[0], m[1]] + recetas[m].J7 * gs['J_7', k, m[0], m[1]] + recetas[m].J8 * gs['J_8', k, m[0], m[1]] >= 14 for m in M for k in K)

#9: Hay Tl kilos disponibles en el lote l.
m.addConstrs(sum(y[j, l, d] for d in D) <= lotes[l].tn*1000*b[j, l] for j in J for l in L)

#10: Sólo se pueden cosechar uvas tipo j del Lote l.
m.addConstrs(y[j, l, d] <= relacion[j,l] *4000000 for d in D for j in J for l in L)

m.optimize()
