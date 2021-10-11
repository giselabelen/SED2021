[top]
components: generador1@GeneradorLlamadas generador2@GeneradorLlamadas generador3@GeneradorLlamadas medidor@Medidor

out: out
in: in

link: in parar@generador1
link: llamada@generador1 entrante@medidor
link: in parar@generador2
link: llamada@generador2 atendida@medidor
link: in parar@generador3
link: llamada@generador3 finalizada@medidor
link: mediciones@medidor out

[generador1]
distribution: constant
value: 1

[generador2]
distribution: constant
value: 5

[generador3]
distribution: constant
value: 10

[medidor]
periodo: 30
