from entidades import *
from datetime import datetime, timedelta
import time

if __name__ == '__main__':
    
    inicio = time.time()
    iteracion = 0 
    dict_results = {}
    simulaciones = 1000
    while iteracion < simulaciones: 
        sim = Simulacion(datetime(2020, 1, 1), 94)
        sim.run()
        for i in sim.lotes: 
            if iteracion == 0: 
                dict_results[i] = sim.lotes[i].dias_lluvia
            else: 
                for j in range(len(dict_results[i])):
                    dict_results[i][j] += sim.lotes[i].dias_lluvia[j]
        iteracion += 1 
    lotes_list = list(dict_results.keys())
    cantidad_lluvia = []
    for i in lotes_list: 
        lista = []
        for j in range(len(dict_results[i])): 
            lista.append(dict_results[i][j]/simulaciones)
        cantidad_lluvia.append(lista)
    lotes_df = pd.DataFrame(cantidad_lluvia, columns = ['-7','-6','-5','-4', '-3','-2','-1','0','1','2','3','4','5','6','7'])
    lotes_df.insert(0, "Lote", lotes_list, True)
    lotes_df.to_excel('docs/lluvia_lotes_2.xlsx', sheet_name="lluvias")   
    final = time.time()
    print(f"Successful DES simulation. Time excecution: {final - inicio}")
