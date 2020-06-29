from collections import deque
from random import expovariate, randint, uniform, seed
from datetime import datetime, timedelta
import time
import numpy as np
import csv
import pandas as pd
import math
seed(1)

class Simulacion:
    def __init__(self, datetime, dias_simulacion):
        # usamos datetime para manejar temporalidad
        self.date = datetime
        #self.tiempo_actual = date
        self.dia_actual = -6
        self.hora_actual = 0
        #self.dias_totales = date + timedelta(days = dias_simulacion)
        self.dias_totales = dias_simulacion
        self.lotes = self.poblar_lotes('docs/vitivinicola.xlsx')
       

    # motor de la simulacion 
    def run(self):
        while self.dia_actual < self.dias_totales:
            #print("\r\r\033[95m DIA {0}\033".format(self.date + timedelta(days = self.dia_actual)))
            for i in self.lotes: 
                rango = self.dia_actual - self.lotes[i].opt
                if  -7 <= rango <= 7: 
                    estado = self.lotes[i].evento_lluvia(rango)
                    #if estado: 
                        #print("LLUEVE EN EL LOTE {}".format(i))
                    #else: 
                        #print("NO LLUEVE EN EL LOTE {}".format(i))
                   #print("\r\r{0}[0m el día: {1} [0m en el lote \033[93m{1}\033".format("\033[92m[Llueve]\033" if self.lotes[i].evento_lluvia == 1 else "\033[91m[No llueve]\033", self.date + timedelta(days = self.dia_actual), i))
                         #while self.hora_actual < 24: 
            #    self.hora_actual += 1
            self.dia_actual += 1 

  
    def poblar_lotes(self, path): 
        lotes = {}
        df_lotes = pd.read_excel(path, sheet_name='lotes', encoding="utf-8", usecols='A:Z', dtype={'Lote COD': str, 'Tipo UVA': str, 'Tn': int, 'Dia optimo cosecha': int, 'p_01': float, 'p_11': float, 'km a planta': int, '$/kg': float})
        for row in range(df_lotes['Lote COD'].count()): 
            lotes[df_lotes.iloc[row, 0]] = Lote(df_lotes.iloc[row, 0], df_lotes.iloc[row, 1], df_lotes.iloc[row, 2],df_lotes.iloc[row, 3],
            df_lotes.iloc[row, 4], df_lotes.iloc[row, 5], df_lotes.iloc[row, 6], df_lotes.iloc[row, 7], df_lotes.iloc[row, 8],
            df_lotes.iloc[row, 9], df_lotes.iloc[row, 10], df_lotes.iloc[row, 11])
        return lotes 

class Lote:
    def __init__(self, codigo, tipo_u, tn, opt, p_01, p_11, dist, precio, t_hasta_ferm, nu, dias_lluvia_prom, brix):
        """ 
        codigo: codigo de lote 
        tipo_u: tipo de uva que genera el lote
        tn: toneladas de produccion
        opt: dia optimo de cosecha 
        p_01: probabilidad de que en el lote llueva si ayer no llovio
        p_11: probabilidad de que en el lote llueva si ayer llovio
        dist: distancia que existe entre el lote y la planta 
        precio: precio de la uva por kilogramo 
        dias_lluvia: dias que efectivamente llovio o no en ese lote 
        llovio_ayer: indica si llovio o no el dia anterior 
        """
        self.codigo = codigo
        self.tipo_u = tipo_u 
        self.tn = tn 
        self.opt = int(opt)
        self.p_01 = p_01
        self.p_11 = p_11 
        self.dist = dist 
        self.precio = precio 
        # Este tiempo ya considera todo el que pasa hasta antes de entrar a fermentacion 
        self.tiempo = t_hasta_ferm
        self.brix = brix
        self.nu = nu
        self.dias_lluvia_prom = dias_lluvia_prom
        self.dias_lluvia = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.lluvias = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.peso = self.prom_peso_recetas()

    def evento_lluvia(self, rango):
        eventos= [1, 0]
        if -8 < rango < 8:
            # Si es el primer dia de evaluacion del lote, por lo que no hay registro anterior
            if rango == -7: 
                probabilidades = [self.p_01, (1-self.p_01)]
            # Revisamos si llovio o no el dia anterior
            else: 
                if self.dias_lluvia[rango + 6] == 1:
                    probabilidades = [self.p_11, (1-self.p_11)]
                else:
                    probabilidades = [self.p_01, (1-self.p_01)]
            evento = np.random.choice(eventos,p=probabilidades)
            # Si llueve, agregamos el evento de lluvia, sino no. 
            if evento == 1: 
                self.lluvias[rango + 7] = 1
            for dia in self.lluvias[0:rango + 7]:
                self.dias_lluvia[rango + 7] += dia
                
    def calidad_precio(self, dia_cosechado): 
        # self.prom_peso_recetas*self.p_alcoholico
        return float(1+self.peso)*self.p_alcoholico(dia_cosechado)/(self.precio*self.dias_lluvia_prom)

    def p_alcoholico(self, dia_cosechado, tiempo=0, dias_lluvia=False):
        rango = dia_cosechado - self.opt
        llovio = 0
        for i in range(rango + 7): 
            llovio += self.lluvias[i]
        if not dias_lluvia: 
            return 0.62*self.brix*(self.calidad_max(rango)-llovio*0.1 - (1 - math.exp(-(self.tiempo+tiempo)/self.nu)))
        else: 
            return 0.62*self.brix*(self.calidad_max(rango)-dias_lluvia*0.1 - (1 - math.exp(-(self.tiempo+tiempo)/self.nu)))

    def prom_peso_recetas(self): 
        if self.tipo_u == 'J_1': 
            return 0.185555556
        elif self.tipo_u == 'J_2': 
            return 0.1625
        elif self.tipo_u == 'J_3': 
            return 0.118571429
        elif self.tipo_u == 'J_4': 
            return 0.164285714
        elif self.tipo_u == 'J_5': 
            return 0.157142857
        elif self.tipo_u == 'J_6': 
            return 0.205
        elif self.tipo_u == 'J_7': 
            return 0.16875
        elif self.tipo_u == 'J_8': 
            return 0.11
        else: 
            return 0.00000000001

    def calidad_max(self, rango): 
        if self.tipo_u == 'J_1': 
            return -((rango**2)/490) + rango/140 + 1
        elif self.tipo_u == 'J_2': 
            return -3*((rango**2)/1960) + rango/1400 + 1
        elif self.tipo_u == 'J_3': 
            return -9*((rango**2)/4900) + rango/700 + 1
        elif self.tipo_u == 'J_4': 
            return -19*((rango**2)/9800) + rango/280 + 1
        elif self.tipo_u == 'J_5': 
            return 1-(rango**2)/980
        elif self.tipo_u == 'J_6': 
            return -3*((rango**2)/1400)+ rango/1400 + 1
        elif self.tipo_u == 'J_7': 
            return -13*((rango**2)/9800) + rango/1400 + 1
        elif self.tipo_u == 'J_8': 
            return -17*((rango**2)/9800) + rango/280 + 1 
        else: 
            return 0.00000000001

    def calcular_costo(self, dia):
        # LLueve = 1, No LLueve = 0
        eventos= [1, 0]
        rango = dia - self.opt
        if -8 < rango < 8:
            # Si es el primer dia de evaluacion del lote, por lo que no hay registro anterior
            if rango == -7: 
                probabilidades = [self.p_01, (1-self.p_01)]
            # Revisamos si llovio o no el dia anterior
            else: 
                if self.lluvias[rango + 6] == 1:
                    probabilidades = [self.p_11, (1-self.p_11)]
                else:
                    probabilidades = [self.p_01, (1-self.p_01)]
            evento = np.random.choice(eventos,p=probabilidades)
            # Si llueve, agregamos el evento de lluvia, sino no. 
            if evento == 1: 
                self.lluvias[rango + 7] = 1

            # Se suman todos los dias que llovieron hasta la fecha
            llovio = 0
            for i in range(rango + 7): 
                llovio += self.lluvias[i]
            calidad = self.calidad_max(rango)-llovio*0.1 - (1 - math.exp(-self.tiempo/self.nu))
            costo= abs((self.precio/calidad) - self.precio)* self.tn*1000
            """
            print("LOTE: {}\n".format(self.codigo))
            print("DIA: {}\n".format(dia))
            print("RANGO: {}".format(rango))
            print("CALIDAD MAX: {}\n".format(self.calidad_max(rango)))
            print("PERDIDA DE CALIDAD: {}".format(1-math.exp(-self.tiempo/self.nu)))
            print("LLUVIAS: {}".format(llovio))
            print("CALIDAD TOTAL: {}".format(self.calidad_max(rango)-llovio*0.1 - (1-math.exp(-self.tiempo/self.nu))))
            print("COSTO: {}".format(costo))
            """
            return costo
        else: 
            return 1000000000000
            print("entre -.-")


        
                                
class Procesamiento: 
    def __init__(self, uvas, estanques, recetas, vinos): 
        self.uvas = uvas #diccconarios de población de datos
        self.estanques= estanques
        self.recetas = recetas
        self.vinos = vinos
        
        self.eq_molienda = 4
        self.eq_prensado = 6
        self.eq_clarificacion = 2
        self.eq_mezcla= 2
        self.cap_max_molienda = 12000
        self.cap_max_prensado = 15000
        self.cap_max_clarificacion = 10000
        self.cap_max_mezcla= 10000
        self.caudal_molienda = 3000
        self.caudal_prensado = 2500
        self.caudal_clarificacion = 5000
        self.caudal_mezcla = 5000  
        self.merma_molienda = 0.05
        self.merma_prensado = 0.35
        self.merma_mezcla = 0.15
        self.merma_clarificacion = 0.05
        self.corriente_molienda = 11400 
        self.corriente_prensado = 9750
        self.corriente_mezcla = 8500
        self.corriente_clarificacion = 9500 

    def ingreso_lote(self, lote):
        self.uvas[lote.tipo_u].ingreso_uva(lote.tn) 

    def molienda(self, tipo_uva):
        pass
 
    def prensado(self):
        pass

    def clarificacion(self):
        pass

    def fermentacion(self):
        pass

    def mezcla(self): 
        pass 


class Uva:
    def __init__(self, tipo, nu, min_ferm, max_ferm, brix, min_opt, max_opt):
        """
        nu: parametro de perdida de calidad 
        min: minimo tiempo de fermentacion 
        max: maximo tiempo de fermentacion 
        brix: el brix de cada uva
        min_opt: 7 dias antes del dia de cosecha optimo 
        max_opt: 7 dias despues del dia de cosecha optimo 
        """
        self.tipo = tipo 
        self.nu = nu 
        self.min = min_ferm
        self.max = max_ferm 
        self.prom = int(round((self.min + self.max)/2, 0))
        self.brix = brix 
        self.min_opt = min_opt
        self.max_opt = max_opt 

        self.masa_entrada = 0 #kg
        self.produccion_molienda = 0 #kg
        self.produccion_prensado = 0 #L
        self.produccion_clarificacion = 0 #L

    def ingreso_uva(self, toneladas):
        self.masa_entrada += toneladas * 1000 #kg

class Vino: 
    def __init__(self, tipo, precio_dstbn, precio_media, precio_dst, volumen):
        """
        precio_media: la media del precio del vino 
        precio_dst: desviacion estandar del precio del vino (fracción)
        volumen: volumen demandado por el vino
        precio_2desv: precio - 2 desviaciones estandar
        """
        self.tipo = tipo 
        self.precio_dstbn = precio_dstbn 
        self.precio_media = precio_media
        self.precio_dst = precio_dst 
        self.volumen = volumen
        self.precio_2desv = precio_media - 2 * (precio_dst * precio_media)

class Receta:
    def __init__(self, tipo_vino, id_receta, J1, J2, J3, J4, J5, J6, J7, J8):
        self.tipo_vino= tipo_vino
        self.id= id_receta
        self.ponderador = {'J_1': J1, 'J_2': J2, 'J_3': J3, 'J_3': J3, 'J_4': J4, 'J_5': J5, 'J_6': J6, 'J_7': J7, 'J_8': J8}
        self.J1 = J1
        self.J2 = J2
        self.J3 = J3
        self.J4 = J4
        self.J5 = J5
        self.J6 = J6
        self.J7 = J7
        self.J8 = J8

class Estanque:
    def __init__(self, nombre):
        self.tipo = nombre
        self.tiempo = 9
        self.disponible = True
        self.lotes = []

class Estanques:
    def __init__(self, tipo, capacidad, estanques): 
        self.tipo = tipo 
        self.capacidad = capacidad
        self.estanques = estanques

    @property
    def disponibilidad(self): 
        disp = 0
        for e in self.estanques: 
            if e.disponible == True: 
                disp += 1
        return disp

    def fermentar(self, cantidad_estanques, lote): 
        cantidad_est = cantidad_estanques
        pos = 0
        for e in self.estanques: 
            if e.disponible == True: 
                print('FERMENTANDO EN ESTANQUE {}{}'.format(self.tipo, pos))
                e.disponible = False
                e.lotes.append(lote)
                cantidad_est -= 1
            if cantidad_est == 0: 
                break 
            pos += 1
                
        
