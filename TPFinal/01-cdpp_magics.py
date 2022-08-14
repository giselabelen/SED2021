from IPython.core.magic import (Magics, magics_class, line_magic)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from pathlib import Path
from urllib import request
from typing import Dict, List, Optional, Callable
import pandas
import subprocess
import shutil
import zipfile
import os

"""
Colección de funciones magics para facilitar el uso del simulador CDPP en Jupyter Labs.

Para que IPython cargue y utilice las funciones y magics definidos en este archivo, se lo debe colocar en la carpeta"
" ~/.ipython/profile_{NAME}/startup/
donde {NAME} es el nombre del perfil de IPython sobre el cua lse va a trabajar, por defecto es default(profile_default).
"""

URL_CARLETON_MODELS: str = "http://www.sce.carleton.ca/faculty/wainer/wbgraf/samples/"

# definimos los nombres de las columnas en los dataframes de pandas
# TIME_COL: str = 'time'
# TIME_COL2: str = 'time2'
# PORT_COL: str = 'port'
# VALUE_COL: str = 'value'
# MESSAGE_TYPE_COL: str = 'message_type'
# MODEL_ORIGIN_COL: str = 'model_origin'
# MODEL_DEST_COL: str = 'model_dest'


# def parse_value(value: str):
#     """
#     Parsea un string y devuelve un valor o una lista de valores
#     """
#     is_list = value.strip().startswith("[") and value.strip().endswith("]")
#     if is_list:
#         return tuple(float(num) for num in value.replace('[', '').replace(']', '').split(', '))
#     return float(value)
#
#
# def time_to_secs(time):
#     """
#     Parsea un string con tiempos en el formato utilizado por el simulador
#     """
#     h, m, s, ms, r = time.split(':')
#     return float(h) * 60 * 60. + float(m) * 60. + float(s) + float(ms) / 1000. + float(r) / 1000.
#
#
# df_converters: Dict[str, Callable] = {
#     VALUE_COL: parse_value,
#     TIME_COL: time_to_secs
# }

LINE_MAGICS: List[str] = ["lscdpp", "cdpp_run", "drawlog_run", "cdpp_help", "drawlog_help", "cdpp_compile",
                          "cdpp_compile_tools", "cdpp_recompile", "cdpp_unzip", "cdpp_download",
                          "cdpp_download_carleton", "cdpp_copy_to_project", "cdpp_show", "cdpp_set_project",
                          "cdpp_init", "parse_log", "parse_out_ev"]
CELL_MAGICS: List[str] = []


def download_file(url: str, download_file_path: Path):
    """
    Descarga el archivo indicado por la url al destino indicado por download_file_path
    """
    try:
        request.urlretrieve(url, download_file_path)
    except Exception as e:
        print(f"Error: Failed to download file {e}")


def parse_args_from_string(s: str):
    """
    Función que parsea un string como si fueran argumentos de línea de comandos y devuelve un diccionario
    @example Dado el string '-m asd -l asd' devuelve el diccionario {"-m": "asd", "-l": "asd"}.
    """
    raw_args: List[str] = s.split()
    args: Dict[str, str] = {}
    for x, y in zip(raw_args, raw_args[1:]):
        if x.startswith("-"):
            args[x] = y
    return args


@magics_class
class CDPP(Magics):
    """
    Clase contenedora de las funciones magics creadas para simplificar el uso del simulador CDPP
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.compile_from_project: bool = False
        self.CDPP_PROJECT_SRC: Optional[Path] = None
        self.CDPP_PROJECT_BIN: Optional[Path] = None
        self.CDPP_PROJECT_DIR: Optional[Path] = None
        self.SED_HOME: Path = Path()
        self.CDPP_DIR: Path = Path()
        self.CDPP_SRC: Path = Path()
        self.CDPP_EXAMPLES: Path = Path()
        self.CDPP_SCRIPTS: Path = Path()
        self.BASE_BIN: Path = Path()
        self.CDPP_ATOMICS: Path = Path()
        self.CDPP_EXAMPLES_CELL: Path = Path()
        self.CDPP_BIN: Path = Path()
        self.DRAWLOG_BIN: Path = Path()

    def get_cdpp_cwd(self) -> Optional[Path]:
        """
        Devuelve el directorio de trabajo actual para lo que es compilación del simulador.
        Es necesario para distinguir la compilación del simulador canónico del modificado en un proyecto.
        """
        if not self.compile_from_project:
            return self.CDPP_SRC
        return self.CDPP_PROJECT_SRC

    def set_up_project_compile(self, parameters: List[str]):
        """
        Establece el entorno del proyecto para que se compile y utilice una version del simulador propia del proyecto
        """
        if len(parameters) == 1:
            self.compile_from_project = False
            self.CDPP_PROJECT_DIR = self.CDPP_DIR.joinpath(Path(parameters[0]))
        else:
            self.compile_from_project = parameters[0].lower() == "-c"
            self.CDPP_PROJECT_DIR = self.CDPP_DIR.joinpath(Path(parameters[1]))

        if not self.CDPP_PROJECT_DIR.exists():
            print(f"Error: Project dir {str(self.CDPP_PROJECT_DIR)} does not exists.")
            return

        if not self.CDPP_PROJECT_DIR.is_relative_to(self.SED_HOME):
            print("Error: Project directory must be relative to SED folder")
            return

        globals()["CDPP_PATHS"]["CDPP_PROJECT_DIR"] = self.CDPP_PROJECT_DIR

        if self.compile_from_project:
            self.CDPP_PROJECT_SRC = self.CDPP_PROJECT_DIR.joinpath("src")

            if not self.CDPP_PROJECT_SRC.exists():
                print(f"Error: Project src dir {str(self.CDPP_PROJECT_SRC)} does not exists.")
                return

            self.CDPP_PROJECT_BIN = self.CDPP_PROJECT_SRC.joinpath("bin")

            if not self.CDPP_PROJECT_BIN.exists():
                print(f"Error: Project src/bin dir {str(self.CDPP_PROJECT_BIN)} does not exists.")
                return
        else:
            self.CDPP_PROJECT_SRC = None
            self.CDPP_PROJECT_BIN = None

        globals()["CDPP_PATHS"]["CDPP_PROJECT_SRC"] = self.CDPP_PROJECT_SRC
        globals()["CDPP_PATHS"]["CDPP_PROJECT_BIN"] = self.CDPP_PROJECT_BIN

    @magic_arguments()
    @argument("home", type=str, help="Path a la carpeta que contiene al directorio SED.")
    @line_magic
    def cdpp_init(self, line: str) -> Optional[Dict[str, Path]]:
        """
        Función magic de línea que se encarga de inicializar el entorno del simulador CDPP, carga todos los paths que se
         van a utilizar y crea una copia global para que se puedan acceder desde los notebooks.
        Toma como parámetro obligatorio el path a la carpeta que contiene a la carpeta SED(ej: /home/usuario/),
        la cual contiene el simulador CDPP.
        """
        args = parse_argstring(CDPP.cdpp_init, line)

        home_path: Path = Path(args.home)
        if not home_path.exists():
            print(f"Error: Folder path {home_path} does not exists.")
            return
        self.SED_HOME = home_path.joinpath('SED')
        if not self.SED_HOME.exists():
            print(f"Error: {home_path} does not contain folder named SED.")

        # Directorio base donde está instalado el simulador

        self.CDPP_DIR = self.SED_HOME.joinpath('CDPP_ExtendedStates-codename-Santi')
        if not self.CDPP_DIR.exists():
            print(f"Error: {home_path} does not contain folder named CDPP_ExtendedStates-codename-Santi.")
            return

        self.CDPP_SRC = self.CDPP_DIR.joinpath('src')
        self.CDPP_EXAMPLES = self.CDPP_DIR.joinpath('examples')
        self.CDPP_SCRIPTS = self.CDPP_DIR.joinpath('scripts')
        self.BASE_BIN = self.CDPP_SRC.joinpath('bin')
        self.CDPP_ATOMICS = self.CDPP_SRC.joinpath('cd++/atomics')

        self.CDPP_EXAMPLES_CELL = self.CDPP_EXAMPLES.joinpath('cell-devs')
        self.CDPP_BIN = self.BASE_BIN.joinpath('cd++')
        self.DRAWLOG_BIN = self.BASE_BIN.joinpath('drawlog')

        cdpp_paths: Dict[str, Path] = {"SED_HOME": self.SED_HOME, "CDPP_DIR": self.CDPP_DIR, "CDPP_SRC": self.CDPP_SRC,
                                       "CDPP_EXAMPLES": self.CDPP_EXAMPLES,
                                       "CDPP_EXAMPLES_CELL": self.CDPP_EXAMPLES_CELL, "CDPP_SCRIPTS": self.CDPP_SCRIPTS,
                                       "CDPP_ATOMICS": self.CDPP_ATOMICS, "CDPP_BIN": self.CDPP_BIN,
                                       "DRAWLOG_BIN": self.DRAWLOG_BIN, "BASE_BIN": self.BASE_BIN}

        globals()["CDPP_PATHS"] = cdpp_paths

        self.compile_from_project = False

        return globals()["CDPP_PATHS"]

    @magic_arguments()
    @argument("project", type=str,
              help="Path a la carpeta que contiene el proyecto sobre el cual se quiere trabajar."
                   "Debe ser relativo a la carpeta del simulador.")
    @argument("-c", "--compile_from_project", action="store_true",
              help="Flag que indica si se debe compilar y usar el simulador dentro de la carpeta del proyecto, "
                   "en lugar de la carpeta base.")
    @line_magic
    def cdpp_set_project(self, line: str) -> str:
        """
        Función magic de línea que establece el path al proyecto sobre el cual trabajar.
        """
        args = parse_argstring(CDPP.cdpp_set_project, line)

        parameters: List[str] = [args.project]
        if args.compile_from_project:
            parameters.insert(0, "-c")

        self.set_up_project_compile(parameters)

        return str(self.CDPP_PROJECT_DIR)

    @magic_arguments()
    @argument("file", type=str, help="Path al archivo a mostrar. Debe ser relativo al directorio del proyecto.")
    @line_magic
    def cdpp_show(self, line: str) -> None:
        """
        Función magic de línea que carga un archivo de texto y lo muestra en la celda
        """
        args = parse_argstring(CDPP.cdpp_show, line)
        file_path = Path(args.file)

        if not file_path.is_relative_to(self.CDPP_PROJECT_DIR) and (self.CDPP_PROJECT_DIR / file_path).exists():
            file_path = self.CDPP_PROJECT_DIR / file_path
        if not file_path.exists():
            print(f"Error: File {str(file_path)} does not exists.")
        print(file_path.read_text())

    @magic_arguments()
    @argument("folder_path", type=str, help="Path a la carpeta a copiar en el directorio del proyecto actual.")
    @line_magic
    def cdpp_copy_to_project(self, line: str) -> None:
        """
        Función magic de línea que copia una carpeta y su contenido a la carpeta principal del proyecto actual.
        """
        args = parse_argstring(CDPP.cdpp_copy_to_project, line)
        src_path: Path = Path(args.folder_path)
        if not src_path.exists():
            print("Error: Path does not exists.")
            return
        print(f"Copiando contenidos de {src_path} a {self.CDPP_PROJECT_DIR}...")
        try:
            shutil.copytree(src_path, self.CDPP_PROJECT_DIR, dirs_exist_ok=True, copy_function=shutil.copy)
            print("Listo!")
        except Exception as e:
            print(f"Error: Directory copy failed. {str(e)}")

    @magic_arguments()
    @argument("url", type=str, help="URL del recurso a descargar.")
    @argument("download_path", type=str, help="Ubicación y nombre donde se guarda el archivo descargado.")
    @line_magic
    def cdpp_download(self, line: str) -> None:
        """
        Función magic que descarga el archivo indicado por la url parámetro y lo guarda con el nombre indicado
        """
        args = parse_argstring(CDPP.cdpp_download, line)

        out_path = Path(args.download_path)
        download_file(args.url, out_path)

        print(f"Done: {args.url}, {out_path}")

    @magic_arguments()
    @argument("download_path", type=str,
              help="Ubicación y nombre donde se guarda el archivo descargado." 
                   "Es relativo a la carpeta del proyecto actual.")
    @line_magic
    def cdpp_download_carleton(self, line: str) -> None:
        """
        Función magic que descarga el archivo indicado por la url pasada por parámetro y lo guarda en el path relativo
        a la carpeta del proyecto indicado
        """
        args = parse_argstring(CDPP.cdpp_download_carleton, line)
        path: Path = Path(args.download_path)
        out_path: Path = self.CDPP_PROJECT_DIR.joinpath(path)
        download_file(URL_CARLETON_MODELS + args.download_path, out_path)

        print(f"Done: {URL_CARLETON_MODELS + args.download_path}, {str(out_path)}")

    @magic_arguments()
    @argument("path", type=str,
              help="Path al archivo comprimido que se quiere descomprimir, relativo a la carpeta del proyecto actual.")
    @line_magic
    def cdpp_unzip(self, line: str) -> None:
        """
        Función magic que descomprime el archivo indicado por el path, relativo a la carpeta del proyecto
        """
        args = parse_argstring(CDPP.cdpp_unzip, line)
        file_path = self.CDPP_PROJECT_DIR.joinpath(args.path)

        if not file_path.exists():
            print(f"Error: File {str(file_path)} does not exists")

        with zipfile.ZipFile(f"{str(file_path)}", 'r') as zip_ref:
            zip_ref.extractall(self.CDPP_PROJECT_DIR)

        print(f"Done extracting {line}")

    @line_magic
    def cdpp_compile(self, _: str) -> None:
        """
        Función magic de línea que se encarga de compilar el simulador CDPP
        """
        command: List[str] = ["make", "-j4"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True, shell=True,
                               stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_compile_tools(self, _: str) -> None:
        """
        Función magic de línea que se encarga de compilar las herramientas auxiliares del simulador CDPP(ej: drawlog)
        """
        command: List[str] = ["make", "-j4", "tools"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True, shell=True,
                               stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_recompile(self, line: str) -> None:
        """
        Función magic de línea que se encarga de limpiar la compilación del simulador CDPP y luego lo compila.
        """
        command: List[str] = ["make", "clean"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True, shell=True,
                               stdout=subprocess.PIPE).stdout.read())
        self.cdpp_compile(line)

    @line_magic
    def cdpp_help(self, _: str) -> None:
        """
        Función magic de línea que muestra la ayuda del programa cd++
        """
        if self.SED_HOME == Path():
            print("Error: Entorno CDPP no inicializado, use el magic %cdpp_init primero y vuelva a intentarlo.")
            return
        program: Path = self.get_cdpp_cwd().joinpath("bin").joinpath("cd++")
        command: List[str] = [f"{str(program)}", "-h"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True,
                               stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def drawlog_help(self, _: str) -> None:
        """
        Función magic de línea que muestra la ayuda del programa drawlog
        """
        if self.SED_HOME == Path():
            print("Error: Entorno CDPP no inicializado, use el magic %cdpp_init primero y vuelva a intentarlo.")
            return
        program: Path = self.BASE_BIN.joinpath("drawlog")
        command: List[str] = [f"{str(program)}", "-h"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True,
                               stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def drawlog_run(self, line: str) -> None:
        """
        Función magic de línea que ejecuta el programa drawlog con sus parámetros correspondientes indicados por línea
        """
        parameters: Dict[str, str] = parse_args_from_string(line)
        for k in parameters.keys():
            if k in ["-l", "-m"]:
                parameters[k] = str(self.CDPP_PROJECT_DIR / Path(parameters[k]))

        if not self.compile_from_project:
            program: Path = self.BASE_BIN.joinpath("cd++")
        else:
            program: Path = self.CDPP_PROJECT_BIN.joinpath("cd++")
        command: List[str] = [f"{str(program)}"]

        for k, v in parameters.items():
            command.append(k)
            command.append(v)

        print(subprocess.Popen(command, cwd=self.CDPP_PROJECT_DIR, universal_newlines=True,
                               stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_run(self, line: str) -> None:
        """
        Función magic de línea que ejecuta el simulador CD++ con sus parámetros correspondientes indicados por línea.
        """
        parameters: Dict[str, str] = parse_args_from_string(line)
        for k in parameters.keys():
            if k in ["-l", "-m", "-o", "-D"]:
                parameters[k] = str(self.CDPP_PROJECT_DIR / Path(parameters[k]))

        if not self.compile_from_project:
            program: Path = self.BASE_BIN.joinpath("cd++")
        else:
            program: Path = self.CDPP_PROJECT_BIN.joinpath("cd++")
        command: List[str] = [f"{str(program)}"]

        for k, v in parameters.items():
            command.append(k)
            command.append(v)

        print(subprocess.Popen(command, cwd=self.CDPP_PROJECT_DIR, universal_newlines=True,
                               stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def lscdpp(self, _: str) -> Dict[str, List[str]]:
        """
        Función magic que lista todos los magics definidos que simplifican el uso del simulador CDPP
        """
        return {"line": LINE_MAGICS, "cell": CELL_MAGICS}

    @magic_arguments()
    @argument("path_to_out_ev", type=str,
              help="Path al archivo de salida .out generado por una ejecución del simulador.")
    @line_magic
    def parse_out_ev(self, line: str) -> Optional[pandas.DataFrame]:
        """
        Función magic de línea que lee y parsea un archivo .out o .ev generado por una ejecución del simulador CDPP
        y devuelve un Dataframe de pandas con la información correspondiente.
        """
        args = parse_argstring(CDPP.parse_out_ev, line)
        path = Path(args.path_to_out_ev)
        if self.CDPP_PROJECT_DIR is not None:
            path = self.CDPP_PROJECT_DIR / Path(args.path_to_out_ev)
        if not path.exists():
            print(f"Error: File {line} does not exists.")
            return
        df = parser_out_ev(path)
        return df

    @magic_arguments()
    @argument("path_log_file", type=str,
              help="Path al archivo de salida .log generado por una ejecución del simulador.")
    @line_magic
    def parse_log(self, line: str) -> Optional[Dict[str, pandas.DataFrame]]:
        """
        Función magic de línea que lee y parsea un archivo .log generado por una ejecución del simulador CDPP
        y devuelve un Dataframe de pandas con la información correspondiente.
        """
        args = parse_argstring(CDPP.parse_log, line)
        path = Path(args.path_to_log_file)
        if self.CDPP_PROJECT_DIR is not None:
            path = self.CDPP_PROJECT_DIR / Path(args.path_to_log_file)
        if not path.exists():
            print(f"Error: File {line} does not exists.")
            return
        return parser_log(path)


if __name__ == '__main__':
    from IPython import get_ipython
    get_ipython().register_magics(CDPP)
