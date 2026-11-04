"""
Pinto Andrango Juan Francisco
Tarea Individual DG_S4: Formulación y Búsqueda Ciega en Espacios de Estados

"""

from collections import deque
from time import perf_counter
from typing import Callable, Dict, List, Optional, Set, Tuple


Estado = Tuple[int, int, bool]
Movimiento = Tuple[int, int]
Grafo = Dict[Estado, List[Estado]]
ResultadoBusqueda = Tuple[Optional[List[Estado]], int, int, int]

TOTAL_MISIONEROS = 3
TOTAL_CANIBALES = 3
IZQUIERDA = True
DERECHA = False

ESTADO_INICIAL: Estado = (3, 3, IZQUIERDA)
ESTADO_OBJETIVO: Estado = (0, 0, DERECHA)

# El bote debe transportar una o dos personas.
MOVIMIENTOS: Tuple[Movimiento, ...] = (
    (2, 0),  # dos misioneros
    (0, 2),  # dos caníbales
    (1, 1),  # un misionero y un caníbal
    (1, 0),  # un misionero
    (0, 1),  # un caníbal
)


def es_estado_valido(estado: Estado) -> bool:
    
    m_izq, c_izq, bote_izq = estado

    if type(bote_izq) is not bool:
        return False

    if not (0 <= m_izq <= TOTAL_MISIONEROS):
        return False
    if not (0 <= c_izq <= TOTAL_CANIBALES):
        return False

    m_der = TOTAL_MISIONEROS - m_izq
    c_der = TOTAL_CANIBALES - c_izq

    izquierda_segura = m_izq == 0 or m_izq >= c_izq
    derecha_segura = m_der == 0 or m_der >= c_der
    return izquierda_segura and derecha_segura


def generar_sucesores(estado: Estado) -> List[Estado]:
    
    m_izq, c_izq, bote_izq = estado
    sucesores: List[Estado] = []

    for m_bote, c_bote in MOVIMIENTOS:
        if bote_izq:
            nuevo_estado = (m_izq - m_bote, c_izq - c_bote, DERECHA)
        else:
            nuevo_estado = (m_izq + m_bote, c_izq + c_bote, IZQUIERDA)

        if es_estado_valido(nuevo_estado):
            sucesores.append(nuevo_estado)

    return sucesores


def construir_grafo(estado_inicial: Estado) -> Grafo:
    
    grafo: Grafo = {}
    pendientes = deque([estado_inicial])
    descubiertos: Set[Estado] = {estado_inicial}

    while pendientes:
        vertice = pendientes.popleft()
        vecinos = generar_sucesores(vertice)
        grafo[vertice] = vecinos

        for vecino in vecinos:
            if vecino not in descubiertos:
                descubiertos.add(vecino)
                pendientes.append(vecino)

    return grafo


def reconstruir_camino(
    padres: Dict[Estado, Optional[Estado]], objetivo: Estado
) -> List[Estado]:
    
    camino: List[Estado] = []
    actual: Optional[Estado] = objetivo

    while actual is not None:
        camino.append(actual)
        actual = padres[actual]

    camino.reverse()
    return camino


def buscar_bfs(inicio: Estado, objetivo: Estado) -> ResultadoBusqueda:

    if not es_estado_valido(inicio) or not es_estado_valido(objetivo):
        return None, 0, 0, 0

    frontera = deque([inicio])
    padres: Dict[Estado, Optional[Estado]] = {inicio: None}
    nodos_expandidos = 0
    aristas_evaluadas = 0

    while frontera:
        actual = frontera.popleft()

        if actual == objetivo:
            return reconstruir_camino(padres, actual), nodos_expandidos, len(padres), aristas_evaluadas

        nodos_expandidos += 1
        sucesores = generar_sucesores(actual)
        aristas_evaluadas += len(sucesores)
        for sucesor in sucesores:
            if sucesor not in padres:
                padres[sucesor] = actual
                frontera.append(sucesor)

    return None, nodos_expandidos, len(padres), aristas_evaluadas


def buscar_dfs(inicio: Estado, objetivo: Estado) -> ResultadoBusqueda:
    
    if not es_estado_valido(inicio) or not es_estado_valido(objetivo):
        return None, 0, 0, 0

    frontera = [inicio]
    padres: Dict[Estado, Optional[Estado]] = {inicio: None}
    nodos_expandidos = 0
    aristas_evaluadas = 0

    while frontera:
        actual = frontera.pop()

        if actual == objetivo:
            return reconstruir_camino(padres, actual), nodos_expandidos, len(padres), aristas_evaluadas

        nodos_expandidos += 1
        sucesores = generar_sucesores(actual)
        aristas_evaluadas += len(sucesores)
        for sucesor in reversed(sucesores):
            if sucesor not in padres:
                padres[sucesor] = actual
                frontera.append(sucesor)

    return None, nodos_expandidos, len(padres), aristas_evaluadas


def describir_viaje(origen: Estado, destino: Estado) -> str:

    m_movidos = abs(origen[0] - destino[0])
    c_movidos = abs(origen[1] - destino[1])
    direccion = "izquierda -> derecha" if origen[2] else "derecha -> izquierda"
    return f"{m_movidos} M y {c_movidos} C ({direccion})"


def mostrar_solucion(nombre: str, camino: Optional[List[Estado]]) -> None:

    print(f"\n{'=' * 18} {nombre} {'=' * 18}")

    if camino is None:
        print("No se encontró una solución.")
        return

    print("Estado: (misioneros_izq, canibales_izq, bote_izq)")
    print("        bote_izq: True = izquierda, False = derecha")
    print(f"Inicio: {camino[0]}")

    for numero, (origen, destino) in enumerate(zip(camino, camino[1:]), start=1):
        print(f"Viaje {numero:2}: {describir_viaje(origen, destino):35} -> {destino}")

    print(f"Total de viajes: {len(camino) - 1}")


def mostrar_grafo(grafo: Grafo) -> None:
    
    total_aristas = sum(len(vecinos) for vecinos in grafo.values())
    print(f"\n{'=' * 22} Canibales y misioneros  {'=' * 22}")
    print("Vertice = (misioneros_izq, canibales_izq, bote_izq)")
    print(f"Total de vertices alcanzables: {len(grafo)}")
    print(f"Total de aristas dirigidas:    {total_aristas}")
    print("\nLista de adyacencia (vertice -> vecinos conectados):")

    for numero, (vertice, vecinos) in enumerate(grafo.items(), start=1):
        print(f"V{numero:02} {vertice} -> {vecinos}")


def ejecutar_benchmark(
    algoritmo: Callable[[Estado, Estado], ResultadoBusqueda]
) -> Tuple[Optional[List[Estado]], int, int, int, float]:
   
    inicio_tiempo = perf_counter()
    camino, nodos_expandidos, vertices_visitados, aristas_evaluadas = algoritmo(
        ESTADO_INICIAL, ESTADO_OBJETIVO
    )
    tiempo = perf_counter() - inicio_tiempo
    return camino, nodos_expandidos, vertices_visitados, aristas_evaluadas, tiempo


def mostrar_tabla_comparativa(
    resultados: List[Tuple[str, Optional[List[Estado]], int, int, int, float]]
) -> None:
    
    print(f"\n{'=' * 20} Benchmarking Y Analisis {'=' * 20}")
    encabezado = (
        f"{'Algoritmo':<9} | {'Expandidos':>10} | {'Vertices':>8} | "
        f"{'Aristas':>7} | {'Tiempo (s)':>12} | {'Acciones':>8}"
    )
    print(encabezado)
    print("-" * len(encabezado))

    for nombre, camino, nodos, vertices, aristas, tiempo in resultados:
        acciones = len(camino) - 1 if camino is not None else 0
        print(
            f"{nombre:<9} | {nodos:>10} | {vertices:>8} | {aristas:>7} | "
            f"{tiempo:>12.9f} | {acciones:>8}"
        )

    print("\nNota: una accion corresponde a un viaje del bote.")
    print("Un nodo se cuenta como expandido cuando se generan sus sucesores.")
    print("Vertices indica estados descubiertos; aristas indica conexiones evaluadas.")


def main() -> None:
    grafo = construir_grafo(ESTADO_INICIAL)
    solucion_bfs, nodos_bfs, vertices_bfs, aristas_bfs, tiempo_bfs = ejecutar_benchmark(buscar_bfs)
    solucion_dfs, nodos_dfs, vertices_dfs, aristas_dfs, tiempo_dfs = ejecutar_benchmark(buscar_dfs)

    mostrar_grafo(grafo)
    mostrar_solucion("BFS", solucion_bfs)
    mostrar_solucion("DFS", solucion_dfs)
    mostrar_tabla_comparativa(
        [
            ("BFS", solucion_bfs, nodos_bfs, vertices_bfs, aristas_bfs, tiempo_bfs),
            ("DFS", solucion_dfs, nodos_dfs, vertices_dfs, aristas_dfs, tiempo_dfs),
        ]
    )


if __name__ == "__main__":
    main()


