#ifndef __AGENTE_H // cambiar nombre
#define __AGENTE_H // cambiar nombre

/** include files **/
#include <random>
#include "atomic.h"  // class Atomic
#include "VTime.h"

#define ATOMIC_MODEL_NAME "Agente" // cambiar nombre

/** forward declarations **/
class Distribution;

/** declarations **/
class Agente: public Atomic {
	public:
		Agente( const string &name = ATOMIC_MODEL_NAME ); // Default constructor
		~Agente(); // Destructor
		virtual string className() const {return ATOMIC_MODEL_NAME;}
	protected:
		Model &initFunction();
		Model &externalFunction( const ExternalMessage & );
		Model &internalFunction( const InternalMessage & );
		Model &outputFunction( const CollectMessage & );
	private:
		/***********      Example declarations   **********************************/
    Port &finalizada ,&pedido;   	// this is an output port named 'out'
    const Port &entrante;	// this is an input port named 'in'
		Distribution *dist ;
		Distribution &distribution()	{ return *dist; }
		/**************************************************************************/
		// [(!) declare common variables]
    enum Estados {
      ATENDIENDO,
      PIDIENDO
    };
    Estados estado;
    VTime t;
    Tuple<Real> llamada;
    Real id;
};	// class Agente
#endif   //__AGENTE_H
