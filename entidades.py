class Procesamiento: 
    def __init__(self, masa_inicial): 
        self.masa_entrada = masa_inicial #kg
        self.masa_en_molienda = 0 #kg
        self.produccion_molienda = 0 #kg
        self.masa_en_prensado = 0 #kg
        self.produccion_prensado = 0 #L
        self.volumen_en_clarificacion = 0 #L
        self.produccion_clarificacion = 0 #L
        
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

    def entrada_masa(self,masa):
        self.masa_entrada += masa

    def molienda(self):
        #1h de molienda
        #Inicio de la hora
        if self.masa_entrada <= (self.cap_max_molienda * self.eq_molienda)-self.masa_en_molienda:
            self.masa_en_molienda += self.masa_entrada
            self.masa_entrada = 0
        else:
            self.masa_entrada -= (self.cap_max_molienda * self.eq_molienda)-self.masa_en_molienda
            self.masa_en_molienda = self.cap_max_molienda * self.eq_molienda
        #Termino de la hora
        self.masa_en_molienda *= (1-self.merma_molienda)
        if self.masa_en_molienda >= self.caudal_molienda * self.eq_molienda:
            self.produccion_molienda += self.caudal_molienda * self.eq_molienda
            self.masa_en_molienda -= self.caudal_molienda * self.eq_molienda
        else:
            self.produccion_molienda += self.masa_en_molienda 
            self.masa_en_molienda = 0

    def prensado(self):
        #1h de prensado
        #Inicio de la hora
        if self.produccion_molienda <= (self.cap_max_prensado * self.eq_prensado)- self.masa_en_prensado:
            self.masa_en_prensado += self.produccion_molienda
            self.produccion_molienda = 0
        else:
            self.produccion_molienda -= (self.cap_max_prensado * self.eq_prensado)-self.masa_en_prensado
            self.masa_en_prensado = self.cap_max_prensado * self.eq_prensado
        #Termino de la hora
        self.masa_en_prensado *= (1-self.merma_prensado) #Ahora son litros
        if self.masa_en_prensado >= self.caudal_prensado * self.eq_prensado:
            self.produccion_prensado += self.caudal_prensado * self.eq_prensado
            self.masa_en_prensado -= self.caudal_prensado * self.eq_prensado
        else:
            self.produccion_prensado += self.masa_en_prensado
            self.masa_en_prensado = 0

    def clarificacion(self):
        #1h de clarificacion
        #Inicio de la hora
        if self.produccion_prensado <= (self.cap_max_clarificacion * self.eq_clarificacion)-self.volumen_en_clarificacion:
            self.volumen_en_clarificacion += self.produccion_prensado
            self.produccion_prensado = 0
        else:
            self.produccion_prensado -= (self.cap_max_clarificacion * self.eq_clarificacion)-self.volumen_en_clarificacion
            self.volumen_en_clarificacion = self.cap_max_clarificacion * self.eq_clarificacion
        #Termino de la hora
        self.volumen_en_clarificacion *= (1-self.merma_clarificacion)
        if self.volumen_en_clarificacion >= self.caudal_clarificacion * self.eq_clarificacion:
            self.produccion_clarificacion += self.caudal_clarificacion * self.eq_clarificacion
            self.volumen_en_clarificacion -= self.caudal_clarificacion * self.eq_clarificacion
        else:
            self.produccion_clarificacion += self.volumen_en_clarificacion
            self.volumen_en_clarificacion = 0

    def fermentacion(self):
        pass

    def mezcla(self): 
        pass 

class Lote:
    def __init__(self, codigo, tipo_u, tn, opt, p_01, p_11, dist, precio):
        """ 
        codigo: codigo de lote 
        tipo_u: tipo de uva que genera el lote
        tn: toneladas de produccion
        opt: dia optimo de cosecha 
        p_01: probabilidad de que en el lote llueva si ayer no llovio
        p_11: probabilidad de que en el lote llueva si ayer llovio
        dist: distancia que existe entre el lote y la planta 
        precio: precio de la uva por kilogramo 
        """
        self.codigo = codigo
        self.tipo_u = tipo_u 
        self.tn = tn 
        self.opt = opt
        self.p_01 = p_01
        self.p_11 = p_11 
        self.dist = dist 
        self.precio = precio 
    
         
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

class Vino: 
    def __init__(self, tipo, precio_dstbn, precio_media, precio_dst, volumen):
        """
        precio_media: la media del precio del vino 
        precio_dst: desviacion estandar del precio del vino 
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



