/*
#ifndef __COLA_H // cambiar nombre
#define __COLA_H // cambiar nombre

#include <random>
#include "atomic.h"  // class Atomic
#include "VTime.h"

#define ATOMIC_MODEL_NAME "Cola" // cambiar nombre

class Cola: public Atomic {
	public:
		Cola( const string &name = ATOMIC_MODEL_NAME ); // Default constructor
		~Cola(); // Destructor
		virtual string className() const {return ATOMIC_MODEL_NAME;}
	protected:
		Model &initFunction();
		Model &externalFunction( const ExternalMessage & );
		Model &internalFunction( const InternalMessage & );
		Model &outputFunction( const CollectMessage & );
	private:
		// [(!) TODO: declare ports, distributions and other private varibles here]
		const Port &entrada, &liberar;
		Port &salida;
        enum Estados {
            ENCOLANDO,
            VACIA,
            LIBERANDO
        };
        Estados estado;
        bool hayPedido;
        list<value_ptr> llamadasEncoladas;
        bool sigEstado;
};	// class Cola
#endif   //__COLA_H */

#ifndef __COLA_H
#define __COLA_H

#include <list>
#include "atomic.h"     	// class Atomic
#include "atomicstate.h"	//
#include "value.h"
#include "VTime.h"

#define QUEUE_MODEL_NAME "Cola"

class Cola : public Atomic
{
public:
	Cola( const std::string &name = "Cola" );
	virtual std::string className() const {  return "Cola" ;}
protected:
	Model &initFunction();
	Model &externalFunction( const ExternalMessage & );
	Model &internalFunction( const InternalMessage & );
	Model &outputFunction( const CollectMessage & );
private:
  const Port &entrada, &liberar;
  Port &salida;
  bool recienLibere;

  // Estados estado;
  // bool hayPedido;
  list<value_ptr> llamadasEncoladas;
  // bool sigEstado;

	VTime preparationTime;
};	// class Cola
#endif   //__COLA_H


