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

#include "DistribuidorAgentes.h" // Cambiar nombre, base header

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
DistribuidorAgentes::DistribuidorAgentes( const string &name ) : 
	Atomic( name )
	, pedido(addInputPort( "pedido" ))
	, entrante(addInputPort( "entrante" ))
	, pedirLlamada(addOutputPort( "pedirLlamada" ))
	, agente1(addOutputPort( "agente1" ))
	, agente2(addOutputPort( "agente2" ))
{}

/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &DistribuidorAgentes::initFunction()
{
  estado = Estados::DESOCUPADO;
  luegoDeEnviar = false;
  llamada = Tuple<Real>({-1.0, -1.0});

  passivate();
	return *this ;
}

/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &DistribuidorAgentes::externalFunction( const ExternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dext");
#endif
	//[(!) update common variables]

  if (msg.port() == pedido) {
    pedidosEnEspera.push_back(*dynamic_pointer_cast<Real>(msg.value()));
  }

  switch(estado) {
  case Estados::DESOCUPADO:
    {
      if (msg.port() == pedido) {
        estado = Estados::PIDIENDO;
        holdIn( AtomicState::active, VTime::Zero );
      }
    }
    break;
  case Estados::ESPERANDO:
    {
      if (msg.port() == entrante) {
        estado = Estados::ENVIANDO;
        llamada = *dynamic_pointer_cast<Tuple<Real>>(msg.value());
        holdIn( AtomicState::active, VTime::Zero );
      }
    }
    break;
  default:
    break;
  }

	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
* Description: This method executes when the TA has expired, right after the outputFunction has finished.
* The new state and TA should be set.
********************************************************************/
Model &DistribuidorAgentes::internalFunction( const InternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dint");
#endif

  switch(estado) {
  case Estados::PIDIENDO:
    {
      estado = Estados::ESPERANDO;
      passivate();
    }
    break;
  case Estados::ENVIANDO:
    {
      if (luegoDeEnviar) {
        estado = Estados::PIDIENDO;
        holdIn(AtomicState::active, VTime::Zero);
      } else {
        estado = Estados::DESOCUPADO;
        passivate();
      }
    }
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
Model &DistribuidorAgentes::outputFunction( const CollectMessage &msg )
{
  switch(estado) {
  case Estados::PIDIENDO:
    {
      if (pedidosEnEspera.empty()){
        MASSERT(false);
      }
      sendOutput(msg.time(), pedirLlamada, pedidosEnEspera.front());
    }
    break;
  case Estados::ENVIANDO:
    {
      if (pedidosEnEspera.empty()){
        MASSERT(false);
      }
      Real id_pedido = pedidosEnEspera.front();
      pedidosEnEspera.pop_front();
      if (id_pedido == 1.0) {
        sendOutput(msg.time(), agente1, llamada);
      } else {
        sendOutput(msg.time(), agente2, llamada);
      }
      luegoDeEnviar = pedidosEnEspera.empty();
    }
    break;
  default:
    MASSERT(false);
    break;
  }

	return *this;

}

DistribuidorAgentes::~DistribuidorAgentes()
{
}
