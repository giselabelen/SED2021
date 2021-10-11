[top]
components: generador@GeneradorLlamadas cola@Cola agente1@Agente

out: out
in: in

link: in parar@generador
link: llamada@generador entrada@cola
link: salida@cola entrante@agente1
link: pedido@agente1 liberar@cola
link: finalizada@agente1 out

[generador]
distribution: constant
value: 5

[agente1]
id: 1
distribution: exponential
mean: 5

[cola]
preparation: 00:00:01:000:0