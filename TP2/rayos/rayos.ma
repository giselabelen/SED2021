[Top]
components : rayos

[rayos]
type : cell
dim : (10, 10, 2)
delay : transport
border : nowrapped
neighbors : rayos(0,-1,0)  rayos(0,0,0)  rayos(0,1,0)
neighbors : rayos(0,-1,1)  rayos(0,0,1)  rayos(0,1,1)
initialvalue : 1.0
initialcolvalue: 0 10
localtransition : rayos-rule
defaultDelayTime : 0.0

[rayos-rule]
% Regla avanzar sin obstaculos
% Si mi valor en intensidades y en atenuaciones es 0, y el valor de intensidad de mi vecino izquierdo es mayor a 0, tomo el % valor de intensidad de mi vecino izquierdo.

rule : {(0,-1,0)} 0 {(0,0,0) = 0 and (0,0,1) = 0 and (0, -1, 0) > 0}  

% Regla avanzar con obstaculos
% Si mi valor en intensidades es 0 y en atenuaciones no es 0, y el valor de intensidad de mi vecino izquierdo es mayor a 0, % tomo el valor de intensidad de mi vecino izquierdo menos la atenuacion. (TODO: Hacer bien el calculo de atenuacion)

rule : {(0,-1,0) * exp((0,0,1))} 0 {(0,0,0) = 0 and (0,0,1) > 0 and (0, -1, 0) > 0}  

% Regla borde derecho
% En las celdas de la última columna, se mantiene el valor -1 mientras su vecino izquierdo no tenga valor distinto de 0.

rule : {(0,0,0)} 0 {cellpos(1) = 9 and (0, -1, 0) = 0 and (0,0,0) = -1}

% Regla output
% En las celdas de la última columna, si su vecino izquierdo tiene un valor de intensidad mayor a 0, se toma ese valor.

rule : {(0,-1,0)} 0 { cellpos(1) = 9 and (0, -1, 0) > 0 }

% Regla default
% Es siempre verdadera. Mantiene el valor actual de la celda.

rule : {(0,0,0)} 0 { t }