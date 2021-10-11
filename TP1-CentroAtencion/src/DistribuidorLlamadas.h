#ifndef __DISTRIBUIDORLLAMADAS_H // cambiar nombre
#define __DISTRIBUIDORLLAMADAS_H // cambiar nombre

/** include files **/
#include <random>
#include "atomic.h"  // class Atomic
#include "VTime.h"

#define ATOMIC_MODEL_NAME "DistribuidorLlamadas" // cambiar nombre

/** forward declarations **/
class Distribution;

/** declarations **/
class DistribuidorLlamadas: public Atomic {
	public:
		DistribuidorLlamadas( const string &name = ATOMIC_MODEL_NAME ); // Default constructor
		~DistribuidorLlamadas(); // Destructor
		virtual string className() const {return ATOMIC_MODEL_NAME;}
	protected:
		Model &initFunction();
		Model &externalFunction( const ExternalMessage & );
		Model &internalFunction( const InternalMessage & );
		Model &outputFunction( const CollectMessage & );
	private:
		const Port &entrante;	// this is an input port named 'in'
    Port &pedirLlamada, &clientes, &noClientes ;   	// this is an output port named 'out'
		Distribution *dist ;
		Distribution &distribution()	{ return *dist; }

		// [(!) declare common variables]
    enum class Estados {
      PIDIENDO,
      ESPERANDO,
      ENVIANDO
    };
    Estados estado;
    Tuple<Real> llamada;

		// Lifetime programmed since the last state transition to the next planned internal transition.
		VTime sigma;
};	// class DistribuidorLlamadas
#endif   //__DISTRIBUIDORLLAMADAS_H
