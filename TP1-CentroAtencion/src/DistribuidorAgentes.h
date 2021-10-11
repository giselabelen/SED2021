#ifndef __DISTRIBUIDORAGENTES_H // cambiar nombre
#define __DISTRIBUIDORAGENTES_H // cambiar nombre

/** include files **/
#include <random>
#include "atomic.h"  // class Atomic
#include "VTime.h"

#define ATOMIC_MODEL_NAME "DistribuidorAgentes" // cambiar nombre

/** declarations **/
class DistribuidorAgentes: public Atomic {
	public:
		DistribuidorAgentes( const string &name = ATOMIC_MODEL_NAME ); // Default constructor
		~DistribuidorAgentes(); // Destructor
		virtual string className() const {return ATOMIC_MODEL_NAME;}
	protected:
    Model &initFunction();
		Model &externalFunction( const ExternalMessage & );
		Model &internalFunction( const InternalMessage & );
		Model &outputFunction( const CollectMessage & );
	private:
    const Port &pedido, &entrante;	// this is an input port named 'in'
    Port &pedirLlamada, &agente1, &agente2;   	// this is an output port named 'out'
		// [(!) declare common variables]
    enum class Estados{
      DESOCUPADO,
      PIDIENDO,
      ESPERANDO,
      ENVIANDO
    };
    Estados estado;
    std::list<Real> pedidosEnEspera;
    bool luegoDeEnviar;
    Tuple<Real> llamada;
};	// class DistribuidorAgentes


#endif   //__DISTRIBUIDORAGENTES_H
