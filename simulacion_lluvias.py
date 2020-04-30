from collections import deque
from random import expovariate, randint, uniform, seed
from datetime import datetime, timedelta
from entidades import Lote
import time
import numpy as np
seed(1)

class Lluvias:
    def __init__(self, tiempo_simulacion, lote):
        # usamos datetime para manejar temporalidad
        date = datetime(2020, 1, 1)

        # seteamos variables de tiempo
        self.tiempo_actual = date
        self.tiempo_maximo = date + timedelta(days = tiempo_simulacion)

        # seteamos inputs de distribuciones y estructuras de la simulación
        self.lote = lote
        self.p_11= self.lote.p_11
        self.p_01= self.lote.p_01
        self.llovio_ayer = False #supongo día 0

        # las variables para el cálculo de estadísticas se dejan en el constructor
        self.cantidad_dias_lluvia = 0 
        self.cantidad_dias_no_lluvia = 0

    @property
    def proximo_evento(self):
        eventos= ["llueve", "no_llueve"]
        if self.llovio_ayer:
            probabilidades = [self.p_11, (1-self.p_11)]
        else:
            probabilidades = [self.p_01, (1-self.p_01)]
        prox_evento= np.random.choice(eventos,p=probabilidades)
        tiempo_prox_evento= self.tiempo_actual + timedelta(days = 1)

        if tiempo_prox_evento > self.tiempo_maximo:
            return "fin"
        return prox_evento

    # funcion que define la lluvia
    def llueve(self):
        time.sleep(0.4)
        print("\r\r\033[91m[Llueve]\033[0m el día: {} ".format(self.tiempo_actual))
        self.tiempo_actual += timedelta(days = 1)
        self.llovio_ayer = True
        self.cantidad_dias_lluvia += 1

    # funcion que define no lluvia
    def no_llueve(self):
        time.sleep(0.4)
        print("\r\r\033[92m[No llueve]\033[0m el día: {} ".format(self.tiempo_actual))
        self.tiempo_actual += timedelta(days = 1)
        self.llovio_ayer = False
        self.cantidad_dias_no_lluvia += 1


    # motor de la simulacion 
    def run(self):
        while self.tiempo_actual < self.tiempo_maximo:
            evento = self.proximo_evento
            if evento == "fin":
                self.tiempo_actual = self.tiempo_maximo
                break
            elif evento == "llueve":
                self.llueve()
            elif evento == "no_llueve":
                self.no_llueve()
                
    def show(self):
        print("La cantidad de días que llovió fue: {}". format(self.cantidad_dias_lluvia))
        print("La cantidad de días que no llovió fue: {}". format(self.cantidad_dias_no_lluvia))


l=Lote("codigo", "tipo_u", "tn", "opt", 0.8, 0.1, "dist", "precio") #Ejemplo
lluvias = Lluvias(7,l) #Ejemplos simulación de 7 días para el lote l
inicio = time.time()
lluvias.run()
lluvias.show()
final = time.time()
print()
print(f"Successful DES simulation. Time excecution: {final - inicio}")