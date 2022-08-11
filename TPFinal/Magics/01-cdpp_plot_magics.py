from IPython.core.magic import (Magics, magics_class, line_magic)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from pathlib import Path
import pandas as pd
import os

# definimos los nombres de las columnas en los dataframes de pandas
TIME_COL = 'time'
TIME_COL2 = 'time2'
PORT_COL = 'port'
VALUE_COL = 'value'
MESSAGE_TYPE_COL = 'message_type'
MODEL_ORIGIN_COL = 'model_origin'
MODEL_DEST_COL = 'model_dest'


def parse_value(value: str):
    is_list = value.strip().startswith("[") and value.strip().endswith("]")
    if is_list:
        return tuple(float(num) for num in value.replace('[', '').replace(']', '').split(', '))
    return float(value)


def time_to_secs(time):
    h, m, s, ms, r = time.split(':')
    return float(h) * 60 * 60. + float(m) * 60. + float(s) + float(ms) / 1000. + float(r) / 1000.


df_converters = {
    VALUE_COL: parse_value,
    TIME_COL: time_to_secs
}


@magics_class
class CDPPPlotMagics(Magics):
    @magic_arguments()
    @argument("path_to_out_ev", type=str,
              help="Path al archivo de salida .out generado por una ejecución del simulador.")
    @line_magic
    def parser_out_ev(self, line: str):
        args = parse_argstring(CDPPPlotMagics.parser_log, line)
        path = Path(args.path_to_out_ev)
        if not path.exists():
            print(f"Error: File {line} does not exists.")
        df = pd.read_csv(path,
                         delimiter=r'(?<!,)\s+',
                         engine='python',  # C engine doesnt work for regex
                         converters=df_converters,
                         names=[TIME_COL, PORT_COL, VALUE_COL]
                         )
        return df

    @magic_arguments()
    @argument("path_to_log_file", type=str,
              help="Path al archivo de salida .log generado por una ejecución del simulador.")
    @line_magic
    def parser_log(self, line: str):
        args = parse_argstring(CDPPPlotMagics.parser_log, line)
        path = Path(args.path_to_log_file)
        if not path.exists():
            print(f"Error: File {line} does not exists.")

        log_file_per_component = {}
        parsed_logs = {}

        # separo cada log file
        with open(path, 'r') as main_log_file:
            main_log_file.readline()  # Ignore first line
            log_dir = os.path.dirname(path)
            for line in main_log_file:
                name, path = line.strip().split(' : ')
                log_file_per_component[name] = (path if os.path.isabs(path) else
                                                log_dir + '/' + path.split('/')[-1])

        # parseo cada log file
        for log_name, filename in log_file_per_component.items():
            parsed_logs[log_name] = pd.read_csv(filename,
                                                delimiter=r' /\s+',
                                                engine='python',  # C engine doesnt work for regex
                                                names=['1', '2', '3', '4', '5', '6', '7', '8']
                                                # nombre genérico pues varía el contenido de la fila según tipo de mensaje
                                                )
        return parsed_logs


if __name__ == '__main__':
    from IPython import get_ipython
    get_ipython().register_magics(CDPPPlotMagics)
