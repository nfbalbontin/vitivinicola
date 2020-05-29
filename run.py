from entidades import *
from datetime import datetime, timedelta
import time

if __name__ == '__main__':
    
    inicio = time.time()
    iteracion = 0 
    dict_results = {}
    simulaciones = 1000
    while iteracion < simulaciones: 
        sim = Simulacion(datetime(2020, 1, 1), 94, 'docs/vitivinicola.xlsx')
        sim.run()
        if iteracion == 0: 
            for i in sim.lotes:  
                dict_results[i] = [sim.lotes[i].dias_lluvia["antes"],  sim.lotes[i].dias_lluvia["despues"]]
        else: 
            for i in sim.lotes: 
                dict_results[i][0] += sim.lotes[i].dias_lluvia["antes"]
                dict_results[i][1] += sim.lotes[i].dias_lluvia["despues"]
        iteracion += 1 
    lotes_list = list(dict_results.keys())
    cantidad_lluvia = []
    for i in lotes_list: 
        cantidad_lluvia.append([i,dict_results[i][0]/simulaciones, dict_results[i][0]/simulaciones])
    lotes_df = pd.DataFrame(cantidad_lluvia, columns = ['Lote','7 Dias Antes Prom','7 Dias Despues Prom'])
    lotes_df.insert(0, "Lote", lotes_list, True)
    lotes_df.to_excel('docs/lluvia_lotes_2.xlsx', sheet_name="lluvias")   
    final = time.time()
    print(f"Successful DES simulation. Time excecution: {final - inicio}")
