from __future__ import annotations

import heapq
from dataclasses import dataclass


@dataclass
class Edge:
    to: int
    rev: int
    capacity: int
    cost: int


class MinCostMaxFlow:
    def __init__(self, n: int) -> None:
        self.n = n
        self.graph: list[list[Edge]] = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int, capacity: int, cost: int) -> None:
        forward = Edge(v, len(self.graph[v]), capacity, cost)
        backward = Edge(u, len(self.graph[u]), 0, -cost)
        self.graph[u].append(forward)
        self.graph[v].append(backward)

    def min_cost_flow(self, source: int, sink: int, max_flow: int) -> tuple[int, int]:
        n = self.n
        flow = 0
        cost = 0
        potential = [0] * n

        while flow < max_flow:
            dist = [float("inf")] * n
            prev_node = [-1] * n
            prev_edge = [-1] * n
            dist[source] = 0
            pq: list[tuple[float, int]] = [(0, source)]

            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue
                for i, edge in enumerate(self.graph[u]):
                    if edge.capacity <= 0:
                        continue
                    v = edge.to
                    new_dist = d + edge.cost + potential[u] - potential[v]
                    if new_dist < dist[v]:
                        dist[v] = new_dist
                        prev_node[v] = u
                        prev_edge[v] = i
                        heapq.heappush(pq, (new_dist, v))

            if dist[sink] == float("inf"):
                break

            for v in range(n):
                if dist[v] < float("inf"):
                    potential[v] += int(dist[v])

            add_flow = max_flow - flow
            v = sink
            while v != source:
                u = prev_node[v]
                edge_idx = prev_edge[v]
                add_flow = min(add_flow, self.graph[u][edge_idx].capacity)
                v = u

            v = sink
            while v != source:
                u = prev_node[v]
                edge_idx = prev_edge[v]
                edge = self.graph[u][edge_idx]
                edge.capacity -= add_flow
                rev = edge.rev
                self.graph[v][rev].capacity += add_flow
                cost += add_flow * edge.cost
                v = u

            flow += add_flow

        return flow, cost


def pedir_entero(mensaje: str, minimo: int = 0) -> int:
    while True:
        try:
            valor = int(input(mensaje))
            if valor < minimo:
                print(f"Ingresa un número mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Entrada inválida. Debe ser un número entero.")


def leer_matriz_costos(proveedores: int, articulos: int) -> list[list[int]]:
    print("\nIngrese la matriz de costos unitarios.")
    print("Cada fila corresponde a un proveedor y cada columna a un artículo.")
    matriz = []
    for i in range(proveedores):
        fila = []
        for j in range(articulos):
            costo = pedir_entero(f"Costo de proveedor {i + 1} para artículo {j + 1}: ", 0)
            fila.append(costo)
        matriz.append(fila)
    return matriz


def resolver_asignacion_optima(
    costos: list[list[int]],
    oferta: list[int],
    demanda: list[int],
) -> tuple[int, list[list[int]]]:
    p = len(oferta)
    a = len(demanda)

    source = 0
    prov_offset = 1
    art_offset = prov_offset + p
    sink = art_offset + a
    n_nodes = sink + 1

    mcmf = MinCostMaxFlow(n_nodes)

    for i, cap in enumerate(oferta):
        mcmf.add_edge(source, prov_offset + i, cap, 0)

    for i in range(p):
        for j in range(a):
            mcmf.add_edge(prov_offset + i, art_offset + j, 10**9, costos[i][j])

    for j, dem in enumerate(demanda):
        mcmf.add_edge(art_offset + j, sink, dem, 0)

    total_demanda = sum(demanda)
    flujo, costo = mcmf.min_cost_flow(source, sink, total_demanda)

    if flujo < total_demanda:
        raise ValueError("No existe solución factible con la oferta total ingresada.")

    asignacion = [[0 for _ in range(a)] for _ in range(p)]
    for i in range(p):
        u = prov_offset + i
        for edge in mcmf.graph[u]:
            if art_offset <= edge.to < sink:
                j = edge.to - art_offset
                reverse_edge = mcmf.graph[edge.to][edge.rev]
                asignacion[i][j] = reverse_edge.capacity

    return costo, asignacion


def main() -> None:
    print("=== Modelo de Asignación de Proveedores (Costo Mínimo) ===")

    proveedores = pedir_entero("Cantidad de proveedores: ", 1)
    articulos = pedir_entero("Cantidad de artículos: ", 1)

    oferta = []
    print("\nIngrese la capacidad (oferta) de cada proveedor:")
    for i in range(proveedores):
        oferta.append(pedir_entero(f"Oferta del proveedor {i + 1}: ", 0))

    demanda = []
    print("\nIngrese la demanda de cada artículo:")
    for j in range(articulos):
        demanda.append(pedir_entero(f"Demanda del artículo {j + 1}: ", 0))

    costos = leer_matriz_costos(proveedores, articulos)

    total_oferta = sum(oferta)
    total_demanda = sum(demanda)
    if total_oferta < total_demanda:
        print(
            "\nNo se puede satisfacer la demanda: "
            f"oferta total ({total_oferta}) < demanda total ({total_demanda})."
        )
        return

    if total_oferta > total_demanda:
        print(
            "\nAviso: la oferta total es mayor que la demanda total. "
            "El modelo dejará parte de la oferta sin usar."
        )

    try:
        costo_total, asignacion = resolver_asignacion_optima(costos, oferta, demanda)
    except ValueError as error:
        print(f"\nError: {error}")
        return

    print("\n=== Solución óptima encontrada ===")
    print(f"Costo total mínimo: {costo_total}")
    print("\nAsignación (unidades enviadas de proveedor i a artículo j):")

    encabezado = "          " + " ".join([f"Art{j+1:>6}" for j in range(articulos)])
    print(encabezado)
    for i in range(proveedores):
        fila = f"Prov{i+1:>3} -> " + " ".join([f"{asignacion[i][j]:>8}" for j in range(articulos)])
        print(fila)


if __name__ == "__main__":
    main()
