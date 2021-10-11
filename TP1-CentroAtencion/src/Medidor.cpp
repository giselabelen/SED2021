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

#include "Medidor.h" // Cambiar nombre, base header

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
Medidor::Medidor( const string &name ) : 
	Atomic( name )
	, entrante(addInputPort( "entrante" ))
	, atendida(addInputPort( "atendida" ))
	, finalizada(addInputPort( "finalizada" ))
	, mediciones(addOutputPort( "mediciones" ))
{
  periodo = VTime(str2Value( ParallelMainSimulator::Instance().getParameter( description(), "periodo"))) ;
}

/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &Medidor::initFunction()
{
	// [(!) Initialize common variables]
	this->elapsed  = VTime::Zero;
 	this->timeLeft = VTime::Inf;
 	this->sigma = periodo;

 	// set next transition
 	holdIn( AtomicState::active, this->sigma  ) ;
	return *this ;
}

/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &Medidor::externalFunction( const ExternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dext");
#endif
	//[(!) update common variables]
	this->sigma    = nextChange();
	this->elapsed  = msg.time()-lastChange();
 	this->timeLeft = this->sigma - this->elapsed;

  if (msg.port() == entrante) {
    Tuple<Real> llamada = *dynamic_pointer_cast<Tuple<Real>>(msg.value());
    unsigned int id = static_cast<unsigned int>(llamada[0].value());
    bool esCliente = llamada[1] == 1.0;
    entrantesXTiempo[id] = {msg.time(), esCliente};
    holdIn( AtomicState::active, this->timeLeft );
  }
  else if (msg.port() == atendida) {
    Tuple<Real> llamada = *dynamic_pointer_cast<Tuple<Real>>(msg.value());
    unsigned int id = static_cast<unsigned int>(llamada[0].value());
    bool esCliente = llamada[1] == 1.0;
    atendidasXTiempo[id] = {msg.time(), esCliente};
    holdIn( AtomicState::active, this->timeLeft );
  }
  else  if (msg.port() == finalizada) {
    Tuple<Real> llamada = *dynamic_pointer_cast<Tuple<Real>>(msg.value());
    unsigned int id = static_cast<unsigned int>(llamada[0].value());
    bool esCliente = llamada[1] == 1.0;
    finalizadasXTiempo[id] = {msg.time(), esCliente};
    holdIn( AtomicState::active, this->timeLeft );
  } else {
    MASSERT(false);
  }
	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
* Description: This method executes when the TA has expired, right after the outputFunction has finished.
* The new state and TA should be set.
********************************************************************/
Model &Medidor::internalFunction( const InternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dint");
#endif
  entrantesXTiempo.clear();
  atendidasXTiempo.clear();
  finalizadasXTiempo.clear();
  this->sigma = periodo;
	holdIn( AtomicState::active, this->sigma );
	return *this;

}

/*******************************************************************
* Function Name: outputFunction
* Description: This method executes when the TA has expired. After this method the internalFunction is called.
* Output values can be send through output ports
********************************************************************/
Model &Medidor::outputFunction( const CollectMessage &msg )
{
  Real sumaAtendidas(0.0);
  Real maxAtendidas(0.0);
  for (const auto& kv : atendidasXTiempo) {
    VTime t = kv.second.timestamp - entrantesXTiempo[kv.first].timestamp;
    sumaAtendidas = sumaAtendidas + Real(t.asSecs());
    if (Real(t.asSecs()) > maxAtendidas) {
      maxAtendidas = Real(t.asSecs());
    }
  }
  Real promedioAtendidas(0.0);
  if (!atendidasXTiempo.empty()) {
    promedioAtendidas = sumaAtendidas / Real(atendidasXTiempo.size());
  }

  Real sumaFinalizadas(0.0);
  Real maxFinalizadas(0.0);
  for (const auto& kv : finalizadasXTiempo) {
    VTime t = kv.second.timestamp - entrantesXTiempo[kv.first].timestamp;
    sumaFinalizadas = sumaFinalizadas + Real(t.asSecs());
    if (Real(t.asSecs()) > maxFinalizadas) {
      maxFinalizadas = Real(t.asSecs());
    }
  }
  Real promedioFinalizadas(0.0);
  if (!finalizadasXTiempo.empty()) {
    promedioFinalizadas = sumaFinalizadas / Real(finalizadasXTiempo.size());
  }

  Tuple<Real> m{promedioAtendidas, maxAtendidas, promedioFinalizadas, maxFinalizadas};
  sendOutput(msg.time(), mediciones, m);

	return *this;

}

Medidor::~Medidor()
{
}
