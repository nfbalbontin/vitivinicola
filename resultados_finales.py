from poblacion_datos import poblar_recetas, poblar_vinos
import json

with open('docs/lotes_estanques_dict.txt', 'r') as fl: 
    dicc = json.load(fl)

recetas = poblar_recetas('docs/vitivinicola.xlsx')
vinos = poblar_vinos('docs/vitivinicola.xlsx')

cantidad_total={'J_1':{'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0},
        'J_2':{'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0},
        'J_3':{'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0},
        'J_4':{'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0},
        'J_5':{'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0},
        'J_6':{'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0},
        'J_7':{'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0},
        'J_8':{'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0}}

p_alcoholico = {'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0}

for lote in dicc:
    if 'p_alcoholico' in dicc[lote].keys():
        for receta in dicc[lote]['cantidad_x_receta_estanques']:
            cantidad_total[dicc[lote]['tipo']][receta] += dicc[lote]['cantidad_x_receta_estanques'][receta]

# Potencial alcoholico 
for receta in p_alcoholico:
    for lote in dicc:
        if 'p_alcoholico' in dicc[lote].keys():
            if receta in dicc[lote]['cantidad_x_receta_estanques'].keys():
                cantidad = dicc[lote]['cantidad_x_receta_estanques'][receta]
                ponderado = cantidad / cantidad_total[dicc[lote]['tipo']][receta]
                potencial = ponderado * dicc[lote]['p_alcoholico'] * recetas[receta].ponderador[dicc[lote]['tipo']]
                p_alcoholico[receta] += potencial
print(f'Potencial alcoholico: {p_alcoholico}')
print('-------------------------------------')

# Cantidad producida por vino
produccion_final = {'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0}
produccion_total = 0
for receta in produccion_final:
    for uva in cantidad_total:
        produccion_final[receta] += recetas[receta].ponderador[uva] * cantidad_total[uva][receta]
for vino in produccion_final:
    produccion_total += produccion_final[vino]

print(f'Cantidad producida por vino: {produccion_final}')
print('-------------------------------------')
print(f'Cantidad producida total: {produccion_final}')
print('-------------------------------------')

# Ganancias por vino
ganancias = {'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'C1': 0, 'D1': 0, 'D2': 0, 'E1': 0, 'E2': 0}
for vino in produccion_final:
    ganancias[vino] += produccion_final[vino] * vinos[vino[0]].precio_2desv
ganancias_totales = 0
for vino in ganancias:
    ganancias_totales += ganancias[vino]
print(f'Ganancias por vino: {ganancias}')
print('-------------------------------------')
print(f'Ganancias totales: {ganancias_totales}')
print('-------------------------------------')

