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

D=[i for i in range(3)]
print(lotes)
L=[lote for lote in lotes]
print(uvas)
J=[uva for uva in uvas]
print(vinos)
K=[vino for vino in vinos]
print(recetas)
M=[receta for receta in recetas]


#Modelo 
m= Model('planificacion_cosecha')

#Variables
'''
b_j : binaria que toma valor 1 si se decide comprar el lote l el día t, y 0 si no
y_jld: Cantidad de kilos cosechados de la uva tipo j el día t en el lote l (y por lo tanto, transportados a la planta el día t)    
x_km:Metros cúbicos de vino k producidos por receta m.
'''
b = m.addVars(L, ub=1, name="b_jl")
y = m.addVars(J, L, D,vtype=GRB.CONTINUOUS, name="y_jld")
x = m.addVars(K, M,vtype=GRB.CONTINUOUS, name="x_km")

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
"""
Costo asociado a la pérdida de calidad por cosechar el día d del tipo de uva j dado un día óptimo de cosecha del lote l.
"""
c_djl=10000 #calcular


#Función Objetivo

m.setObjective()
m.setObjective(sum((lotes[l].precio * lotes[l].tn * b[l] + for l in L) + sum(c_djl * y[j,l] for l in L for j in J), GRB.MINIMIZE)

#Restricciones
#No se puede cosechar más de los kg disponibles en el lote.
m.addConstrs(sum(y[j,l,d] for d in D) <= lotes[l].tn * b[j,l]* 1000 for l in L for j in J)





m.optimize()