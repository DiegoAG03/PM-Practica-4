# Procesadores Multinúcleo
# Práctica 4 - Los cinco filósofos
# Alumno: Diego Ambrosio González

import sys
from time import sleep
from random import randint
from threading import Semaphore, Thread, Event

# Philosopher states
EATING = 0
HUNGRY = 1
THINKING = 2

# Hunger levels
CRAVING = 0
HUNGER_HUNGRY = 1
UNCOMFORTABLY_HUNGRY = 2
VERY_HUNGRY = 3
STARVING = 4

states = []
hunger = []
philosophers = []    # Threads
forks = []           # Forks

# Variables for the fair solution
waiting = []
waiting_order = []
order_counter = 0

# Protects the priority decision
priority_mutex = Semaphore(1)

# Stop the simulation when a philosopher starves
simulation_over = Event()

def right(p):
    return (p + 1) % len(philosophers)

def left(p):
    return (p + len(philosophers) - 1) % len(philosophers)

def take_fork(p, f, blocking=True):
    # Philosopher p tries to acquire fork f.
    # If blocking=True, the philosopher waits until the fork becomes available.
    # If blocking=False, the philosopher only tries to acquire the fork and returns immediately if it is not available.
    print(f'Philosopher {p} tries to take fork {f}')
    acquired = forks[f].acquire(blocking=blocking)
    if acquired:
        print(f'Philosopher {p} takes fork {f}')
    else:
        print(f'Philosopher {p} could not take fork {f}')
    return acquired

def put_fork(p, f):
    # Philosopher p releases fork f.
    forks[f].release()
    print(f'Philosopher {p} puts fork {f} down')

def hunger_name(level):
    hunger_levels = [
        'CRAVING',
        'HUNGRY',
        'UNCOMFORTABLY HUNGRY',
        'VERY HUNGRY',
        'STARVING'
        ]
    return hunger_levels[level]

def increase_hunger(p):
    if hunger[p] < STARVING:
        hunger[p] += 1
    print(f'Philosopher {p} is now {hunger_name(hunger[p])}')
    if hunger[p] == STARVING:
        print(f'Philosopher {p} has starved to death!')
        simulation_over.set()
        return True
    return False
    
def think(p):
    states[p] = THINKING
    print(f'Philosopher {p} is thinking')
    sleep(0.001 * randint(500, 1500))
    if simulation_over.is_set():
        return
    states[p] = HUNGRY
    hunger[p] = CRAVING
    print(f'Philosopher {p} finished thinking and is now {hunger_name(hunger[p])}')

def eat(p):
    states[p] = EATING
    print(f'Philosopher {p} is eating ({hunger_name(hunger[p])})')
    sleep(0.001 * randint(500, 1500))

def start_waiting(p):
    global order_counter
    priority_mutex.acquire()
    if not waiting[p]:
        waiting[p] = True
        waiting_order[p] = order_counter
        order_counter += 1
        print(f'Philosopher {p} enters waiting queue with order {waiting_order[p]}')
    priority_mutex.release()

def stop_waiting(p):
    priority_mutex.acquire()
    waiting[p] = False
    waiting_order[p] = -1
    priority_mutex.release()

def has_higher_priority(p, q):
    # True if philosopher p has higher priority than philosopher q.
    # First criterion: hunger.
    if hunger[p] > hunger[q]:
        return True
    if hunger[p] < hunger[q]:
        return False
    # Second criterion: waiting time.
    # Smaller order = longer waiting time.
    return (waiting_order[p] < waiting_order[q])

def has_priority(p):
    priority_mutex.acquire()
    left_p = left(p)
    right_p = right(p)
    for neighbor in (left_p, right_p):
        # Ignore neighbors that are not waiting.
        if not waiting[neighbor]:
            continue
        # If the neighbor has higher priority, philosopher p must wait.
        if has_higher_priority(neighbor, p):
            print(f'Philosopher {p} waits: philosopher {neighbor} has higher priority')
            priority_mutex.release()
            return False
    priority_mutex.release()
    return True

def neighbor_is_eating(p):
    left_p = left(p)
    right_p = right(p)
    return (states[left_p] == EATING or states[right_p] == EATING)

def philosopher(p):

    while not simulation_over.is_set():
        # Determine the two forks needed by philosopher p.
        left_fork = p
        right_fork = right(p)

        start_waiting(p)

        # Before touching any fork, check if a neighbor philosopher deserves priority.
        if not has_priority(p):
            # Simply wait and check priority again later.
            sleep(0.001 * randint(50, 150))
            continue

        # Check if one of the neighbors is currently eating.
        if neighbor_is_eating(p):
            print(f'Philosopher {p} waits because a neighbor is eating')
            sleep(0.001 * randint(50, 150))
            continue
        
        # Philosopher currently has priority.
        # Try to take the left fork.
        got_left_fork = take_fork(p, left_fork, blocking=False)
        if not got_left_fork:
            sleep(0.001 * randint(50, 150))
            continue

        got_right_fork = take_fork(p, right_fork, blocking=False)

        if got_right_fork:
            stop_waiting(p)
            eat(p)

            # Release both forks after eating.
            put_fork(p, right_fork)
            put_fork(p, left_fork)

            # Stop if another philosopher somehow reached STARVING.
            if simulation_over.is_set():
                break
            think(p)

        else:
            # Release the first fork to prevent deadlock.
            put_fork(p, left_fork)
            died = increase_hunger(p)
            if died:
                break
            sleep(0.001 * randint(50, 150))


def main(args):
    n = 5
    global states, hunger, philosophers, forks
    
    if len(args) > 1:
        n = int(args[1])
        
    for i in range(n):
        states.append(HUNGRY)      # Philosophers are initially hungry
        hunger.append(CRAVING)     # Start at the first hunger level
        waiting.append(False)
        waiting_order.append(-1)
        forks.append(Semaphore(1)) # Creates free fork (Semaphore in 1)
        philosophers.append(Thread(target=philosopher, args=[i]))
        
    for i in range(n):
        philosophers[i].start()
        
    # Run the simulation for a maximum of 15 seconds.
    # If STARVING occurs before 15 seconds, simulation_over will be activated immediately.
    simulation_over.wait(timeout=15)

    # If the 15 seconds elapsed without starvation, stop the simulation normally.
    if not simulation_over.is_set():
        print('\nSimulation time completed without starvation.')
        simulation_over.set()

    for i in range(n):
        philosophers[i].join()

    print('Simulation finished.')

if __name__ == '__main__':
    main(sys.argv)