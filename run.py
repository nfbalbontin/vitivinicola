from entidades import *
from poblacion_datos import * 
from datetime import datetime, timedelta

if __name__ == '__main__':
    sim = Simulacion(datetime(2020, 1, 1), 94)
    sim.run(poblar_lotes('docs/vitivinicola.xlsx'))