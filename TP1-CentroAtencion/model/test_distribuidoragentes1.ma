[top]
components: generador@GeneradorLlamadas cola@Cola distribuidor@DistribuidorAgentes agente1@Agente agente2@Agente

out: out
in: in

link: in parar@generador
link: llamada@generador entrada@cola
link: salida@cola entrante@distribuidor
link: pedirLlamada@distribuidor liberar@cola
link: agente1@distribuidor entrante@agente1
link: agente2@distribuidor entrante@agente2
link: pedido@agente1 pedido@distribuidor
link: pedido@agente2 pedido@distribuidor
link: finalizada@agente1 out
link: finalizada@agente2 out

[generador]
distribution: constant
value: 5

[distribuidor]

[cola]
preparation: 00:00:01:000:0

[agente1]
id: 1
distribution: exponential
mean: 5

[agente2]
id: 2
distribution: exponential
mean: 5