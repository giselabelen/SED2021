#ifndef __MEDIDOR_H // cambiar nombre
#define __MEDIDOR_H // cambiar nombre

/** include files **/
#include <random>
#include <map>
#include "atomic.h"  // class Atomic
#include "VTime.h"

#define ATOMIC_MODEL_NAME "Medidor" // cambiar nombre

/** declarations **/
class Medidor: public Atomic {
	public:
		Medidor( const string &name = ATOMIC_MODEL_NAME ); // Default constructor
		~Medidor(); // Destructor
		virtual string className() const {return ATOMIC_MODEL_NAME;}
	protected:
		Model &initFunction();
		Model &externalFunction( const ExternalMessage & );
		Model &internalFunction( const InternalMessage & );
		Model &outputFunction( const CollectMessage & );
	private:
    const Port &entrante, &atendida, &finalizada;
		Port &mediciones;
		/**************************************************************************/
		// [(!) declare common variables]
    struct DatosLlamada {
      VTime timestamp;
      bool esCliente;
    };
    VTime periodo;
    std::map<unsigned int, DatosLlamada> entrantesXTiempo;
    std::map<unsigned int, DatosLlamada> atendidasXTiempo;
    std::map<unsigned int, DatosLlamada> finalizadasXTiempo;

		// Lifetime programmed since the last state transition to the next planned internal transition.
		VTime sigma;
		// Time elapsed since the last state transition until now
		VTime elapsed;
		// Time remaining to complete the last programmed Lifetime
		VTime timeLeft;
};	// class Medidor


#endif   //__MEDIDOR_H 
