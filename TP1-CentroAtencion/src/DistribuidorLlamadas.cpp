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

#include "DistribuidorLlamadas.h" // Cambiar nombre, base header

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
DistribuidorLlamadas::DistribuidorLlamadas( const string &name ) :
	Atomic( name )
	, entrante(addInputPort("entrante"))
	, pedirLlamada(addOutputPort("pedirLlamada"))
	, clientes(addOutputPort("clientes"))
  , noClientes(addOutputPort("noClientes"))
{
  try {
		dist = Distribution::create( ParallelMainSimulator::Instance().getParameter( description(), "distribution" ) );
		MASSERT( dist ) ;
		for ( register int i = 0; i < dist->varCount(); i++ )
    {
      string parameter( ParallelMainSimulator::Instance().getParameter( description(), dist->getVar( i ) ) ) ;
      dist->setVar( i, str2Value( parameter ) ) ;
    }
	}
  catch( InvalidDistribution &e )	{
		e.addText( "The model " + description() + " has distribution problems!" ) ;
		e.print(cerr);
		MTHROW( e ) ;
	}
  catch( MException &e ) {
		MTHROW( e ) ;
	}
}

/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &DistribuidorLlamadas::initFunction()
{
 	this->sigma    = VTime::Zero; // force an internal transition in t=0;
  estado = Estados::PIDIENDO;
  llamada = Tuple<Real>({-1.0, -1.0});
 	// set next transition
 	holdIn( AtomicState::active, this->sigma  ) ;
	return *this ;
}

/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &DistribuidorLlamadas::externalFunction( const ExternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dext");
#endif
  if (msg.port() == entrante && estado == Estados::ESPERANDO) {
    estado = Estados::ENVIANDO;
    llamada = *dynamic_pointer_cast<Tuple<Real>>(msg.value());
    this->sigma = VTime(static_cast< float >(fabs(distribution().get())));
    holdIn( AtomicState::active, this->sigma );
  }

	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
* Description: This method executes when the TA has expired, right after the outputFunction has finished.
* The new state and TA should be set.
********************************************************************/
Model &DistribuidorLlamadas::internalFunction( const InternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dint");
#endif

  switch (estado) {
  case Estados::PIDIENDO:
    estado = Estados::ESPERANDO;
    passivate();
    break;
  case Estados::ENVIANDO:
    estado = Estados::PIDIENDO;
    this->sigma = VTime::Zero;
    holdIn( AtomicState::active, this->sigma );
    break;
  default:
    MASSERT(false);
    break;
  }
	return *this;
}

/*******************************************************************
* Function Name: outputFunction
* Description: This method executes when the TA has expired. After this method the internalFunction is called.
* Output values can be send through output ports
********************************************************************/
Model &DistribuidorLlamadas::outputFunction( const CollectMessage &msg )
{
	//TODO: implement the output function here
	// remember you can use sendOutput(time, outputPort, value) function.
	// sendOutput( msg.time(), out, 1) ;
	// value could be a tuple with different number of elements:
	// Tuple<Real> out_value{Real(value), 0, 1};
	// sendOutput(msg.time(), out, out_value);
  switch (estado) {
  case Estados::PIDIENDO:
    sendOutput(msg.time(), pedirLlamada, 1);
    break;
  case Estados::ENVIANDO:
    if (llamada[0] >= 0.0) { // Es llamada valida, la llamada inicial es invalida por lo que hay que descartarla
      if (llamada[1] == 0.0) {
        sendOutput(msg.time(), noClientes, llamada);
      } else {
        sendOutput(msg.time(), clientes, llamada);
      }
    }
    break;
  default:
    MASSERT(false);
  }
	return *this;

}

DistribuidorLlamadas::~DistribuidorLlamadas()
{
  delete dist;
}
