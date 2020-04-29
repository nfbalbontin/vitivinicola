from collections import deque
from random import choice
from random import expovariate


class Vehiculo:
    # Esta clase modela los autos que llegan a la revision

    def __init__(self, tiempo_llegada=0):
        self.tipo_vehiculo = choice(['moto', 'camioneta', 'auto'])
        self.tiempo_llegada = tiempo_llegada

    def __repr__(self):
        return 'Tipo vehiculo: {0}'.format(self.tipo_vehiculo)

class Taller:

    def __init__(self, tipos):
        self.tarea_actual = None
        self.tiempo_revision = 0
        self.tipos = tipos

    def pasar_vehiculo(self, vehiculo):
        self.tarea_actual = vehiculo
        # Creamos un tiempo de atencion aleatorio
        self.tiempo_revision = round(
            expovariate(self.tipos[vehiculo.tipo_vehiculo]))

    @property
    def ocupado(self):
        return self.tarea_actual != None

class Simulacion:
    # Esta clase implemeta la simulacion.
    # Tambien se puede usar una funcion como en el caso anterior.
    # Se inicializan todas las variables utilizadas en la simulacion.

    def __init__(self, tiempo_maximo, tasa_llegada, tipos):
        self.tiempo_maximo_sim = tiempo_maximo
        self.tasa_llegada = tasa_llegada
        self.tiempo_simulacion = 0
        self.tiempo_proximo_auto = 0
        self.tiempo_atencion = float('Inf')
        self.tiempo_espera = 0
        self.planta = Taller(tipos)
        self.cola_espera = deque()
        self.vehiculos_atendidos = 0

    def proximo_auto(self, tasa_llegada):
        # actualizar el tiempo de llegada del próximo auto
        self.tiempo_proximo_auto = self.tiempo_simulacion + \
            round(expovariate(tasa_llegada))

    def run(self):
        # Este metodo ejecuta la simulacion de la revision y la cola de espera
        # se estima aleatoreamente la llegada de un auto a la linea de revision
        self.proximo_auto(self.tasa_llegada)

        # Ejecutamos el ciclo verificando que el tiempo de simulacion no supere
        # el tiempo maximo de simulacion
        while self.tiempo_simulacion < self.tiempo_maximo_sim:

            # Primero revisamos el evento actual. Si la planta esta vacia o
            # si la planta esta ocupada, y no ha salido algun vehiculo de la planta,
            # el tiempo de simulacion siempre sera el tiempo de llegada de los vehiculos.
            # Cuando sale el vehiculo, el tiempo de simulacion debe ser el tiempo transcurrido
            # hasta esta revision.

            # actualizamos el tiempo de simulacion al primer evento que sea el
            # siguiete
            self.tiempo_simulacion = min(self.tiempo_proximo_auto,
                                         self.tiempo_atencion)

            print('[SIMULACION] tiempo = {0} min'.format(
                self.tiempo_simulacion))

            # se compara si es que el próximo evento es una llegada
            if self.tiempo_simulacion == self.tiempo_proximo_auto:

                # Mientras se este revisando un vehiculo en la planta,
                # el resto de los vehiculos se sigue acumulando en la cola. Por cada
                # llegada se genera el proximo evento mediante el metodo
                # proximo_auto

                # Si un vehículo ha llegado, debemos ponerlo en la cola
                self.cola_espera.append(Vehiculo(self.tiempo_proximo_auto))

                # También debemos generar un tiempopara
                # la llegada del próximo auto
                self.proximo_auto(self.tasa_llegada)

                print('[COLA] Llega {0} en : {1} min.'.format(
                    self.cola_espera[-1].tipo_vehiculo,
                    self.tiempo_simulacion))

                # Si el taller está ocupado el vehículo tiene
                # que esperar su turno. Si no está ocupado, es atendido.
                if not self.planta.ocupado:

                    # Si la planta esta desocupada y quedan elementos en la cola de espera,
                    # el siguiente vehiculo sale de la cola y entra a la planta.
                    # Al entrar se le asigna aleatoriamente el tiempo de atencion y se genera
                    # el instante estimado de termino de la revision

                    # sacamos un auto en la cola de atencion
                    proximo_vehiculo = self.cola_espera.popleft()

                    # y lo pasamos a la planta
                    self.planta.pasar_vehiculo(proximo_vehiculo)

                    # actualizar tiempo de espera, en realidad se suma 0
                    self.tiempo_espera += self.tiempo_simulacion \
                        - self.planta.tarea_actual.tiempo_llegada

                    # nuevo tiempo de atención
                    self.tiempo_atencion = self.tiempo_simulacion + \
                        self.planta.tiempo_revision

                    # actualizar contador de vehículos que salieron de la cola
                    self.vehiculos_atendidos += 1

                    print('[PLANTA] Entra {0} con un tiempo de atencion',
                          'de {1} min.').format(
                              self.planta.tarea_actual.tipo_vehiculo,
                              self.planta.tiempo_revision)

            elif self.tiempo_simulacion == self.tiempo_atencion:

                # Cuando un vehículo ha terminado, uno nuevo puede ser servido.
                print('[PLANTA] Sale: {0} a los {1} min.'.format(
                    self.planta.tarea_actual.tipo_vehiculo,
                    self.tiempo_simulacion))

                if len(self.cola_espera) == 0:
                        # el siguiente tiempo de salida tiene que estar
                        # fuera del rango de la simulación porque ningún
                        # vehículo puuede salir del taller si ninguno
                        # está siendo atendido
                    self.tiempo_atencion = float('Inf')
                    self.planta.tarea_actual = None

                else:

                    # tomar el primer vehículo de la cola de espera
                    proximo_vehiculo = self.cola_espera.popleft()

                    # el vehículo comienza a se atendido
                    self.planta.pasar_vehiculo(proximo_vehiculo)

                    # update the waiting time
                    self.tiempo_espera += self.tiempo_simulacion - \
                        self.planta.tarea_actual.tiempo_llegada

                    # the next final service time is generated
                    self.tiempo_atencion = self.tiempo_simulacion \
                        + self.planta.tiempo_revision

                self.vehiculos_atendidos += 1

        print('Estadisticas:')
        print('Tiempo total atencion {0} min.'.format(self.tiempo_atencion))
        print('Total de vehiculos atendidos: {0}'.format(
            self.vehiculos_atendidos))
        print('Tiempo promedio de espera {0} min.'.format(
            round(self.tiempo_espera / self.vehiculos_atendidos)))


if __name__ == '__main__':
    # En este ejemplo inicializamos la simulacion con 50 min como tiempo maximo.
    # Definimos la tasa de llegada de los vehiculos en un vehiculo cada 5 minutos.
    # Tambien definimos un diccionario con los tipos de vehiculos que atendera la planta
    # y la tasa promedio de atencion para cada tipo de vehiculo.
    # Experimente con tiempos mayores y otras tasas de atencion y llegada.

    # Los tipos de vehículos y sus tasas de servicios
    vehiculos = {'moto': 1.0/8, 'auto': 1.0/15, 'camioneta': 1.0/20}

    # tasa de llegada de los vehículos
    tasa_llegada_vehiculos = 1/5

    # La simulación corre hasta 50 minutos
    s = Simulacion(50, tasa_llegada_vehiculos, vehiculos)
    s.run()

