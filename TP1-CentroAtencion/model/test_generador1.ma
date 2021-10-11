[top]
components: generador@GeneradorLlamadas

out: out
in: in

link: in parar@generador
link: llamada@generador out

[generador]
distribution: constant
value: 1
