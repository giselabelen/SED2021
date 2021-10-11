[top]
components: generador@GeneradorLlamadas

out: out
in: in

link: in parar@generador
link: llamada@generador out

[generador]
distribution: poisson
mean: 5
initial: 0
increment: 1
