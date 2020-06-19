from gurobipy import *
from poblacion_datos import poblar_lotes, poblar_uvas, poblar_recetas, poblar_vinos

# Diccionarios de datos
lotes = poblar_lotes("docs/vitivinicola.xlsx")
uvas = poblar_uvas("docs/vitivinicola.xlsx")
vinos = poblar_vinos("docs/vitivinicola.xlsx")
recetas = poblar_recetas("docs/vitivinicola.xlsx")

# Demanda por satisfacer incluyendo mermas
perdidas_merma = 0.498
dps_vino_a = vinos["A"].volumen * 1333 / perdidas_merma
dps_vino_b = vinos["B"].volumen * 1333 / perdidas_merma
dps_vino_c = vinos["C"].volumen * 1333 / perdidas_merma
dps_vino_d = vinos["D"].volumen * 1333 / perdidas_merma
dps_vino_e = vinos["E"].volumen * 1333 / perdidas_merma

for semana in range(1, 15):
    if semana == 1:
        dia_inicial = -6
        dia_final = 1
    elif semana == 2:
        dia_inicial = 1
        dia_final = 7
    else:
        dia_inicial = 7 * (semana - 2)
        dia_final = 7 * (semana - 1)

    # Conjuntos
    """
    D: días
    L: lotes
    J: uvas
    V: vinos
    R: recetas
    """
    D = [i for i in range(dia_inicial, dia_final)]
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
    y_jrv: cantidad de uva j que se usa para hacer la receta r del vino v
    w_jd: cantidad de uva j cosechada el día d en kilogramos
    b_vr: cantidad de vino v hecho con la receta r
    t_v: cantidad total del vino v producida
    """
    x = m.addVars(L, D, vtype=GRB.BINARY, name="x_ld")
    y = m.addVars(J, R, V, vtype=GRB.CONTINUOUS, name="y_jrv")
    w = m.addVars(J, D, vtype=GRB.CONTINUOUS, name="w_jd")
    b = m.addVars(V, R, vtype=GRB.CONTINUOUS, name="b_vr")
    t = m.addVars(V, vtype=GRB.CONTINUOUS, name="t_v")

    # Parámetros
    M = 1000000000000000  # número muy grande
    perdidas_merma_2 = 0.52  # hasta clarificación
    y_max = (10000 / perdidas_merma_2) * 18  # capacidad máxima de fábrica en un día, calibrable (18 horas de producción)
    relacion = {}  # 1 si la uva j esta en el lote l
    for uva in uvas:
        for lote in lotes:
            if uva == lote[0:3]:
                relacion[uva, lote] = 1
            else:
                relacion[uva, lote] = 0

    # Función Objetivo
    m.setObjective((2.8 * t["A"] + 3.1 * t["B"] + 3.05 * t["C"] + 2.7 * t["D"] + 2.4 * t["E"])
        - sum(lotes[l].precio * lotes[l].tn * 1000 * x[l, d] for l in L for d in D)
        - sum(lotes[l].calcular_costo(d) * x[l, d] for l in L for d in D),
        GRB.MAXIMIZE,
    )

    # Restricciones
    # Definición variable w
    m.addConstrs(
        sum(x[l, d] * lotes[l].tn * 1000 * relacion[j, l] for l in L) == w[j, d]
        for j in J
        for d in D
    )

    # Definición variable y
    m.addConstrs(
        sum(w[j, d] for d in D) == sum(y[j, r, v] for r in R for v in V) for j in J
    )

    # Cada tipo de vino solo se puede hacer con sus recetas
    for receta in recetas:
        for vino in vinos:
            if receta[0] != vino:  
                m.addConstrs(y[j,receta,vino] == 0 for j in J)

    # Relación entre variables x y w (revisar)
    m.addConstrs(
        sum(x[l, d] * M * relacion[j, l] for l in L) >= w[j, d] for d in D for j in J
    )

    # Un lote puede ser comprado máximo una vez
    m.addConstrs(sum(x[l, d] for d in D) <= 1 for l in L)

    # Cantidad cosechada en un día no puede superar el máximo de la fábrica al día
    m.addConstrs(sum(w[j, d] for j in J) <= y_max for d in D)

    # El total de un vino es la suma de sus recetas, definición de variable t
    m.addConstr(t["A"] == b["A", "A1"] + b["A", "A2"])
    m.addConstr(t["B"] == b["B", "B1"] + b["B", "B2"] + b["B", "B3"])
    m.addConstr(t["C"] == b["C", "C1"])
    m.addConstr(t["D"] == b["D", "D1"] + b["D", "D2"])
    m.addConstr(t["E"] == b["E", "E1"] + b["E", "E2"])

    # Si no se hace una receta, no se debería usar uva para esta
    m.addConstrs(b[v, r] * M >= y[j, r , v] for j in J for r in R for v in V)


    # Un lote se puede cosechar solo entre día óptimo +7 y día óptimo -7
    for l in lotes:
        for d in D:
            if not (lotes[l].opt - 7 <= d <= lotes[l].opt + 7):
                m.addConstr(x[l, d] == 0)

    # Si ya se satisface la demanda de un vino, no se puede producir más de ese.
    m.addConstr(t["A"] <= dps_vino_a)
    m.addConstr(t["B"] <= dps_vino_b)
    m.addConstr(t["C"] <= dps_vino_c)
    m.addConstr(t["D"] <= dps_vino_d)
    m.addConstr(t["E"] <= dps_vino_e)

    # Satisfacción de demanda vino A
    ##Receta 1
    m.addConstr(y["J_1", "A1", "A"] == 0.1 * b["A", "A1"])
    m.addConstr(y["J_2", "A1", "A"] == 0.2 * b["A", "A1"])
    m.addConstr(y["J_4", "A1", "A"] == 0.2 * b["A", "A1"])
    m.addConstr(y["J_6", "A1", "A"] == 0.4 * b["A", "A1"])
    m.addConstr(y["J_7", "A1", "A"] == 0.1 * b["A", "A1"])

    ##Receta 2
    m.addConstr(y["J_2", "A2", "A"] == 0.3 * b["A", "A2"])
    m.addConstr(y["J_3", "A2", "A"] == 0.1 * b["A", "A2"])
    m.addConstr(y["J_4", "A2", "A"] == 0.1 * b["A", "A2"])
    m.addConstr(y["J_6", "A2", "A"] == 0.2 * b["A", "A2"])
    m.addConstr(y["J_7", "A2", "A"] == 0.2 * b["A", "A2"])
    m.addConstr(y["J_8", "A2", "A"] == 0.1 * b["A", "A2"])

    # Satisfacción de demanda vino B
    ##Receta 1
    m.addConstr(y["J_1", "B1", "B"] == 0.1 * b["B", "B1"])
    m.addConstr(y["J_2", "B1", "B"] == 0.1 * b["B", "B1"])
    m.addConstr(y["J_4", "B1", "B"] == 0.2 * b["B", "B1"])
    m.addConstr(y["J_5", "B1", "B"] == 0.2 * b["B", "B1"])
    m.addConstr(y["J_6", "B1", "B"] == 0.2 * b["B", "B1"])
    m.addConstr(y["J_7", "B1", "B"] == 0.2 * b["B", "B1"])

    ##Receta 2
    m.addConstr(y["J_1", "B2", "B"] == 0.2 * b["B", "B2"])
    m.addConstr(y["J_2", "B2", "B"] == 0.1 * b["B", "B2"])
    m.addConstr(y["J_3", "B2", "B"] == 0.1 * b["B", "B2"])
    m.addConstr(y["J_4", "B2", "B"] == 0.2 * b["B", "B2"])
    m.addConstr(y["J_5", "B2", "B"] == 0.2 * b["B", "B2"])
    m.addConstr(y["J_6", "B2", "B"] == 0.2 * b["B", "B2"])

    ##Receta 3
    m.addConstr(y["J_1", "B3", "B"] == 0.2 * b["B", "B3"])
    m.addConstr(y["J_3", "B3", "B"] == 0.2 * b["B", "B3"])
    m.addConstr(y["J_5", "B3", "B"] == 0.1 * b["B", "B3"])
    m.addConstr(y["J_6", "B3", "B"] == 0.1 * b["B", "B3"])
    m.addConstr(y["J_7", "B3", "B"] == 0.2 * b["B", "B3"])
    m.addConstr(y["J_8", "B3", "B"] == 0.2 * b["B", "B3"])

    # Satisfacción de demanda vino C
    ##Receta 1
    m.addConstr(y["J_1", "C1", "C"] == 0.5 * b["C", "C1"])
    m.addConstr(y["J_3", "C1", "C"] == 0.1 * b["C", "C1"])
    m.addConstr(y["J_5", "C1", "C"] == 0.1 * b["C", "C1"])
    m.addConstr(y["J_6", "C1", "C"] == 0.2 * b["C", "C1"])
    m.addConstr(y["J_7", "C1", "C"] == 0.1 * b["C", "C1"])

    # Satisfacción de demanda vino D
    ##Receta 1
    m.addConstr(y["J_1", "D1", "D"] == 0.1 * b["D", "D1"])
    m.addConstr(y["J_2", "D1", "D"] == 0.1 * b["D", "D1"])
    m.addConstr(y["J_3", "D1", "D"] == 0.1 * b["D", "D1"])
    m.addConstr(y["J_4", "D1", "D"] == 0.2 * b["D", "D1"])
    m.addConstr(y["J_5", "D1", "D"] == 0.3 * b["D", "D1"])
    m.addConstr(y["J_6", "D1", "D"] == 0.2 * b["D", "D1"])

    ##Receta 2
    m.addConstr(y["J_1", "D2", "D"] == 0.2 * b["D", "D2"])
    m.addConstr(y["J_2", "D2", "D"] == 0.2 * b["D", "D2"])
    m.addConstr(y["J_6", "D2", "D"] == 0.2 * b["D", "D2"])
    m.addConstr(y["J_7", "D2", "D"] == 0.3 * b["D", "D2"])
    m.addConstr(y["J_8", "D2", "D"] == 0.1 * b["D", "D2"])

    # Satisfacción de demanda vino E
    ##Receta 1
    m.addConstr(y["J_1", "E1", "E"] == 0.15 * b["E", "E1"])
    m.addConstr(y["J_2", "E1", "E"] == 0.15 * b["E", "E1"])
    m.addConstr(y["J_3", "E1", "E"] == 0.15 * b["E", "E1"])
    m.addConstr(y["J_4", "E1", "E"] == 0.15 * b["E", "E1"])
    m.addConstr(y["J_5", "E1", "E"] == 0.1 * b["E", "E1"])
    m.addConstr(y["J_6", "E1", "E"] == 0.1 * b["E", "E1"])
    m.addConstr(y["J_7", "E1", "E"] == 0.1 * b["E", "E1"])
    m.addConstr(y["J_8", "E1", "E"] == 0.1 * b["E", "E1"])

    ##Receta 2
    m.addConstr(y["J_1", "E2", "E"] == 0.12 * b["E", "E2"])
    m.addConstr(y["J_2", "E2", "E"] == 0.15 * b["E", "E2"])
    m.addConstr(y["J_3", "E2", "E"] == 0.08 * b["E", "E2"])
    m.addConstr(y["J_4", "E2", "E"] == 0.1 * b["E", "E2"])
    m.addConstr(y["J_5", "E2", "E"] == 0.1 * b["E", "E2"])
    m.addConstr(y["J_6", "E2", "E"] == 0.25 * b["E", "E2"])
    m.addConstr(y["J_7", "E2", "E"] == 0.15 * b["E", "E2"])
    m.addConstr(y["J_8", "E2", "E"] == 0.05 * b["E", "E2"])

    m.optimize()

    print(f"------------ Semana {semana} ------------ ")
    print(f"Obj: {m.objVal}")

    # para mostrar el valor de todas las variables distintas de cero
    for v in m.getVars():
        if v.x != 0:
            print(v.varName, v.X)

    # para mostrar el valor de las variables x distintas de cero
    '''
    print("Lotes comprados:")
    for indice in x:
        if x[indice].x != 0:
            print(x[indice].varName, x[indice].x)
    '''

    # para mostrar el valor de las variables t distintas de cero
    '''
    print("Vino producido:")
    for indice in t:
        print(t[indice].varName, t[indice].x)
    '''

    # Para borrar los lotes que ya fueron comprados
    for indice in x:
        if round(x[indice].x) != 0:
            del lotes[indice[0]]

    # Para restar de la demanda por satisfacer lo que se produjo
    dps_vino_a -= t["A"].x
    dps_vino_b -= t["B"].x
    dps_vino_c -= t["C"].x
    dps_vino_d -= t["D"].x
    dps_vino_e -= t["E"].x

    print("Falta por producir:")
    print(f"A: {dps_vino_a}")
    print(f"B: {dps_vino_b}")
    print(f"C: {dps_vino_c}")
    print(f"D: {dps_vino_d}")
    print(f"E: {dps_vino_e}")

    # m.write('example.lp')

