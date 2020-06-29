
import pandas as pd
import json, math
from poblacion_datos import poblar_lotes, poblar_uvas, poblar_recetas, poblar_vinos, poblar_estanques
from itertools import chain

uvas = poblar_uvas("docs/vitivinicola.xlsx")
coleccion_estanques = poblar_estanques("docs/vitivinicola.xlsx")
lotes = poblar_lotes("docs/vitivinicola.xlsx")

J = [uva for uva in uvas]
D = [i for i in range(-6, 93)]

def open_dicts(path):
  with open(path) as df: 
    content = df.read()
    return json.loads(content)


def gen_posibles_estanques():
  values = {}
  valores = {}
  est = {'20': ['T1',1], '10': ['T2',2], '15': ['T3', 3]}
  for i in est: 
    values[i] = [[est[i][0]]]
    valores[i] = [[est[i][1] + 1]]
    for j in est: 
      value1 = str(int(i)+int(j))
      valor1 = est[i][1] + est[j][1] + 2
      if value1 not in values: 
        values[value1] = [[est[i][0], est[j][0]]]
        valores[value1] = [[valor1]]
      elif valor1 not in valores[value1]:
        values[value1].append([est[i][0], est[j][0]])
        valores[value1].append(valor1)
      for k in est: 
        value2 = str(int(i)+int(j)+int(k))
        valor2 = est[i][1] + est[j][1] + est[k][1] + 3
        if value2 not in values: 
          values[value2] = [[est[i][0], est[j][0], est[k][0]]]
          valores[value2] = [[valor2]]
        elif valor2 not in valores[value2]:
          values[value2].append([est[i][0], est[j][0], est[k][0]])
          valores[value2].append(valor2)
        for m in est: 
          value3 = str(int(i)+int(j)+int(k)+int(m))
          valor3 = est[i][1] + est[j][1] + est[k][1] + est[m][1] + 4
          if value3 not in values: 
            values[value3] = [[est[i][0], est[j][0], est[k][0], est[m][0]]]
            valores[value3] = [[valor3]]
          elif valor3 not in valores[value3]: 
            values[value3].append([est[i][0], est[j][0], est[k][0], est[m][0]])
            valores[value3].append(valor3)
          for n in est: 
            value4 = str(int(i)+int(j)+int(k)+int(m)+int(n))
            valor4 = est[i][1] + est[j][1] + est[k][1] + est[m][1] + est[n][1] + 5
            if  int(value4) <= 80 and value4 not in values: 
              values[value4] = [[est[i][0], est[j][0], est[k][0], est[m][0], est[n][0]]]
              valores[value4] = [[valor4]]
            elif int(value4) <= 80 and valor4 not in valores[value4]: 
              values[value4].append([est[i][0], est[j][0], est[k][0], est[m][0], est[n][0]])
              valores[value4].append(valor4)
            for o in est: 
              value5 = str(int(i)+int(j)+int(k)+int(m)+int(n)+int(o))
              valor5 = est[i][1] + est[j][1] + est[k][1] + est[m][1] + est[n][1] + est[o][1] + 6
              if int(value5) <= 80 and value5 not in values: 
                values[value5] = [[est[i][0], est[j][0], est[k][0], est[m][0], est[n][0], est[o][0]]]
                valores[value5] = [[valor5]]
              elif int(value5) <= 80 and valor5 not in valores[value5]: 
                values[value5].append([est[i][0], est[j][0], est[k][0], est[m][0], est[n][0], est[o][0]])
                valores[value5].append(valor5)
              for p in est: 
                value6 = str(int(i)+int(j)+int(k)+int(m)+int(n)+int(o)+int(p))
                valor6 = est[i][1] + est[j][1] + est[k][1] + est[m][1] + est[n][1] + est[o][1] + est[p][1] + 7
                if int(value6) <= 80 and value6 not in values: 
                  values[value6] = [[est[i][0], est[j][0], est[k][0], est[m][0], est[n][0], est[o][0], est[p][0]]]
                  valores[value6] = [[valor6]]
                elif int(value6) <= 80 and valor6 not in valores[value6]: 
                  values[value6].append([est[i][0], est[j][0], est[k][0], est[m][0], est[n][0], est[o][0], est[p][0]])
                  valores[value6].append(valor6)
                for q in est: 
                  value7 = str(int(i)+int(j)+int(k)+int(m)+int(n)+int(o)+int(p)+int(q))
                  valor7 = est[i][1] + est[j][1] + est[k][1] + est[m][1] + est[n][1] + est[o][1] + est[p][1] + est[q][1] + 8
                  if int(value7) <= 80 and value7 not in values: 
                    values[value7] = [[est[i][0], est[j][0], est[k][0], est[m][0], est[n][0], est[o][0], est[p][0], est[q][0]]]
                    valores[value7] = [[valor7]]
                  elif int(value7) <= 80 and valor7 not in valores[value7]: 
                    values[value7].append([est[i][0], est[j][0], est[k][0], est[m][0], est[n][0], est[o][0], est[p][0], est[q][0]])
                    valores[value7].append(valor7)
  values_dict = {}
  for val in values: 
    values_dict[val] = []
    pos = 0
    for lista in values[val]: 
      values_dict[val].append({})
      for item in lista: 
        if item not in values_dict[val][pos]:
          values_dict[val][pos][item] = 1
        else: 
          values_dict[val][pos][item] += 1
      pos += 1
  return values_dict

def set_estanque(value, lote, faker=False): 
  print(value)
  posibles_estanques = pos_estanques[value]
  green_light = 0
  for dict_estanques in posibles_estanques: 
    for estanque in dict_estanques: 
      if coleccion_estanques[estanque].disponibilidad >= dict_estanques[estanque]: 
        green_light += 1
    if green_light == len(dict_estanques): 
      for estanque in dict_estanques: 
        coleccion_estanques[estanque].fermentar(dict_estanques[estanque], lote)
      return True
    else: 
      green_light = 0
  if green_light == 0 and int(value) < 80 and faker==False: 
    set_estanque(str(int(value) + 5), lote, False)
  if green_light == 0 and (int(value) == 80 or faker==True): 
    if int(value) - 5 == 5: 
      return False
    set_estanque(str(int(value) -5), lote, True)


lote_dict = open_dicts('docs/lotes_dict.txt')
rep_dict = open_dicts('docs/recetas_dict.txt')
vino_dict = open_dicts('docs/vinos_dict.txt')
pos_estanques = gen_posibles_estanques()


for dia in D: 
  print("----------------------------DIA {}------------------------------".format(dia))
  for tipo in coleccion_estanques: 
    pos = 0
    for estanque in coleccion_estanques[tipo].estanques: 
      if estanque.disponible == False: 
        estanque.tiempo -= 1
      if estanque.tiempo == 0: 
        estanque.tiempo = 9
        estanque.disponible = True
        print("ESTANQUE {0}{1} DESOCUPADO".format(tipo, pos))
      pos += 1 
  for l in lote_dict: 
    if int(lote_dict[l]['dia_c']) == dia: 
      print("COSECHA LOTE {}".format(l))
      print("CANTIDAD {}".format(str(math.ceil(math.ceil(int(lote_dict[l]['cantidad'])/1000)/5)*5)))
      est = set_estanque(str(math.ceil(math.ceil(int(lote_dict[l]['cantidad'])/1000)/5)*5), lote_dict[l])
      if not est: 
        print("NO SE PUDO ASIGNAR UN ESTANQUE")







      
     
