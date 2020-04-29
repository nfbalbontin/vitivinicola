class Procesamiento: 
    def __init__(self): 
        pass

    def molienda(self):
        pass

    def prensado(self):
        pass

    def clarificacion(self):
        pass

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
    def __init__(self, nu, min_ferm, max_ferm, brix):
        """
        nu: parametro de perdida de calidad 
        min: minimo tiempo de fermentacion 
        max: maximo tiempo de fermentacion 
        brix: el brix de cada uva 
        """
        self.nu = nu 
        self.min = min_ferm
        self.max = max_ferm 
        self.brix = brix 

class Vino: 
    def __init__(self, precio_media, precio_dst, volumen):
        """
        precio_media: la media del precio del vino 
        precio_dst: desviacion estandar del precio del vino 
        volumen: volumen demandado por el vino
        """
        self.precio_media = precio_media
        self.precio_dst = precio_dst 
        self.volumen = volumen


