from IPython.core.magic import (Magics, magics_class, line_magic)
from pathlib import Path
import subprocess
import shutil

"""
Colección de funciones magics para facilitar el uso del simulador CDPP en Jupyter Labs.

Para que IPython cargue y utilice las funciones y los magics definidos en este archivo, se lo debe colocar en la carpeta ~/.ipython/profile_{NAME}/startup/
donde {NAME} es el nombre del perfil de IPython sobre el cua lse va a trabajar, por defecto es default(profile_default).
"""


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
    @line_magic
    def cdpp_init(self, line : str) -> str:
        """
        Función magic de línea que se encarga de inicializar el entorno del simulador CDPP, carga todos los paths que se van a utilizar
        y crea una copia global para que se puedan acceder desde los notebooks.
        """
        parameters : list[str] = line.split()
        home_path : str = parameters[0]
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

        return str(self.SED_HOME)

    @line_magic
    def cdpp_set_project(self, line : str) -> str:
        """
        Función magic de línea que setea el path al proyecto actual del simulador CDPP.
        """
        parameters : list[str] = line.split()
        if len(parameters) == 0:
            return "Error: Project directory path missing"
        self.CDPP_PROJECT_DIR : Path = self.CDPP_DIR / Path(parameters[0])
        globals()["CDPP_PATHS"]["CDPP_PROJECT_DIR"] = self.CDPP_PROJECT_DIR
        return str(self.CDPP_PROJECT_DIR)

    @line_magic
    def cdpp_show_model(self, line : str) -> str:
        """
        Función magic de línea que carga un archivo de texto y lo muestra en la celda
        """
        parameters : list[str] = line.split()
        if len(parameters) != 1:
            return "Error: Must give model file path."
        model_path : Path = self.CDPP_PROJECT_DIR / Path(parameters[0])
        if not model_path.exists():
            return f"Error: File {str(model_path)} does not exists."
        print(model_path.read_text())
        return ""

    @line_magic
    def cdpp_copy_to_project(self, line : str) -> str:
        """
        Función magic de línea que copia una carpeta y su contenido a la carpeta principal del proyecto actual.
        """
        parameters : list[str] = line.split()
        if len(parameters) != 1:
            return "Error: Must give path to copy"
        src_path : Path = Path(parameters[0])
        if not src_path.exists():
            return "Error: Path does not exists."
        print(f"Copiando contenidos de {src_path} a {self.CDPP_PROJECT_DIR}...")
        try:
            shutil.copytree(src_path, self.CDPP_PROJECT_DIR, dirs_exist_ok=True, copy_function=shutil.copy)
            return "Listo!"
        except Exception as e:
            return f"Error: Directory copy failed. {str(e)}"

    @line_magic
    def cdpp_compile(self, line : str) -> None:
        """
        Función magic de línea que se encarga de compilar el simulador CDPP
        """
        command : list[str] = ["make", "-j4"]
        print(subprocess.Popen(command, cwd=self.CDPP_SRC, universal_newlines=True, shell=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_compile_tools(self, line : str) -> None:
        """
        Función magic de línea que se encarga de compilar las herramientas auxiliares del simulador CDPP(ej: drawlog)
        """
        command : list[str] = ["make", "-j4", "tools"]
        print(subprocess.Popen(command, cwd=self.CDPP_SRC, universal_newlines=True, shell=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_recompile(self, line : str) -> None:
        """
        Función magic de línea que se encarga de limpiar la compilación del simulador CDPP y luego lo compila.
        """
        command : list[str] = ["make", "clean"]
        print(subprocess.Popen(command, cwd=self.CDPP_SRC, universal_newlines=True, shell=True, stdout=subprocess.PIPE).stdout.read())
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
        print(subprocess.Popen(command, cwd=self.CDPP_PROJECT_DIR, universal_newlines=True, stdout=subprocess.PIPE).stdout.read())

    @line_magic
    def cdpp_run(self, line : str) -> None:
        """
        Función magic de línea que ejecuta el simulador CD++ con los parámetros indicados por línea
        """
        parameters : dict[str, str] = parse_args_from_string(line)
        for k, v in parameters.items():
            if k in ["-l", "-m", "-o", "-D"]:
                v = str(self.CDPP_PROJECT_DIR / Path(v))

        program : Path = self.BASE_BIN.joinpath("cd++")
        command : list[str] = [f"{str(program)}"]

        for k, v in parameters.items():
            command.append(k)
            command.append(v)

        print(subprocess.Popen(command, cwd=self.CDPP_PROJECT_DIR, universal_newlines=True, stdout=subprocess.PIPE).stdout.read())

if __name__ == '__main__':
    from IPython import get_ipython
    get_ipython().register_magics(CDPP)

