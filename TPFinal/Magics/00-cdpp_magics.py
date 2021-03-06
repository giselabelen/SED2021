from typing import Optional
from IPython.core.magic import (Magics, magics_class, line_magic)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from pathlib import Path
from urllib import request
import subprocess
import shutil
import zipfile

"""
Colección de funciones magics para facilitar el uso del simulador CDPP en Jupyter Labs.

Para que IPython cargue y utilice las funciones y los magics definidos en este archivo, se lo debe colocar en la carpeta ~/.ipython/profile_{NAME}/startup/
donde {NAME} es el nombre del perfil de IPython sobre el cua lse va a trabajar, por defecto es default(profile_default).
"""

URL_CARLETON_MODELS : str = "http://www.sce.carleton.ca/faculty/wainer/wbgraf/samples/"

LINE_MAGICS : list[str] = ["lscdpp", "cdpp_run", "drawlog_run", "cdpp_help", "drawlog_help", "cdpp_compile", "cdpp_compile_tools", "cdpp_recompile",
                           "cdpp_unzip", "cdpp_download", "cdpp_download_carleton", "cdpp_copy_to_project", "cdpp_show_model", "cdpp_set_project",
                           "cdpp_init"]
CELL_MAGICS : list[str] = []

def download_file(url : str, download_file_path : Path):
    try:
        request.urlretrieve(url, download_file_path)
    except Exception as e:
        print(f"Error: Failed to download file {e}")


def parse_args_from_string(s : str):
    """
    Función que parsea un string como si fueran argumentos de línea de comandos y devuelve un diccionario para más fácil acceso.
    @example Dado el string '-m asd -l asdgf' devuelve el diccionario {"-m": "asd", "-l": "asdgf"}.
    """
    raw_args : list[str] = s.split()
    args : dict[str, str] = {}
    for x, y in zip(raw_args, raw_args[1:]):
        if x.startswith("-"):
            args[x] = y
    return args

@magics_class
class CDPP(Magics):
    def get_cdpp_cwd(self) -> Optional[Path]:
        if not self.compile_from_project:
            return self.CDPP_SRC
        return self.CDPP_PROJECT_SRC

    def set_up_project_compile(self, parameters : list[str]):
        if len(parameters) == 1:
            self.compile_from_project : bool = False
            self.CDPP_PROJECT_DIR : Path = self.CDPP_DIR.joinpath(Path(parameters[0]))
        else:
            self.compile_from_project : bool = parameters[0].lower() == "-c"
            self.CDPP_PROJECT_DIR : Path = self.CDPP_DIR.joinpath(Path(parameters[1]))

        if not self.CDPP_PROJECT_DIR.exists():
            return f"Error: Project dir {str(self.CDPP_PROJECT_DIR)} does no exists."

        globals()["CDPP_PATHS"]["CDPP_PROJECT_DIR"] = self.CDPP_PROJECT_DIR

        if self.compile_from_project:
            self.CDPP_PROJECT_SRC : Optional[Path] = self.CDPP_PROJECT_DIR.joinpath("src")

            if not self.CDPP_PROJECT_SRC.exists():
                return f"Error: Project src dir {str(self.CDPP_PROJECT_SRC)} does no exists."

            self.CDPP_PROJECT_BIN : Optional[Path] = self.CDPP_PROJECT_SRC.joinpath("bin")

            if not self.CDPP_PROJECT_BIN.exists():
                return f"Error: Project src/bin dir {str(self.CDPP_PROJECT_BIN)} does no exists."
        else:
            self.CDPP_PROJECT_SRC : Optional[Path] = None
            self.CDPP_PROJECT_BIN : Optional[Path] = None

        globals()["CDPP_PATHS"]["CDPP_PROJECT_SRC"] = self.CDPP_PROJECT_SRC
        globals()["CDPP_PATHS"]["CDPP_PROJECT_BIN"] = self.CDPP_PROJECT_BIN


    @magic_arguments()
    @argument("home", type=str, help="Path a la carpeta que contiene al directorio SED.")
    @line_magic
    def cdpp_init(self, line : str) -> str:
        """
        Función magic de línea que se encarga de inicializar el entorno del simulador CDPP, carga todos los paths que se van a utilizar y crea una copia global para que se puedan acceder desde los notebooks.
        Toma como parámetro obligatorio el path a la carpeta que contiene a la carpeta SED(ej: /home/usuario/), la cual contiene el simulador CDPP.
        """
        # parameters : list[str] = line.split()
        # if len(parameters) == 0:
        #    return "Error: Missing parameters."

        args = parse_argstring(CDPP.cdpp_init, line)

        home_path : str = args.home
        self.SED_HOME : Path = Path(home_path).joinpath('SED')
        #Directorio base donde está instalado el simulador
        self.CDPP_DIR : Path = self.SED_HOME.joinpath('CDPP_ExtendedStates-codename-Santi')

        self.CDPP_SRC : Path = self.CDPP_DIR.joinpath('src')
        self.CDPP_EXAMPLES : Path = self.CDPP_DIR.joinpath('examples')
        self.CDPP_SCRIPTS : Path = self.CDPP_DIR.joinpath('scripts')
        self.BASE_BIN : Path = self.CDPP_SRC.joinpath('bin')
        self.CDPP_ATOMICS : Path = self.CDPP_SRC.joinpath('cd++/atomics')

        self.CDPP_EXAMPLES_CELL : Path = self.CDPP_EXAMPLES.joinpath('cell-devs')
        self.CDPP_BIN : Path = self.BASE_BIN.joinpath('cd++')
        self.DRAWLOG_BIN : Path = self.BASE_BIN.joinpath('drawlog')

        CDPP_PATHS : dict[str, Path] = {}
        CDPP_PATHS["SED_HOME"] = self.SED_HOME
        CDPP_PATHS["CDPP_DIR"] = self.CDPP_DIR
        CDPP_PATHS["CDPP_SRC"] = self.CDPP_SRC
        CDPP_PATHS["CDPP_EXAMPLES"] = self.CDPP_EXAMPLES
        CDPP_PATHS["CDPP_EXAMPLES_CELL"] = self.CDPP_EXAMPLES_CELL
        CDPP_PATHS["CDPP_SCRIPTS"] = self.CDPP_SCRIPTS
        CDPP_PATHS["CDPP_ATOMICS"] = self.CDPP_ATOMICS
        CDPP_PATHS["CDPP_BIN"] = self.CDPP_BIN
        CDPP_PATHS["DRAWLOG_BIN"] = self.DRAWLOG_BIN
        CDPP_PATHS["BASE_BIN"] = self.BASE_BIN

        globals()["CDPP_PATHS"] = CDPP_PATHS

        self.compile_from_project : bool = False

        return str(self.SED_HOME)

    @magic_arguments()
    @argument("project", type=str, help="Path a la carpeta que contiene el proyecto sobre el cual se quiere trabajar. Debe ser relativo a la carpeta del simulador.")
    @argument("-c", "--compile_from_project", action="store_true",
              help="Flag que indica si se debe compilar y usar el simulador dentro de la carpeta del proyecto, en lugar de la carpeta base.")
    @line_magic
    def cdpp_set_project(self, line : str) -> str:
        """
        Función magic de línea que setea el path al proyecto sobre el cual trabajar.
        """
        args = parse_argstring(CDPP.cdpp_set_project, line)

        parameters : list[str] = [args.project]
        if args.compile_from_project:
            parameters.insert(0, "-c")

        self.set_up_project_compile(parameters)

        return str(self.CDPP_PROJECT_DIR)

    @magic_arguments()
    @argument("file", type=str, help="Path al archivo a mostrar. Debe ser relativo al directorio del proyecto.")
    @line_magic
    def cdpp_show_model(self, line : str) -> None:
        """
        Función magic de línea que carga un archivo de texto .ma y lo muestra en la celda
        """
        args = parse_argstring(CDPP.cdpp_show_model, line)

        model_path : Path = self.CDPP_PROJECT_DIR / Path(args.file)
        if not model_path.exists():
            print(f"Error: File {str(model_path)} does not exists.")
        print(model_path.read_text())

    @magic_arguments()
    @argument("folderpath", type=str, help="Path a la carpeta a copiar en el directorio del proyecto actual.")
    @line_magic
    def cdpp_copy_to_project(self, line : str) -> str:
        """
        Función magic de línea que copia una carpeta y su contenido a la carpeta principal del proyecto actual.
        """
        args = parse_argstring(CDPP.cdpp_copy_to_project, line)
        src_path : Path = Path(args.folderpath)
        if not src_path.exists():
            return "Error: Path does not exists."
        print(f"Copiando contenidos de {src_path} a {self.CDPP_PROJECT_DIR}...")
        try:
            shutil.copytree(src_path, self.CDPP_PROJECT_DIR, dirs_exist_ok=True, copy_function=shutil.copy)
            return "Listo!"
        except Exception as e:
            return f"Error: Directory copy failed. {str(e)}"

    @magic_arguments()
    @argument("url", type=str, help="URL del recurso a descargar.")
    @argument("download_path", type=str, help="Ubicación y nombre donde se guarda el archivo descargado.")
    @line_magic
    def cdpp_download(self, line : str) -> str:
        """
        Función magic que descarga el archivo indicado por la url pasada por parametro y lo guarda con el nombre indicado
        """
        args = parse_argstring(CDPP.cdpp_download, line)

        out_path = Path(args.download_path)
        download_file(args.url, out_path)

        return f"Done: {args.url}, {out_path}"

    @magic_arguments()
    @argument("download_path", type=str, help="Ubicación y nombre donde se guarda el archivo descargado. Es relativo a la carpeta del proyecto actual.")
    @line_magic
    def cdpp_download_carleton(self, line : str) -> str:
        """
        Función magic que descarga el archivo indicado por la url pasada por parametro y lo guarda en el path relativo a la carpeta del proyecto indicado
        """
        args = parse_argstring(CDPP.cdpp_download_carleton, line)

        out_path : Path = self.CDPP_PROJECT_DIR.joinpath(Path(args.download_path))
        download_file(URL_CARLETON_MODELS + args.download_path, out_path)

        return f"Done: {URL_CARLETON_MODELS + args.download_path}, {str(out_path)}"

    @magic_arguments()
    @argument("path", type=str, help="Path al archivo comprimido que se quiere descomprimir, relativo a la carpeta del proyecto actual.")
    @line_magic
    def cdpp_unzip(self, line : str) -> str:
        """
        Función magic que descomprime el archivo indicado por el path, relativo a la carpeta del proyecto
        """
        args = parse_argstring(CDPP.cdpp_unzip, line)
        file_path = self.CDPP_PROJECT_DIR.joinpath(args.path)

        if not file_path.exists():
            print(f"Error: File {str(file_path)} does not exists")

        with zipfile.ZipFile(f"{str(file_path)}", 'r') as zip_ref:
            zip_ref.extractall(self.CDPP_PROJECT_DIR)

        return f"Done extracting {line}"

    @line_magic
    def cdpp_compile(self, line : str) -> None:
        """
        Función magic de línea que se encarga de compilar el simulador CDPP
        """
        command : list[str] = ["make", "-j4"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True, shell=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_compile_tools(self, line : str) -> None:
        """
        Función magic de línea que se encarga de compilar las herramientas auxiliares del simulador CDPP(ej: drawlog)
        """
        command : list[str] = ["make", "-j4", "tools"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True, shell=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_recompile(self, line : str) -> None:
        """
        Función magic de línea que se encarga de limpiar la compilación del simulador CDPP y luego lo compila.
        """
        command : list[str] = ["make", "clean"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True, shell=True, stdout=subprocess.PIPE).stdout.read())
        self.cdpp_compile(line)

    @line_magic
    def cdpp_help(self, line : str) -> None:
        """
        Función magic de línea que muestra la ayuda del programa cd++
        """
        program : Path = self.BASE_BIN.joinpath("cd++")
        command : list[str] = [f"{str(program)}", "-h"]
        print(subprocess.Popen(command, cwd=self.CDPP_PROJECT_DIR, universal_newlines=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def drawlog_help(self, line : str) -> None:
        """
        Función magic de línea que muestra la ayuda del programa drawlog
        """
        program : Path = self.BASE_BIN.joinpath("drawlog")
        command : list[str] = [f"{str(program)}", "-h"]
        print(subprocess.Popen(command, cwd=self.get_cdpp_cwd(), universal_newlines=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def drawlog_run(self, line : str) -> None:
        """
        Función magic de línea que ejecuta el programa drawlog con sus parámetros correspondientes indicados por línea
        """
        parameters : dict[str, str] = parse_args_from_string(line)
        for k, v in parameters.items():
            if k in ["-l", "-m"]:
                v = str(self.CDPP_PROJECT_DIR / Path(v))

        if not self.compile_from_project:
            program : Path = self.BASE_BIN.joinpath("cd++")
        else:
            program : Path = self.CDPP_PROJECT_BIN.joinpath("cd++")
        command : list[str] = [f"{str(program)}"]

        for k, v in parameters.items():
            command.append(k)
            command.append(v)

        print(subprocess.Popen(command, cwd=self.CDPP_PROJECT_DIR, universal_newlines=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_run(self, line : str) -> None:
        """
        Función magic de línea que ejecuta el simulador CD++ con sus parámetros correspondientes indicados por línea.
        """
        parameters : dict[str, str] = parse_args_from_string(line)
        for k, v in parameters.items():
            if k in ["-l", "-m", "-o", "-D"]:
                v = str(self.CDPP_PROJECT_DIR / Path(v))

        if not self.compile_from_project:
            program : Path = self.BASE_BIN.joinpath("cd++")
        else:
            program : Path = self.CDPP_PROJECT_BIN.joinpath("cd++")
        command : list[str] = [f"{str(program)}"]

        for k, v in parameters.items():
            command.append(k)
            command.append(v)

        print(subprocess.Popen(command, cwd=self.CDPP_PROJECT_DIR, universal_newlines=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def lscdpp(self, line : str) -> dict[str, list[str]]:
        return {"line": LINE_MAGICS, "cell": CELL_MAGICS}


if __name__ == '__main__':
    from IPython import get_ipython
    get_ipython().register_magics(CDPP)

