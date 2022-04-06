EXAMPLE_SIMPLE = """
[top]
components : generator@generator
out : out_port
in : stop
link : stop stop@generator
link : out@generator out_port

[generator]
distribution : normal
mean : 3
deviation : 1
initial : 1
increment : 5
"""

EXAMPLE_COMPLEX = """
[Top]
components : TrafficGenerator@Generator network 
out : out generator_out
in : setNetworkDelay 
Link : setNetworkDelay setDelay@network
Link : out@TrafficGenerator in@network
Link : out@TrafficGenerator generator_out
Link : out@network out

[TrafficGenerator]
distribution : Constant
value : 10
initial : 0
increment : 1

[network]
components : networkDelay@networkDelayType 
out : out 
in : in setDelay 
Link : in in@networkDelay
Link : setDelay setDelay@networkDelay
Link : out@networkDelay out

[networkDelay]
initialDelay : 5
"""

EXAMPLE_RULES = """
[Top]
components : rayos

[rayos]
type : cell
dim : (100, 100, 2)
delay : transport
border : nowrapped
neighbors : rayos(0,-1,0)  rayos(0,0,0)  rayos(0,1,0)
neighbors : rayos(0,-1,1)  rayos(0,0,1)  rayos(0,1,1)
initialValue : 0.0
initialCellsValue: estado_100_100.val
localtransition : rayos-rule
defaultDelayTime : 0.0

[rayos-rule]
% Regla avanzar sin obstaculos
% Si mi valor en intensidades y en atenuaciones es 0, y el valor de intensidad de mi vecino izquierdo es mayor a 0, tomo el % valor de intensidad de mi vecino izquierdo.

rule : {(0,-1,0)} 100 {cellpos(2) = 0 and (0,0,0) = 0 and (0,0,1) = 0 and (0, -1, 0) > 0}  

% Regla avanzar con obstaculos
% Si mi valor en intensidades es 0 y en atenuaciones no es 0, y el valor de intensidad de mi vecino izquierdo es mayor a 0, % tomo el valor de intensidad de mi vecino izquierdo menos la atenuacion. (TODO: Hacer bien el calculo de atenuacion)

rule : {(0,-1,0) * exp(-1.0 * (0,0,1))} 100 {cellpos(2) = 0 and (0,0,0) = 0 and (0,0,1) > 0 and (0, -1, 0) > 0}  

% Regla ya avance
% Si mi valor en intensidades no es 0 y a mi derecha hay un valor mayor a 0, significa que el rayo ya paso, me pongo en 0.

rule : {0.0} 100 {cellpos(2) = 0 and (0,0,0) > 0 and (0,1,0) > 0}

% Regla borde derecho
% En las celdas de la última columna, se mantiene el valor 0 mientras su vecino izquierdo no tenga valor distinto de 0.

rule : {(0,0,0)} 100 {cellpos(2) = 0 and cellpos(1) = 99 and (0, -1, 0) = 0 and (0,0,0) = 0}

% Regla output
% En las celdas de la última columna, si su vecino izquierdo tiene un valor de intensidad mayor a 0, se toma ese valor.

rule : {(0,-1,0)} 100 {cellpos(2) = 0 and cellpos(1) = 99 and (0, -1, 0) > 0 }

% Regla default
% Es siempre verdadera. Mantiene el valor actual de la celda.

rule : {(0,0,0)} 0 { t }
"""