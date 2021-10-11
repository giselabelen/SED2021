[top]
components: generador@GeneradorLlamadas agente1@Agente

out: out
in: in

link: in parar@generador
link: llamada@generador entrante@agente1
link: finalizada@agente1 out

[generador]
distribution: constant
value: 5

[agente1]
id: 1
distribution: exponential
mean: 5
