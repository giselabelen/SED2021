/** include files **/
#include <random>
#include <string>
#include <stdlib.h>
#include <time.h>

#include "message.h" // class ExternalMessage, InternalMessage
#include "parsimu.h" // ParallelMainSimulator::Instance().getParameter( ... )
#include "real.h"
#include "tuple_value.h"
#include "distri.h"        // class Distribution
#include "strutil.h"

#include "Cola.h" // Cambiar nombre, base header

using namespace std;

#define VERBOSE true

#define PRINT_TIMES(f) {\
	VTime timeleft = nextChange();\
	VTime elapsed  = msg.time() - lastChange();\
	VTime sigma    = elapsed + timeleft;\
	cout << f << "@" << msg.time() <<\
		" - timeleft: " << timeleft <<\
		" - elapsed: " << elapsed <<\
		" - sigma: " << sigma << endl;\
}

/** public functions **/

/*******************************************************************
* Function Name: [#MODEL_NAME#]
* Description: constructor
********************************************************************/
Cola::Cola( const string &name ) :
	Atomic( name )
	// TODO: add ports here if needed (Remember to add them to the .h file also). Each in a new line.
	// Ej:
	, entrada(addInputPort( "entrada" ))
	, liberar(addInputPort( "liberar" ))
    , salida(addOutputPort( "salida" ))
{}

/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &Cola::initFunction()
{
	// [(!) Initialize common variables]
    estado = Estados::VACIA;
    hayPedido = false;
    sigEstado = false;
 	// set next transition
    passivate();
	return *this ;
}

/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &Cola::externalFunction( const ExternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dext");
#endif
	//[(!) update common variables]
    if (msg.port() == entrada) {
        llamadasEncoladas.push_back(msg.value());
        if (hayPedido) {
            estado = Estados::LIBERANDO;
            hayPedido = false;
            holdIn( AtomicState::active, VTime(0.0) );
        } else {
            estado = Estados::ENCOLANDO;
            passivate();
        }
    } else {
        if (estado == Estados::ENCOLANDO) {
            estado = Estados::LIBERANDO;
            holdIn( AtomicState::active, VTime(0.0) );
        }
        if (estado == Estados::VACIA) {
            hayPedido = true;
            passivate();
        }
    }
	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
* Description: This method executes when the TA has expired, right after the outputFunction has finished.
* The new state and TA should be set.
********************************************************************/
Model &Cola::internalFunction( const InternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dint");
#endif
	if (estado == Estados::LIBERANDO) {
        if (sigEstado) {
            estado = Estados::ENCOLANDO;
        } else {
            estado = Estados::VACIA;
        }
    }
    passivate();
	return *this;

}

/*******************************************************************
* Function Name: outputFunction
* Description: This method executes when the TA has expired. After this method the internalFunction is called.
* Output values can be send through output ports
********************************************************************/
Model &Cola::outputFunction( const CollectMessage &msg )
{
    auto llamada = llamadasEncoladas.front();
    sigEstado = !llamadasEncoladas.empty();
    sendOutput(msg.time(), salida, *llamada);
    llamadasEncoladas.pop_front();
    return *this;
}

Cola::~Cola()
{
    llamadasEncoladas.clear();
}
