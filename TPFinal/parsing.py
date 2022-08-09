# estoy ejecutando esto como %run parsing.py al principio del notebook
# este archivo debe estar en el mismo directorio que el notebook en cuestion
# falta probar de colocarlo en otro lado y usar %run /path/to/parsing.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# definimos los nombres de las columnas en los dataframes de pandas
TIME_COL = 'time'
TIME_COL2 = 'time2'
PORT_COL = 'port'
VALUE_COL = 'value'
MESSAGE_TYPE_COL = 'message_type'
MODEL_ORIGIN_COL = 'model_origin'
MODEL_DEST_COL = 'model_dest'

#conversion de valor a float o tupla
def parse_value(value: str):
    is_list = value.strip().startswith("[") and value.strip().endswith("]")
    if is_list:
        return tuple(float(num) for num in value.replace('[', '').replace(']', '').split(', '))
    return float(value)

# conversion tiempo h:m:s:ms:r a segundos
def time_to_secs(time):
    h, m, s, ms, r = time.split(':')
    return float(h)*60*60. + float(m)*60. + float(s) + float(ms)/1000. + float(r)/1000.

# dict para convertir valores de estas columnas al parsear
df_converters = {
        VALUE_COL: parse_value,
        TIME_COL: time_to_secs
    }

# metodo para parsear archivos .out y .ev 
def parser_out_ev(path_to_out_ev):   
    df = pd.read_csv(path_to_out_ev,
                     delimiter=r'(?<!,)\s+',
                     engine='python',  # C engine doesnt work for regex
                     converters=df_converters,
                     names=[TIME_COL, PORT_COL, VALUE_COL]
                    )
    return df

# metodo para parsear archivos .log
def parser_log(path_to_log_file):
    
    log_file_per_component = {}
    parsed_logs = {}

    # separo cada log file
    with open(path_to_log_file, 'r') as main_log_file:
        main_log_file.readline()  # Ignore first line
        log_dir = os.path.dirname(path_to_log_file)
        for line in main_log_file:
            name, path = line.strip().split(' : ')
            log_file_per_component[name] = (path if os.path.isabs(path) else
                                            log_dir + '/' + path.split('/')[-1])

    # parseo cada log file
    for logname, filename in log_file_per_component.items():
        parsed_logs[logname] = pd.read_csv(filename,
                                           delimiter=r' /\s+',
                                           engine='python',  # C engine doesnt work for regex
                                           names=['1','2','3','4','5','6','7','8'] # nombre generico pues varia el contenido de la fila segun tipo de mensaje
                                          )
    return parsed_logs


# metodo para filtrar dataframes de logs segun tipo de mensaje
# se renombran las columnas segun tipo de mensaje
def filter_and_name(df,tipo):
    
    # filtro por tipo indicado
    filtered_df = df[df['3'] == tipo].copy()
    col_names=[]
    
    if(tipo == 'D'):       
        col_names=[0,1,MESSAGE_TYPE_COL,TIME_COL,MODEL_ORIGIN_COL,TIME_COL2,MODEL_DEST_COL,8]
        
    if((tipo == 'Y') or (tipo == 'X')):        
        col_names=[0,1,MESSAGE_TYPE_COL,TIME_COL,MODEL_ORIGIN_COL,PORT_COL,VALUE_COL,MODEL_DEST_COL]
        
    if((tipo == 'I') or (tipo == '*') or (tipo == '@')):
        col_names=[0,1,MESSAGE_TYPE_COL,TIME_COL,MODEL_ORIGIN_COL,MODEL_DEST_COL,7,8]
        
    # nombro las columnas
    filtered_df.columns = col_names
    
    filtered_df.loc[:,TIME_COL] = filtered_df.loc[:,TIME_COL].apply(time_to_secs)
    
    #if(TIME_COL2 in col_names):
     #   filtered_df[TIME_COL2] = filtered_df[TIME_COL2].apply(time_to_secs)
        
    if(VALUE_COL in col_names):
        filtered_df[VALUE_COL] = filtered_df[VALUE_COL].apply(parse_value)
    
    # elimino columnas sin informacion
    to_drop = [0,1,7,8]
    for i in to_drop:
        if i not in col_names:
            to_drop.remove(i)
    
    return filtered_df.drop(to_drop, axis=1)

# METODOS PARA GRAFICAR

# grafico comun
def do_chart_plot(df,ports):
    
    plt.figure(figsize=(10,5))
    
    # plotea valores de los puertos indicados por parametro
    if len(ports)!=0:
        for p in ports:
            df_port = df.loc[df[PORT_COL]==p]
            y_values = df_port[VALUE_COL]
            x_values = df_port[TIME_COL]
            plt.plot(x_values, y_values,marker='x',label=p)
            plt.legend()
    else:
        x_values = df[TIME_COL]
        if(type(df[VALUE_COL][0])== tuple):
            y_values,_,_ = df[VALUE_COL].str
        else:
            y_values = df[VALUE_COL].tolist() # convierto de serie de pandas a lista
        plt.plot(x_values, y_values, marker='x')
        
    plt.grid(True)
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Valor')
    return

# grafico tipo step
def do_chart_step(df,ports):
    plt.figure(figsize=(10,5))
    
    # plotea valores de los puertos indicados por parametro
    if len(ports)!=0:
        for p in ports:
            df_port = df.loc[df[PORT_COL]==p]
            y_values = df_port[VALUE_COL]
            x_values = df_port[TIME_COL]
            plt.plot(x_values, y_values,marker='o',label=p)
            plt.legend()
    else:
        x_values = df[TIME_COL]
        if(type(df[VALUE_COL][0])== tuple):
            y_values,_,_ = df[VALUE_COL].str
        else:
            y_values = df[VALUE_COL].tolist() # convierto de serie de pandas a lista
        plt.step(x_values, y_values, marker='o')
        
    plt.grid(True)
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Valor')
    return

# grafico tipo stem
def do_chart_stem(df,ports):
    
    plt.figure(figsize=(10,5))
    i = 1
    
    # plotea valores de los puertos indicados por parametro
    for p in ports:
        df_port = df.loc[df[PORT_COL]==p]
        y_values = df_port[VALUE_COL]
        x_values = df_port[TIME_COL]
        color = 'C'+str(i)+'o'
        i = i+1
        plt.stem(x_values, y_values,':k',color,use_line_collection=True,label=p)
    
    plt.grid(True)
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Valor')
    plt.legend()
    return

# metodo general para graficar
# asumo que es valor en funcion de tiempo
# doy opcion a especificar de que puertos quiere graficarse (caso logs)
def do_chart(df, chart="plot", ports=[]):
    if(chart == "plot"):
        do_chart_plot(df,ports)
    if(chart == "step"):
        do_chart_step(df,ports)
    if(chart == "stem"):
        do_chart_stem(df,ports)
    return