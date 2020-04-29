from entidades import * 
import sys ####borrar
sys.path.append('C:/Users/Carolina Stuardo/AppData/Local/Programs/Python/Python36/Lib/site-packages')##
import pandas as pd


def poblar_lotes(path): 
    lotes = {}
    df_lotes = pd.read_excel(path, sheet_name='lotes', encoding="utf-8", usecols='A:H', dtype={'Lote COD': str, 'Tipo UVA': str, 'Tn': int, 'Dia optimo cosecha': int, 'p_01': float, 'p_11': float, 'km a planta': int, '$/kg': float})
    print(df_lotes.iloc[0,0])
    for row in range(df_lotes['Lote COD'].count()): 
        lotes[df_lotes.iloc[row, 0]] = Lote(df_lotes.iloc[row, 0], df_lotes.iloc[row, 1], df_lotes.iloc[row, 2], 
                                            df_lotes.iloc[row, 3], df_lotes.iloc[row, 4], df_lotes.iloc[row, 5], 
                                            df_lotes.iloc[row, 6], df_lotes.iloc[row, 7])
    return lotes 

def poblar_uvas(path): 
    uvas = {}
    df_uvas = pd.read_excel(path, sheet_name='uvas', encoding="utf-8", usecols='A:G', 
                             dtype={'Uva': str, 'nu': int, 'min': float, 'max': float, 'brix optimo': float, 
                                    'q[t-7]': float, 'q[t+7]': float}) 
    print(df_uvas.iloc[0,0])
    for row in range(df_uvas['Uva'].count()): 
        uvas[df_uvas.iloc[row, 0]] = Uva(df_uvas.iloc[row, 0], df_uvas.iloc[row, 1], df_uvas.iloc[row, 2], 
                                         df_uvas.iloc[row, 3], df_uvas.iloc[row, 4], df_uvas.iloc[row, 5],
                                         df_uvas.iloc[row, 6])
    return uvas                     

def poblar_vinos(path): 
    vinos = {}
    df_vinos = pd.read_excel(path, sheet_name='vinos', encoding="utf-8", usecols='A:E', 
                             dtype={'Vino Tipo': str, 'Dist': str, 'media': float, 'dst': float, 'volumen': int})
    print(df_vinos.iloc[0,0])
    for row in range(df_vinos['Vino Tipo'].count()): 
        vinos[df_vinos.iloc[row, 0]] = Vino(df_vinos.iloc[row, 0], df_vinos.iloc[row, 1], df_vinos.iloc[row, 2], 
                                         df_vinos.iloc[row, 3], df_vinos.iloc[row, 4])
    return vinos 

def poblar_recetas(path):
    recetas={}
    df_recetas = pd.read_excel(path, sheet_name='recetas', encoding="utf-8", usecols='A:J',  
                                                dtype={'k':str,'m':int,'J1':float,'J2':float,'J3':float,'J4':float,'J5':float,'J6':float,'J7':float,'J8':float})
    for row in range(df_recetas['k'].count()):
        recetas[df_recetas.iloc[row, 0], df_recetas.iloc[row, 1]]= Receta(df_recetas.iloc[row, 0], df_recetas.iloc[row, 1], df_recetas.iloc[row, 2], df_recetas.iloc[row, 3],
                                          df_recetas.iloc[row, 4],df_recetas.iloc[row, 5], df_recetas.iloc[row, 6], df_recetas.iloc[row, 7], df_recetas.iloc[row, 8],df_recetas.iloc[row, 9])
    return recetas

def poblar_estanques(path):
    estanques={}
    df_estanques= pd.read_excel(path, sheet_name='estanques',encoding="utf-8", usecols='A:D', 
                                                dtype={'TK':str,'#':int,'cap(m3)':int,'(m3)':int})
    for row in range(df_estanques['TK'].count()):
        estanques[df_estanques.iloc[row,0]]=Estanque(df_estanques.iloc[row, 0], df_estanques.iloc[row, 1], df_estanques.iloc[row, 2], 
                                         df_estanques.iloc[row, 3])
    return estanques


poblar_lotes('docs/vitivinicola.xlsx')
poblar_uvas('docs/vitivinicola.xlsx')
poblar_vinos('docs/vitivinicola.xlsx')
poblar_recetas('docs/vitivinicola.xlsx')
poblar_estanques('docs/vitivinicola.xlsx')