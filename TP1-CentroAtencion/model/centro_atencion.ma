[top]
components: generador@GeneradorLlamadas mesa area1 area2 medidor@Medidor

out: out_metricas
in: in_parar

link: in_parar parar@generador
link: medicion@medidor out_metricas

link: llamada@generador entrante@mesa
link: llamada@generador entrante@medidor

link: llamadaCliente@mesa entrante@area1
link: llamadaNoCliente@mesa entrante@area2

link: llamadaAtendida@area1 atendida@medidor
link: llamadaFinalizada@area1 finalizada@medidor

link: llamadaAtendida@area2 atendida@medidor
link: llamadaFinalizada@area2 finalizada@medidor

[generador]
distribution: poisson
mean: 5

[mesa]
components: cola@Cola distribuidor@DistribuidorLlamadas

out: llamadaCliente llamadaNoCliente
int: entrante

link: entrante entrada@cola
link: clientes@distribuidor llamadaCliente
link: noClientes@distribuidor llamadaNoCliente

link: salida@cola entrante@distribuidor
link: pedirLlamada@distribuidor liberar@cola

[area1]
components: cola@Cola distribuidor@DistribuidorAgentes agente1@Agente agente2@Agente

out: llamadaAtendida llamadaFinalizada
in: entrante

link: entrante entrante@cola

link: agente1@distribuidor llamadaAtendida
link: agente2@distribuidor llamadaAtendida
link: finalizada@agente1 llamadaFinalizada
link: finalizada@agente2 llamadaFinalizada

link: salida@cola entrante@distribuidor
link: pedirLlamada@distribuidor liberar@cola
link: agente1@distribuidor entrante@agente1
link: agente2@distribuidor entrante@agente2
link: pedido@agente1 pedido@distribuidor
link: pedido@agente2 pedido@distribuidor

[area2]
components: cola@Cola distribuidor@DistribuidorAgentes agente1@Agente agente2@Agente

out: llamadaAtendida llamadaFinalizada
in: entrante

link: entrante entrante@cola

link: agente1@distribuidor llamadaAtendida
link: agente2@distribuidor llamadaAtendida
link: finalizada@agente1 llamadaFinalizada
link: finalizada@agente2 llamadaFinalizada

link: salida@cola entrante@distribuidor
link: pedirLlamada@distribuidor liberar@cola
link: agente1@distribuidor entrante@agente1
link: agente2@distribuidor entrante@agente2
link: pedido@agente1 pedido@distribuidor
link: pedido@agente2 pedido@distribuidor

[medidor]
periodo: 30
