[top]
components: generador@GeneradorLlamadas cola@Cola distribuidor@DistribuidorLlamadas

out: out
in: in

link: in parar@generador
link: llamada@generador entrada@cola
link: salida@cola entrante@distribuidor
link: pedirLlamada@distribuidor liberar@cola
link: clientes@distribuidor out
link: noClientes@distribuidor out

[generador]
distribution: constant
value: 5

[distribuidor]
distribution: exponential
mean: 1

[cola]
preparation: 00:00:01:000:0