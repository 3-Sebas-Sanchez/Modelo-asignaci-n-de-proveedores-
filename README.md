# Modelo-asignaci-n-de-proveedores-

Aplicación con **interfaz gráfica (Tkinter)** para planificar compras a proveedores con el enfoque del artículo:

**Ruiz Torres, Mendoza y Ablanedo Rosas (2013)** — selección y asignación a proveedores en caso de **lotes fijos**.

## Qué calcula

El modelo minimiza el costo total considerando:
- costo de compra unitario,
- costo de gestión por proveedor y período,
- tamaños de lote fijos,
- capacidad por proveedor y período,
- demanda por artículo y período,
- costo de inventario,
- costo de backorder.

## Método

Se implementa la estructura de decisión del modelo entero mixto del artículo (variables de lotes por proveedor-artículo-período, activación de proveedor por período e inventario/backorder), y se resuelve de forma exacta por enumeración para tamaños pequeños.

> Recomendación: usar instancias pequeñas o medianas para mantener tiempos de cómputo razonables.

## Ejecutar

```bash
python3 main.py
```

## Requisitos

- Python 3.9+
- Tkinter (incluido normalmente en instalaciones estándar de Python)
