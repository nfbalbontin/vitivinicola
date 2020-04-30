from collections import deque 
from random import expovariate, randint, uniform, seed
from datetime import datetime, timedelta
import time 
seed(1)


class Camion:
    _id = 0
    def __init__(self, tiempo_instancia):
        Camion._id += 1
        self.id = Camion._id
        self.tiempo_llegada = tiempo_instancia
        self.estacion = None #estación de descarga
        self.tiempo_abandono_fabrica = None
        self.tiempo_descarga= 10
    
    def generar_tiempo_abandono_fabrica(self, tiempo_actual):
        self.tiempo_abandono_fabrica = tiempo_actual + timedelta(minutes=self.tiempo_descarga)

    def generar_tiempo_total_sistema(self, tiempo_actual): #cola + descarga
        self.tiempo_total_sistema = tiempo_actual - self.tiempo_llegada
        print(self.tiempo_total_sistema)

    def __str__(self):
        return "-> {}".format(self.id)

class Fabrica:
    def __init__(self, tiempo_simulacion, tasa_llegada): 
        # usamos datetime para manejar temporalidad
        date = datetime(2020, 1, 1)
        newdate = date.replace(hour=9) #suponiendo fabrica abre a las 9am

        # seteamos variables de tiempo
        self.tiempo_actual = newdate
        self.tiempo_maximo = newdate + timedelta(hours = tiempo_simulacion)

        # seteamos inputs de distribuciones y estructuras de la simulación
        self.tasa_llegada = tasa_llegada
        self.estacion = {"E1" : None, "E2": None}
        self.proximo_camion_llega = self.tiempo_actual + timedelta(minutes=int(expovariate(1/tasa_llegada))) #definir distribución de llegada
        self.cola = deque()

        # las variables para el cálculo de estadísticas se dejan en el constructor
        self.cantidad_camiones = 0 #camiones que llegan a la fabrica
        self.cantidad_camiones_estacion= 0 #cantidad de camiones que ingresan a la estación de descarga
        self.cantidad_camiones_descargados= 0 #camiones que terminan la descarga

        # manejamos una lista con todos los tiempos de abandono que se generan
        self.tiempos_abandono_fabrica = [[self.tiempo_actual.replace(year=3000), None]]


    # usamos properties para trabajar con mayor comodidad el atributo del proximo camion que termina de ser atendido
    @property
    def proximo_camion_termina(self):
        # Esta la próxima persona que terminará de ser atendida con su tiempo asociado
        x, y = self.tiempos_abandono_fabrica[0]
        return x, y

    @property
    def proximo_evento(self):
        tiempos = [self.proximo_camion_llega,
                   self.proximo_camion_termina[0]]
        tiempo_prox_evento = min(tiempos)

        if tiempo_prox_evento >= self.tiempo_maximo:
            return "fin"
        eventos = ["llegada_camion", "abandono_fabrica"]
        return eventos[tiempos.index(tiempo_prox_evento)]

    # funcion que define la llegada de camiones al fabrica
    def llegar_camion(self):
        time.sleep(0.4)
        self.tiempo_actual = self.proximo_camion_llega
        self.proximo_camion_llega = self.tiempo_actual + timedelta(minutes=int(expovariate(1/self.tasa_llegada))) # definir distribucion de llegada
        camion = Camion(self.tiempo_actual, 3) #definir unidades de carga
        self.cantidad_camiones += 1
        print("\r\r\033[91m[LLEGADA]\033[0m ha llegado un camion id: {} {}".format(camion._id,self.tiempo_actual))

        if self.estacion["E1"] == None:
            #self.tiempo_sistema_vacio += (self.tiempo_actual - self.ultimo_tiempo_actual_vacio)
            self.estacion["E1"] = camion
            self.estacion["E1"].estacion = "E1" 
            self.estacion["E1"].generar_tiempo_abandono_fabrica(self.tiempo_actual)
            self.tiempos_abandono_fabrica.append((camion.tiempo_abandono_fabrica, camion))
            self.tiempos_abandono_fabrica.sort(key=lambda z: datetime.strftime(z[0], "%Y-%m-%d-%H-%M"))
            print("\r\r\033[92m[INGRESO ESTACION]\033[0m ha ingresado un camion a E1 id: {} {}".format(
                self.estacion["E1"]._id, self.tiempo_actual))
            self.cantidad_camiones_estacion += 1

        elif self.estacion["E2"] == None:
            #self.tiempo_sistema_vacio += (self.tiempo_actual - self.ultimo_tiempo_actual_vacio)
            self.estacion["E2"] = camion
            self.estacion["E2"].estacion = "E2" 
            self.estacion["E2"].generar_tiempo_abandono_fabrica(self.tiempo_actual)
            self.tiempos_abandono_fabrica.append((camion.tiempo_abandono_fabrica, camion))
            self.tiempos_abandono_fabrica.sort(key=lambda z: datetime.strftime(z[0], "%Y-%m-%d-%H-%M"))
            print("\r\r\033[92m[INGRESO ESTACION]\033[0m ha ingresado un camion a E2 id: {} {}".format(
                self.estacion["E2"]._id, self.tiempo_actual))
            self.cantidad_camiones_estacion += 1
        
        else:
            self.cola.append(camion)
        
        #print(self.estacion["E1"])

    # funcion que define la salida de camiones de la fabrica
    def abandono_fabrica(self):
        time.sleep(0.4)
        #print("quien va a abandonar "+ str(self.proximo_camion_termina[1]))
        self.tiempo_actual, camion_sale = self.proximo_camion_termina
        #print("quien va a abandonar " + str(camion_sale))
        if len(self.cola) > 0: # A tiene prioridad sobre B
            # Si hay, la proxima persona pasa
            print('[RETIRA] Se ha desocupado la Estacion {}, abandona el camion id {} {}'.
                  format(camion_sale.estacion, camion_sale, self.tiempo_actual))
            prox_camion = self.cola.popleft()
            #print(prox_camion)
            prox_camion.estacion = camion_sale.estacion
            self.camion_pasa_a_ser_atendido(prox_camion, camion_sale.estacion)
        else:
            print("[RETIRA] La estacion {} termina de atender al camion id: {}, esta desocupado pero "
                  "no hay camiones en cola {}".format(camion_sale.estacion, camion_sale, self.tiempo_actual))
            self.estacion[camion_sale.estacion] = None
        self.tiempos_abandono_fabrica.pop(0)
        self.cantidad_camiones_descargados += 1


    # funcion que apoya el ingreso de camones
    def camion_pasa_a_ser_atendido(self, camion, e):
        time.sleep(0.4)
        self.estacion[e] = camion
        self.estacion[e].generar_tiempo_abandono_fabrica(self.tiempo_actual)
        self.tiempos_abandono_fabrica.append((self.estacion[e].tiempo_abandono_fabrica, camion))
        self.tiempos_abandono_fabrica.sort(key=lambda z: datetime.strftime(z[0], "%Y-%m-%d-%H-%M"))
        print("\r\r\033[92m[INGRESO ESTACION]\033[0m ha ingresado un camion a {2} id: {0} {1}".format(camion,self.tiempo_actual,e))
        self.cantidad_camiones_estacion += 1


    # motor de la simulacion 
    def run(self):
        while self.tiempo_actual < self.tiempo_maximo:
            evento = self.proximo_evento
            # print("en el modulo hay {}".format(self.modulo_atencion))
            if evento == "fin":
                self.tiempo_actual = self.tiempo_maximo
                break
            elif evento == "llegada_camion":
                self.llegar_camion()
            elif evento == "abandono_fabrica":
                self.abandono_fabrica()
                
    def show(self):
        print("La cantidad de camiones que llegaron a la fabrica {}".format(self.cantidad_camiones))
        print("La cantidad de camiones que entraron a estación  de descarga {}".format(self.cantidad_camiones_estacion))
        print("La cantidad de camiones que terminaron la descarga {}".format(self.cantidad_camiones_descargados))


new_fabrica = Fabrica(4)
inicio = time.time()
new_fabrica.run()
new_fabrica.show()
final = time.time()
print()
print(f"Successful DES simulation. Time excecution: {final - inicio}")