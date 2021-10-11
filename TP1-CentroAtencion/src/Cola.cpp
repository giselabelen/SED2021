/*
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

Cola::Cola( const string &name ) :
	Atomic( name )
	// TODO: add ports here if needed (Remember to add them to the .h file also). Each in a new line.
	// Ej:
	, entrada(addInputPort( "entrada" ))
	, liberar(addInputPort( "liberar" ))
    , salida(addOutputPort( "salida" ))
{}

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
*/

#include <string>
#include "Cola.h"
#include "message.h"
#include "parsimu.h"

using namespace std;

/*******************************************************************
* Nombre de la Funci¢n: Cola::Cola()
* Descripción: Constructor
********************************************************************/
Cola::Cola( const string &name ): Atomic( name )
                                , entrada( addInputPort( "entrada" ) )
	                              , liberar( addInputPort( "liberar" ) )
                                , salida( addOutputPort( "salida" ) )
                                , preparationTime( 0, 0, 0, 1 )
{
	string time( ParallelMainSimulator::Instance().getParameter( description(), "preparation" ) ) ;

	if( time != "" )
		preparationTime = time ;
}


/*******************************************************************
* Nombre de la Función: Cola::initFunction()
* Descripción: Función de Inicialización
********************************************************************/

Model &Cola::initFunction()
{
  llamadasEncoladas.clear();
  recienLibere = false;
  return *this ;
}


/*******************************************************************
* Nombre de la Función: Cola::externalFunction()
* Descripción: Maneja los eventos externos (nuevas solicitudes y aviso de "listo"
********************************************************************/

Model &Cola::externalFunction( const ExternalMessage &msg )
{
	if( msg.port() == entrada )                             	// Si entra una nueva petición
	{
		llamadasEncoladas.push_back( msg.value() ) ;             // Encolarla
	}

	if( msg.port() == liberar )                            // Si notifican condición "listo"
	{
    if ( recienLibere && !llamadasEncoladas.empty()) {
		    llamadasEncoladas.pop_front() ;                          // Eliminar ultima entraga de cola
        recienLibere = false;
    }
		if( !llamadasEncoladas.empty() ) {
			holdIn( AtomicState::active, preparationTime );
			// Programar siguiente envío
    }
	}

	return *this;
}

/*******************************************************************
* Nombre de la Función: Cola::internalFunction()
* Descripción: Pone el modelo en estado pasivo (esperando un "Done" o algo para enviar)
********************************************************************/
Model &Cola::internalFunction( const InternalMessage & )
{
	passivate();
	return *this ;
}


/*******************************************************************
* Nombre de la Función: Cola::outputFunction()
* Descripción: Envía solicitud al receptor
********************************************************************/
Model &Cola::outputFunction( const CollectMessage &msg )
{
	if( !llamadasEncoladas.empty() ) {   // Si la cola no está vacía, enviar primer elemento
		sendOutput( msg.time(), salida, *llamadasEncoladas.front() ) ;
    recienLibere = true;
  }
	return *this ;
}
