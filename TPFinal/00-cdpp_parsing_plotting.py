import pandas
import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Dict, Optional, List, Callable, Union, Tuple

# definimos los nombres de las columnas en los dataframes de pandas
TIME_COL: str = 'time'
TIME_COL2: str = 'time2'
PORT_COL: str = 'port'
VALUE_COL: str = 'value'
MESSAGE_TYPE_COL: str = 'message_type'
MODEL_ORIGIN_COL: str = 'model_origin'
MODEL_DEST_COL: str = 'model_dest'


# conversion de valor a float o tupla
def parse_value(value: str) -> Union[float, Tuple[float]]:
    """
    Parsea un string y devuelve un float o una lista de floats
    """
    is_list = value.strip().startswith("[") and value.strip().endswith("]")
    if is_list:
        return tuple(float(num) for num in value.replace('[', '').replace(']', '').split(', '))
    return float(value)


def time_to_secs(time: str) -> float:
    """
    Parsea un string con tiempos en el formato utilizado por el simulador y lo convierte a segundos.
    """
    h, m, s, ms, r = time.split(':')
    return float(h) * 60 * 60. + float(m) * 60. + float(s) + float(ms) / 1000. + float(r) / 1000.


# dict para convertir valores de estas columnas al parsear
df_converters: Dict[str, Callable] = {
    VALUE_COL: parse_value,
    TIME_COL: time_to_secs
}


def parser_out_ev(path_to_out_ev: str) -> pandas.DataFrame:
    """
    Método para parsear archivos .out y .ev.

    Parameters
    ----------
    path_to_out_ev : str
        String que indica el path donde encontrar un archivo .out o un archivo .ev.

    Returns
    --------
    pandas.DataFrame
        Un pandas.DataFrame que contiene la información del archivo de forma tabulada.
    """
    df = pd.read_csv(path_to_out_ev,
                     delimiter=r'(?<!,)\s+',
                     engine='python',  # C engine doesnt work for regex
                     converters=df_converters,
                     names=[TIME_COL, PORT_COL, VALUE_COL]
                     )
    return df


def parser_log(path_to_log_file: str) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Método para parsear archivos .log.

    Parameters
    ----------
    path_to_log_file : str
        String que indica el path donde encontrar un archivo .log principal y todos los archivos de log a los que este
        referencie.

    Returns
    --------
    Optional[Dict[str, pd.DataFrame]]
        Si no había información en los archivos .log, devuelve None.
        Caso contrario, un diccionario de strings a DataFrame de pandas, donde las claves son los nombres de los
        archivos de log y los valores son la información que contiene dicho log en forma tabulada.
    """

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
                                           names=['1', '2', '3', '4', '5', '6', '7', '8']
                                           # nombre generico pues varía el contenido de la fila segun tipo de mensaje
                                           )
    return parsed_logs


def filter_and_name(df: pandas.DataFrame, tipo: str) -> pandas.Series:
    """
    Método para filtrar dataframes de logs según tipo de mensaje
    Se renombran las columnas según tipo de mensaje.

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe de pandas sobre el que se realiza el filtrado

    tipo: str
        String que indica el tipo de mensaje por el que queremos filtrar al dataframe

    Returns
    -------
    pandas.Series
        Serie de valores de pandas, contiene los datos filtrados.
    """

    # filtro por tipo indicado
    filtered_df = df[df['3'] == tipo].copy()
    col_names = []

    if tipo == 'D':
        col_names = [0, 1, MESSAGE_TYPE_COL, TIME_COL, MODEL_ORIGIN_COL, TIME_COL2, MODEL_DEST_COL, 8]

    if (tipo == 'Y') or (tipo == 'X'):
        col_names = [0, 1, MESSAGE_TYPE_COL, TIME_COL, MODEL_ORIGIN_COL, PORT_COL, VALUE_COL, MODEL_DEST_COL]

    if (tipo == 'I') or (tipo == '*') or (tipo == '@'):
        col_names = [0, 1, MESSAGE_TYPE_COL, TIME_COL, MODEL_ORIGIN_COL, MODEL_DEST_COL, 7, 8]

    # nombro las columnas
    filtered_df.columns = col_names

    filtered_df.loc[:, TIME_COL] = filtered_df.loc[:, TIME_COL].apply(time_to_secs)

    # if(TIME_COL2 in col_names):
    #   filtered_df[TIME_COL2] = filtered_df[TIME_COL2].apply(time_to_secs)

#    if VALUE_COL in col_names:
 #       filtered_df[VALUE_COL] = filtered_df[VALUE_COL].apply(parse_value)

    # elimino columnas sin información
    to_drop = [0, 1, 7, 8]
    l = []
    
    for i in to_drop:
        if i not in col_names:
            l.append(i)
            
    for i in l:
    	to_drop.remove(i)

    return filtered_df.drop(to_drop, axis=1)



# MÉTODOS PARA GRAFICAR

def do_chart_plot(df: pandas.DataFrame, ports: List[str]) -> None:
    """
    Genera y muestra un gráfico de línea común basado en los datos del dataframe, filtrado por los puertos.

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe con la información a graficar.
    ports: List[str]
        Lista de string que contiene los nombres de los puertos por los que nos interesa graficar.
    """

    plt.figure(figsize=(10, 5))

    # plotea valores de los puertos indicados por parámetro
    if len(ports) != 0:
        for p in ports:
            df_port = df.loc[df[PORT_COL] == p]
            y_values = df_port[VALUE_COL]
            x_values = df_port[TIME_COL]
            plt.plot(x_values, y_values, marker='x', label=p)
            plt.legend()
    else:
        x_values = df[TIME_COL]
        if type(df[VALUE_COL][0]) == tuple:
            y_values, *_ = df[VALUE_COL].str
        else:
            y_values = df[VALUE_COL].tolist()  # convierto de serie de pandas a lista
        plt.plot(x_values, y_values, marker='x')

    plt.grid(True)
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Valor')
    return


# grafico tipo step
def do_chart_step(df: pandas.DataFrame, ports: List[str]) -> None:
    """
    Genera y muestra un gráfico step basado en los datos del dataframe, filtrado por los puertos.

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe con la información a graficar.
    ports: List[str]
        Lista de string que contiene los nombres de los puertos por los que nos interesa graficar.
    """
    plt.figure(figsize=(10, 5))

    # plotea valores de los puertos indicados por parámetro
    if len(ports) != 0:
        for p in ports:
            df_port = df.loc[df[PORT_COL] == p]
            y_values = df_port[VALUE_COL]
            x_values = df_port[TIME_COL]
            plt.plot(x_values, y_values, marker='o', label=p)
            plt.legend()
    else:
        x_values = df[TIME_COL]
        if type(df[VALUE_COL][0]) == tuple:
            y_values, *_ = df[VALUE_COL].str
        else:
            y_values = df[VALUE_COL].tolist()  # convierto de serie de pandas a lista
        plt.step(x_values, y_values, marker='o')

    plt.grid(True)
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Valor')
    return


def do_chart_stem(df: pandas.DataFrame, ports: List[str]) -> None:
    """
    Genera y muestra un gráfico stem basado en los datos del dataframe, filtrado por los puertos.

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe con la información a graficar.
    ports: List[str]
        Lista de string que contiene los nombres de los puertos por los que nos interesa graficar.
    """
    plt.figure(figsize=(10, 5))
    i = 1
    # plotea valores de los puertos indicados por parámetro
    for p in ports:
        df_port = df.loc[df[PORT_COL] == p]
        y_values = df_port[VALUE_COL]
        x_values = df_port[TIME_COL]
        color = 'C' + str(i) + 'o'
        i = i + 1
        plt.stem(x_values, y_values, ':k', color, use_line_collection=True, label=p)

    plt.grid(True)
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Valor')
    plt.legend()


def do_chart(df: pandas.DataFrame, chart: str = "plot", ports: List[str] = []) -> None:
    """
    Método general para graficar.
    Asumo que es valor en función de tiempo.
    Doy opción a especificar de que puertos quiere graficarse (caso logs)

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe que contiene los datos a utilizar para graficar.
    chart: str = "plot"
        String que identifica el tipo de gráfico a realizar. Opciones: plot, step y stem. Por defecto se usa plot.
    ports: List[str] = []
        Lista de strings que contiene los nombres de los puertos por los que se va a filtrar el dataframe.
        De interés para graficar datos de los logs.
        Por defecto, su valor es la lista vacía.
    """
    if chart == "plot":
        do_chart_plot(df, ports)
    if chart == "step":
        do_chart_step(df, ports)
    if chart == "stem":
        do_chart_stem(df, ports)
    return
