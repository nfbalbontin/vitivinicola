from poblacion_datos import poblar_recetas
import json

with open('docs/lotes_estanques_dict.txt', 'r') as fl: 
    dicc = json.load(fl)

recetas = poblar_recetas('docs/vitivinicola.xlsx')

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
        for receta in dicc[lote]['cantidad_x_receta']:
            cantidad_total[dicc[lote]['tipo']][receta] += dicc[lote]['cantidad_x_receta'][receta]

for receta in p_alcoholico:
    for lote in dicc:
        if 'p_alcoholico' in dicc[lote].keys():
            if receta in dicc[lote]['cantidad_x_receta'].keys():
                cantidad = dicc[lote]['cantidad_x_receta'][receta]
                ponderado = cantidad / cantidad_total[dicc[lote]['tipo']][receta]
                potencial = ponderado * dicc[lote]['p_alcoholico'] * recetas[receta].ponderador[dicc[lote]['tipo']]
                p_alcoholico[receta] += potencial

print(p_alcoholico)

