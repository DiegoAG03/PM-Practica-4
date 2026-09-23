# Práctica 4 - Los cinco filósofos

Implementación en Python del problema clásico de los cinco filósofos de Edsger W. Dijkstra para la asignatura de Procesadores Multinúcleo.

La práctica estudia problemas de sincronización en programación concurrente, principalmente condiciones de carrera, `deadlock` e inanición (`starvation`). La versión final del programa integra las soluciones desarrolladas en los experimentos 1, 2 y 3 de la práctica.

## Objetivo

Simular cinco filósofos que compiten por cinco tenedores compartidos y aplicar mecanismos de sincronización que permitan:

- Garantizar exclusión mutua sobre cada tenedor.
- Evitar el `deadlock` producido cuando los filósofos retienen un recurso mientras esperan otro.
- Representar distintos niveles de hambre de cada filósofo.
- Incorporar una política de prioridad para reducir el riesgo de `starvation`.
- Mantener concurrencia entre filósofos no adyacentes cuando utilizan pares de tenedores diferentes.

## Modelo

Cada filósofo se implementa como un hilo mediante `threading.Thread` y cada tenedor como un semáforo binario `Semaphore(1)`.

Para un filósofo `Pi`, los recursos necesarios para comer son:

- Tenedor izquierdo: `Fi`.
- Tenedor derecho: `F(i+1)`.

Con cinco filósofos, la asignación queda como `P0 -> F0,F1`, `P1 -> F1,F2`, ..., `P4 -> F4,F0`.

## Solución implementada

### Prevención de deadlock

Los tenedores se intentan adquirir sin bloqueo indefinido. Si un filósofo obtiene el primer tenedor pero no puede adquirir el segundo, libera el primero antes de volver a intentarlo. De esta manera se rompe la condición de retención y espera necesaria para formar el ciclo de `deadlock`.

### Niveles de hambre

La simulación considera cinco niveles:

1. `CRAVING` - Antojadizo.
2. `HUNGRY` - Con apetito.
3. `UNCOMFORTABLY_HUNGRY` - Ávido.
4. `VERY_HUNGRY` - Hambriento.
5. `STARVING` - Famélico.

Cuando un filósofo debe ceder un tenedor después de un intento fallido, su nivel de hambre aumenta. Después de comer y pensar, el nivel vuelve a `CRAVING`.

### Política de prioridad

Para evitar que un filósofo sea postergado indefinidamente, la versión final utiliza dos criterios de prioridad entre filósofos vecinos:

1. Tiene prioridad el filósofo con mayor nivel de hambre.
2. En caso de empate, tiene prioridad el que lleva más tiempo esperando.

Las variables que representan la cola de espera se protegen mediante un semáforo adicional (`priority_mutex`). Además, antes de intentar adquirir los tenedores se comprueba si alguno de los vecinos está comiendo; en ese caso el filósofo espera sin apropiarse innecesariamente de recursos.

## Requisitos

- Python 3.
- Sistema operativo compatible con los módulos estándar de `threading` de Python. La práctica fue desarrollada y probada en Linux.
- No se requieren paquetes externos.

## Ejecución

```bash
python3 philosophers.py
```

La simulación se ejecuta durante un máximo de 15 segundos.

## Autor

Diego Ambrosio González  
Procesadores Multinúcleo - Práctica 4