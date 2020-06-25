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
    def __init__(self, datetime, dias_simulacion, path_excel):
        # usamos datetime para manejar temporalidad
        self.date = datetime
        #self.tiempo_actual = date
        self.dia_actual = -6
        self.hora_actual = 0
        #self.dias_totales = date + timedelta(days = dias_simulacion)
        self.dias_totales = dias_simulacion
        self.lotes = self.poblar_lotes(path_excel)
        self.uvas = self.poblar_uvas(path_excel)
        self.vinos = self.poblar_vinos(path_excel)
        self.recetas = self.poblar_recetas(path_excel)
        self.estanques = self.poblar_estanques(path_excel)
        # seteamos inputs de distribuciones y estructuras de la simulación

    # motor de la simulacion 
    def run(self):
        while self.dia_actual < self.dias_totales:
            #print("\r\r\033[95m DIA {0}\033".format(self.date + timedelta(days = self.dia_actual)))
            for i in self.lotes: 
                if self.lotes[i].opt - 7 <= self.dia_actual <= self.lotes[i].opt: 
                    self.lotes[i].dias_lluvia["antes"] += self.lotes[i].evento_lluvia
                elif self.lotes[i].opt < self.dia_actual <= self.lotes[i].opt + 7: 
                    self.lotes[i].dias_lluvia["despues"] += self.lotes[i].evento_lluvia
                   # print("\r\r{0}[0m el día: {1} [0m en el lote \033[93m{1}\033".format("\033[92m[Llueve]\033" if self.lotes[i].evento_lluvia == 1 else "\033[91m[No llueve]\033", self.date + timedelta(days = self.dia_actual), i))
                         #while self.hora_actual < 24: 
            #    self.hora_actual += 1
            self.dia_actual += 1 

  
    def poblar_lotes(self, path): 
        lotes = {}
        df_lotes = pd.read_excel(path, sheet_name='lotes', encoding="utf-8", usecols='A:J', dtype={'Lote COD': str, 'Tipo UVA': str, 'Tn': int, 'Dia optimo cosecha': int, 'p_01': float, 'p_11': float, 'km a planta': int, '$/kg': float})
        
        for row in range(df_lotes['Lote COD'].count()): 
            lotes[df_lotes.iloc[row, 0]] = Lote(df_lotes.iloc[row, 0], df_lotes.iloc[row, 1], df_lotes.iloc[row, 2], 
                                                df_lotes.iloc[row, 3], df_lotes.iloc[row, 4], df_lotes.iloc[row, 5], 
                                                df_lotes.iloc[row, 6], df_lotes.iloc[row, 7], df_lotes.iloc[row, 8], df_lotes.iloc[row, 9])
        return lotes 

    def poblar_uvas(self, path): 
        uvas = {}
        df_uvas = pd.read_excel(path, sheet_name='uvas', encoding="utf-8", usecols='A:G', 
                                dtype={'Uva': str, 'nu': int, 'min': float, 'max': float, 'brix optimo': float, 
                                        'q[t-7]': float, 'q[t+7]': float}) 
        for row in range(df_uvas['Uva'].count()): 
            uvas[df_uvas.iloc[row, 0]] = Uva(df_uvas.iloc[row, 0], df_uvas.iloc[row, 1], df_uvas.iloc[row, 2], 
                                            df_uvas.iloc[row, 3], df_uvas.iloc[row, 4], df_uvas.iloc[row, 5],
                                            df_uvas.iloc[row, 6])
        return uvas       
    
    def poblar_vinos(self, path): 
        vinos = {}
        df_vinos = pd.read_excel(path, sheet_name='vinos', encoding="utf-8", usecols='A:E', 
                                dtype={'Vino Tipo': str, 'Dist': str, 'media': float, 'dst': float, 'volumen': int})
        for row in range(df_vinos['Vino Tipo'].count()): 
            vinos[df_vinos.iloc[row, 0]] = Vino(df_vinos.iloc[row, 0], df_vinos.iloc[row, 1], df_vinos.iloc[row, 2], 
                                            df_vinos.iloc[row, 3], df_vinos.iloc[row, 4])
        return vinos 
    
    def poblar_recetas(self, path):
        recetas={}
        df_recetas = pd.read_excel(path, sheet_name='recetas', encoding="utf-8", usecols='A:J',  
                                                    dtype={'k':str,'m':int,'J1':float,'J2':float,'J3':float,'J4':float,'J5':float,'J6':float,'J7':float,'J8':float})
        for row in range(df_recetas['k'].count()):
            recetas[df_recetas.iloc[row, 0], df_recetas.iloc[row, 1]]= Receta(df_recetas.iloc[row, 0], df_recetas.iloc[row, 1], df_recetas.iloc[row, 2], df_recetas.iloc[row, 3],
                                            df_recetas.iloc[row, 4],df_recetas.iloc[row, 5], df_recetas.iloc[row, 6], df_recetas.iloc[row, 7], df_recetas.iloc[row, 8],df_recetas.iloc[row, 9])
        return recetas
    
    def poblar_estanques(self, path):
        estanques={}
        df_estanques= pd.read_excel(path, sheet_name='estanques',encoding="utf-8", usecols='A:D', 
                                                    dtype={'TK':str,'#':int,'cap(m3)':int,'(m3)':int})
        for row in range(df_estanques['TK'].count()):
            estanques[df_estanques.iloc[row,0]]=Estanque(df_estanques.iloc[row, 0], df_estanques.iloc[row, 1], df_estanques.iloc[row, 2], 
                                            df_estanques.iloc[row, 3])
        return estanques

class Lote:
    def __init__(self, codigo, tipo_u, tn, opt, p_01, p_11, dist, precio, t_hasta_ferm, nu):
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
        self.nu = nu
        self.dias_lluvia = {"antes": 0, "despues": 0}
        self.lluvias = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def calidad_max(self, dia): 
        if self.tipo_u == 'J_1': 
            return -((dia**2)/490) + dia/140 + 1
        elif self.tipo_u == 'J_2': 
            return -3*((dia**2)/1960) + dia/1400 + 1
        elif self.tipo_u == 'J_3': 
            return -9*((dia**2)/4900) + dia/700 + 1
        elif self.tipo_u == 'J_4': 
            return -19*((dia**2)/9800) + dia/280 + 1
        elif self.tipo_u == 'J_5': 
            return 1-(dia**2)/980
        elif self.tipo_u == 'J_6': 
            return -3*((dia**2)/1400)+ dia/1400 + 1
        elif self.tipo_u == 'J_7': 
            return -13*((dia**2)/9800) + dia/1400 + 1
        elif self.tipo_u == 'J_8': 
            return -17*((dia**2)/9800) + dia/280 + 1 
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
            costo= (self.precio/(self.calidad_max(rango)-llovio*0.1 - (1 - math.exp(-self.tiempo/self.nu))) - self.precio)* self.tn*1000
            print("LOTE: {}\n".format(self.codigo))
            print("DIA: {}\n".format(dia))
            print("RANGO: {}".format(rango))
            print("CALIDAD MAX: {}\n".format(self.calidad_max(rango)))
            print("PERDIDA DE CALIDAD: {}".format(1-math.exp(-self.tiempo/self.nu)))
            print("LLUVIAS: {}".format(llovio))
            print("CALIDAD TOTAL: {}".format(self.calidad_max(rango)-llovio*0.1 - (1-math.exp(-self.tiempo/self.nu))))
            print("COSTO: {}".format(costo))
            return costo*0.000000000001
        else: 
            return 1000000000000
            print("entre -.-")
    
    def p_alcoholico(self, dia):
        if self.tipo_u == 'J_1':
            nu= 100
        elif self.tipo_u == 'J_2':
            nu= 85
        elif self.tipo_u == 'J_3':
            nu= 50
        elif self.tipo_u == 'J_4':
            nu= 55    
        elif self.tipo_u == 'J_5':
            nu= 75
        elif self.tipo_u == 'J_6':
            nu= 60
        elif self.tipo_u == 'J_7':
            nu= 65
        elif self.tipo_u == 'J_8':
            nu= 90

        if dia == self.opt-7:
            calidad_max= self.a7
        elif dia == self.opt-6:
            calidad_max= self.a6
        elif dia == self.opt-5:
            calidad_max= self.a5
        elif dia == self.opt-4:
            calidad_max= self.a4
        elif dia == self.opt-3:
            calidad_max= self.a3
        elif dia == self.opt-2:
            calidad_max= self.a2
        elif dia == self.opt-1:
            calidad_max= self.a1
        elif dia == self.opt:
            calidad_max= self.a0
        elif dia == self.opt+1:
            calidad_max= self.d1
        elif dia == self.opt+2:
            calidad_max= self.d2
        elif dia == self.opt+3:
            calidad_max= self.d3
        elif dia == self.opt+4:
            calidad_max= self.d4
        elif dia == self.opt+5:
            calidad_max= self.d5
        elif dia == self.opt+6:
            calidad_max= self.d6
        elif dia == self.opt+7:
            calidad_max= self.d7
        else:
            calidad_max=0.000001 #es para que no se caiga, no debería comprar estos días igual por la restricción.
        potencial_alcholico= 0.62*nu*calidad_max
        return potencial_alcholico
        
                                
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
        """
        self.tipo = tipo 
        self.precio_dstbn = precio_dstbn 
        self.precio_media = precio_media
        self.precio_dst = precio_dst 
        self.volumen = volumen

class Receta:
    def __init__(self, tipo_vino, id_receta, J1, J2, J3, J4, J5, J6, J7, J8):
        self.tipo_vino= tipo_vino
        self.id= id_receta
        self.J1 = J1
        self.J2 = J2
        self.J3 = J3
        self.J4 = J4
        self.J5 = J5
        self.J6 = J6
        self.J7 = J7
        self.J8 = J8

class Estanque:
    def __init__(self, tipo_estanque, cantidad, capacidad_u, capacidad_t):
        self.tipo = tipo_estanque
        self.cantidad = cantidad
        self.capacidad_unitaria = capacidad_u
        self.capacidad_total = capacidad_t



