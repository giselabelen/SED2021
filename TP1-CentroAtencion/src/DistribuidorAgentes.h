#ifndef __DISTRIBUIDORAGENTES_H // cambiar nombre
#define __DISTRIBUIDORAGENTES_H // cambiar nombre

/** include files **/
#include <random>
#include "atomic.h"  // class Atomic
#include "VTime.h"

#define ATOMIC_MODEL_NAME "DistribuidorAgentes" // cambiar nombre

/** forward declarations **/
//TODO: add distribution class declaration here if needed
// Ej: class Distribution ;

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
};	// class DistribuidorAgentes


#endif   //__DISTRIBUIDORAGENTES_H 
