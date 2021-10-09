#include "pmodeladm.h" 
#include "register.h"

#include "GeneradorLlamadas.h"
#include "Cola.h"
#include "Agente.h"
#include "DistribuidorLlamadas.h"
#include "DistribuidorAgentes.h"
#include "Medidor.h"

void register_atomics_on(ParallelModelAdmin &admin)
{
	admin.registerAtomic(NewAtomicFunction< GeneradorLlamadas >(), "GeneradorLlamadas");
    admin.registerAtomic(NewAtomicFunction< Cola >(), "Cola");
    admin.registerAtomic(NewAtomicFunction< Agente >(), "Agente");
    admin.registerAtomic(NewAtomicFunction< DistribuidorLlamadas >(), "DistribuidorLlamadas");
    admin.registerAtomic(NewAtomicFunction< DistribuidorAgentes >(), "DistribuidorAgentes");
    admin.registerAtomic(NewAtomicFunction< Medidor >(), "Medidor");
}

