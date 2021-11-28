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
#include "realfunc.h"

#include "GeneradorLlamadas.h" // Cambiar nombre, base header

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
GeneradorLlamadas::GeneradorLlamadas( const string &name ) : 
	Atomic( name ),
	parar(addInputPort( "parar" )),
	llamada(addOutputPort( "llamada" ))
{
  try {
		dist = Distribution::create( ParallelMainSimulator::Instance().getParameter( description(), "distribution" ) );
		MASSERT( dist ) ;
		for ( register int i = 0; i < dist->varCount(); i++ )
		{
			string parameter( ParallelMainSimulator::Instance().getParameter( description(), dist->getVar( i ) ) ) ;
			dist->setVar( i, str2Value( parameter ) ) ;
		}

		if( ParallelMainSimulator::Instance().existsParameter( description(), "initial" ) )
			initial = str2Int( ParallelMainSimulator::Instance().getParameter( description(), "initial" ) );
		else
			initial = 0;

		if( ParallelMainSimulator::Instance().existsParameter( description(), "increment" ) )
			increment = str2Int( ParallelMainSimulator::Instance().getParameter( description(), "increment" ) );
		else
			increment = 1;

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
Model &GeneradorLlamadas::initFunction()
{
	// [(!) Initialize common variables]
	this->elapsed  = VTime::Zero;
 	this->timeLeft = VTime::Inf;
 	// this->sigma    = VTime::Zero; // force an internal transition in t=0;

  this->estado = Estados::GENERANDO;
  this->pid = this->initial;
 	// set next transition
  	this->sigma = VTime(static_cast< float >(fabs(distribution().get())));

 	holdIn( AtomicState::active, this->sigma  ) ;
	return *this ;
}

/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &GeneradorLlamadas::externalFunction( const ExternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dext");
#endif
	//[(!) update common variables]
	this->sigma    = nextChange();
	this->elapsed  = msg.time()-lastChange();
 	this->timeLeft = this->sigma - this->elapsed;

	//TODO: implement the external function here.
 	// Remember you can use the msg object (mgs.port(), msg.value()) and you should set the next TA (you might use the holdIn method).
 	// EJ:
 	// if( msg.port() == in )
	//{
	//	// Do something
	//	holdIn( AtomicState::active, this->timeLeft );
	// }
  if (msg.port() == parar) {
      estado = Estados::PARADO;
      passivate();
  }
	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
* Description: This method executes when the TA has expired, right after the outputFunction has finished.
* The new state and TA should be set.
********************************************************************/
Model &GeneradorLlamadas::internalFunction( const InternalMessage &msg )
{
#if VERBOSE
	PRINT_TIMES("dint");
#endif
	this->sigma = VTime(static_cast< float >(fabs(distribution().get())));
	holdIn( AtomicState::active, this->sigma );
	return *this;
}

/*******************************************************************
* Function Name: outputFunction
* Description: This method executes when the TA has expired. After this method the internalFunction is called.
* Output values can be send through output ports
********************************************************************/
Model &GeneradorLlamadas::outputFunction( const CollectMessage &msg )
{
	//TODO: implement the output function here
	// remember you can use sendOutput(time, outputPort, value) function.
	// sendOutput( msg.time(), out, 1) ;
	// value could be a tuple with different number of elements:
	// Tuple<Real> out_value{Real(value), 0, 1};
	// sendOutput(msg.time(), out, out_value);
  int esCliente = (uniform(0.0, 1.0) > 0.5) ? 1 : 0;
  Tuple<Real> datos_tupla{static_cast<Real>(pid), static_cast<Real>(esCliente)};
  pid += increment;

  sendOutput(msg.time(), llamada, datos_tupla);

	return *this;
}

GeneradorLlamadas::~GeneradorLlamadas()
{
    delete dist;
}
