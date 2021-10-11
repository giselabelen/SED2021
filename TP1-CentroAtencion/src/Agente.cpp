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

#include "Agente.h" // Cambiar nombre, base header

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
* Function Name: [Agente]
* Description: constructor
********************************************************************/
Agente::Agente( const string &name ) :
	Atomic( name )
	, finalizada(addOutputPort( "finalizada" ))
	, pedido(addOutputPort( "pedido" ))
	, entrante(addInputPort( "entrante" ))
{
	id = str2Int( ParallelMainSimulator::Instance().getParameter( description(), "id" ) );

  dist = Distribution::create( ParallelMainSimulator::Instance().getParameter( description(), "distribution" ) );
  MASSERT( dist ) ;
  for ( register int i = 0; i < dist->varCount(); i++ ) {
			string parameter( ParallelMainSimulator::Instance().getParameter( description(), dist->getVar( i ) ) ) ;
			dist->setVar( i, str2Value( parameter ) ) ;
	}
}

/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &Agente::initFunction()
{
	// [(!) Initialize common variables]
 	t = VTime::Zero; // force an internal transition in t=0;
  estado = Estados::ATENDIENDO;
  llamada = Tuple<Real>({-1.0, -1.0});

 	// set next transition
 	holdIn( AtomicState::active, t ) ;
	return *this ;
}

/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &Agente::externalFunction( const ExternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dext");
#endif
	//[(!) update common variables]

  if (estado == Estados::PIDIENDO) {
    t = VTime(static_cast< float >(fabs(distribution().get())));
    estado = Estados::ATENDIENDO;
    llamada = *dynamic_pointer_cast<Tuple<Real>>(msg.value());

    holdIn( AtomicState::active, t );
  }

	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
* Description: This method executes when the TA has expired, right after the outputFunction has finished.
* The new state and TA should be set.
********************************************************************/
Model &Agente::internalFunction( const InternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dint");
#endif

  estado = Estados::PIDIENDO;
	passivate();
	return *this;
}

/*******************************************************************
* Function Name: outputFunction
* Description: This method executes when the TA has expired. After this method the internalFunction is called.
* Output values can be send through output ports
********************************************************************/
Model &Agente::outputFunction( const CollectMessage &msg )
{
  if (llamada[0] != -1.0) { // Me fijo si hay llamada que enviar
      sendOutput(msg.time(), finalizada, llamada);
  }
  sendOutput(msg.time(), pedido, id);

	return *this;
}

Agente::~Agente()
{
  delete dist;
}
