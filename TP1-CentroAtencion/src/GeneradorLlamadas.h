#ifndef __GENERADORLLAMADAS_H // cambiar nombre
#define __GENERADORLLAMADAS_H // cambiar nombre

/** include files **/
#include <random>
#include "atomic.h"  // class Atomic
#include "VTime.h"

#define ATOMIC_MODEL_NAME "GeneradorLlamadas" // cambiar nombre

/** forward declarations **/
//TODO: add distribution class declaration here if needed
// Ej: class Distribution ;

/** declarations **/
class GeneradorLlamadas: public Atomic {
	public:
		GeneradorLlamadas( const string &name = ATOMIC_MODEL_NAME ); // Default constructor
		~GeneradorLlamadas(); // Destructor
		virtual string className() const {return ATOMIC_MODEL_NAME;}
	
	protected:
		Model &initFunction();	
		Model &externalFunction( const ExternalMessage & );
		Model &internalFunction( const InternalMessage & );
		Model &outputFunction( const CollectMessage & );
	
	private:
		// [(!) TODO: declare ports, distributions and other private varibles here]
		/***********      Example declarations   **********************************/
		// const Port &in;	// this is an input port named 'in'
		// Port &out ;   	// this is an output port named 'out'
		// Distribution *dist ;
		// Distribution &distribution()	{ return *dist; }
		/**************************************************************************/
	
		// [(!) declare common variables]
		// Lifetime programmed since the last state transition to the next planned internal transition.
		VTime sigma;
		
		// Time elapsed since the last state transition until now
		VTime elapsed;
		
		// Time remaining to complete the last programmed Lifetime
		VTime timeLeft;	
};	// class GeneradorLlamadas


#endif   //__GENERADORLLAMADAS_H 
