from __future__ import annotations

import itertools
import tkinter as tk
from tkinter import messagebox, ttk


def calcular_inventario_backorder(demanda_t, suministro_t):
    inventario = []
    backorder = []
    inv_prev = 0
    bo_prev = 0
    for d, q in zip(demanda_t, suministro_t):
        disponible = inv_prev + q
        requerido = d + bo_prev
        if disponible >= requerido:
            inv = disponible - requerido
            bo = 0
        else:
            inv = 0
            bo = requerido - disponible
        inventario.append(inv)
        backorder.append(bo)
        inv_prev, bo_prev = inv, bo
    return inventario, backorder


def resolver_modelo_lotes_fijos(datos):
    """Búsqueda exacta por enumeración para problemas pequeños.

    Replica la estructura del artículo: costo de compra por lotes fijos + costo de gestión
    de proveedor por período + costos de inventario y backorder a lo largo del horizonte.
    """

    S = datos["proveedores"]
    W = datos["articulos"]
    T = datos["periodos"]

    demanda = datos["demanda"]  # [w][t]
    costo_compra = datos["costo_compra"]  # [s][w]
    lote = datos["lote"]  # [s][w]
    capacidad = datos["capacidad"]  # [s][t] en unidades
    costo_gestion = datos["costo_gestion"]  # [s][t]
    costo_inv = datos["costo_inventario"]  # [w]
    costo_bo = datos["costo_backorder"]  # [w]

    variables = []
    max_lotes = {}
    for s in range(S):
        for w in range(W):
            if lote[s][w] <= 0:
                continue
            for t in range(T):
                m = capacidad[s][t] // lote[s][w]
                max_lotes[(s, w, t)] = m
                variables.append((s, w, t))

    mejor = None
    mejor_plan = None

    rangos = [range(max_lotes[v] + 1) for v in variables]

    for valores in itertools.product(*rangos):
        x = {v: val for v, val in zip(variables, valores)}

        # Capacidad por proveedor y período
        factible = True
        for s in range(S):
            for t in range(T):
                usado = sum(x.get((s, w, t), 0) * lote[s][w] for w in range(W) if lote[s][w] > 0)
                if usado > capacidad[s][t]:
                    factible = False
                    break
            if not factible:
                break
        if not factible:
            continue

        suministro = [[0] * T for _ in range(W)]
        for s, w, t in variables:
            suministro[w][t] += x[(s, w, t)] * lote[s][w]

        inventarios = []
        backorders = []
        for w in range(W):
            inv_w, bo_w = calcular_inventario_backorder(demanda[w], suministro[w])
            inventarios.append(inv_w)
            backorders.append(bo_w)

        costo_total = 0
        for s, w, t in variables:
            costo_total += x[(s, w, t)] * lote[s][w] * costo_compra[s][w]

        for s in range(S):
            for t in range(T):
                activo = any(x.get((s, w, t), 0) > 0 for w in range(W))
                if activo:
                    costo_total += costo_gestion[s][t]

        for w in range(W):
            for t in range(T):
                costo_total += inventarios[w][t] * costo_inv[w]
                costo_total += backorders[w][t] * costo_bo[w]

        if mejor is None or costo_total < mejor:
            mejor = costo_total
            mejor_plan = (x, suministro, inventarios, backorders)

    if mejor_plan is None:
        raise ValueError("No se encontró una solución factible.")

    return mejor, mejor_plan


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador de proveedores - Lotes fijos")
        self.root.geometry("1100x780")

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        self.s_var = tk.IntVar(value=2)
        self.w_var = tk.IntVar(value=2)
        self.t_var = tk.IntVar(value=2)

        ttk.Label(top, text="Proveedores").grid(row=0, column=0)
        ttk.Entry(top, textvariable=self.s_var, width=8).grid(row=0, column=1, padx=8)
        ttk.Label(top, text="Artículos").grid(row=0, column=2)
        ttk.Entry(top, textvariable=self.w_var, width=8).grid(row=0, column=3, padx=8)
        ttk.Label(top, text="Períodos").grid(row=0, column=4)
        ttk.Entry(top, textvariable=self.t_var, width=8).grid(row=0, column=5, padx=8)
        ttk.Button(top, text="Generar formulario", command=self.generar).grid(row=0, column=6, padx=8)
        ttk.Button(top, text="Calcular óptimo", command=self.calcular).grid(row=0, column=7, padx=8)

        note = ttk.Label(
            root,
            text="Modelo tipo MILP del artículo (lotes fijos, gestión por proveedor/periodo, inventario y backorder). Recomendado para tamaños pequeños.",
            foreground="#0b5394",
            padding=(10, 4),
        )
        note.pack(fill="x")

        self.canvas = tk.Canvas(root)
        self.scroll = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.frm = ttk.Frame(self.canvas)
        self.frm.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.frm, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

        self.result = tk.Text(root, height=13)
        self.result.pack(fill="both", padx=10, pady=10)

        self.entries = {}
        self.generar()

    def matriz(self, titulo, rows, cols, pref):
        box = ttk.LabelFrame(self.frm, text=titulo, padding=6)
        box.pack(fill="x", padx=10, pady=6)
        for i in range(rows):
            for j in range(cols):
                e = ttk.Entry(box, width=7)
                e.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                e.insert(0, "0")
                self.entries[(pref, i, j)] = e
        for j in range(cols):
            ttk.Label(box, text=f"C{j+1}").grid(row=0, column=j + 1)
        for i in range(rows):
            ttk.Label(box, text=f"F{i+1}").grid(row=i + 1, column=0)

    def vector(self, titulo, n, pref):
        box = ttk.LabelFrame(self.frm, text=titulo, padding=6)
        box.pack(fill="x", padx=10, pady=6)
        for i in range(n):
            ttk.Label(box, text=f"{i+1}").grid(row=0, column=i)
            e = ttk.Entry(box, width=8)
            e.grid(row=1, column=i, padx=2, pady=2)
            e.insert(0, "0")
            self.entries[(pref, i, 0)] = e

    def generar(self):
        for child in self.frm.winfo_children():
            child.destroy()
        self.entries.clear()
        S, W, T = self.s_var.get(), self.w_var.get(), self.t_var.get()
        self.matriz("Demanda [artículo][periodo]", W, T, "dem")
        self.matriz("Costo compra unitario [proveedor][artículo]", S, W, "cc")
        self.matriz("Tamaño de lote [proveedor][artículo]", S, W, "lot")
        self.matriz("Capacidad [proveedor][periodo]", S, T, "cap")
        self.matriz("Costo gestión [proveedor][periodo]", S, T, "cg")
        self.vector("Costo inventario por artículo", W, "ci")
        self.vector("Costo backorder por artículo", W, "cb")

    def val(self, key):
        try:
            v = float(self.entries[key].get())
            if v < 0:
                raise ValueError
            return v
        except Exception:
            raise ValueError(f"Valor inválido en {key}")

    def calcular(self):
        try:
            S, W, T = self.s_var.get(), self.w_var.get(), self.t_var.get()
            datos = {
                "proveedores": S,
                "articulos": W,
                "periodos": T,
                "demanda": [[int(self.val(("dem", w, t))) for t in range(T)] for w in range(W)],
                "costo_compra": [[self.val(("cc", s, w)) for w in range(W)] for s in range(S)],
                "lote": [[int(self.val(("lot", s, w))) for w in range(W)] for s in range(S)],
                "capacidad": [[int(self.val(("cap", s, t))) for t in range(T)] for s in range(S)],
                "costo_gestion": [[self.val(("cg", s, t)) for t in range(T)] for s in range(S)],
                "costo_inventario": [self.val(("ci", w, 0)) for w in range(W)],
                "costo_backorder": [self.val(("cb", w, 0)) for w in range(W)],
            }
            for s in range(S):
                for w in range(W):
                    if datos["lote"][s][w] == 0:
                        raise ValueError("Los tamaños de lote deben ser mayores a 0.")

            costo, plan = resolver_modelo_lotes_fijos(datos)
            x, suministro, inv, bo = plan
            out = [f"Costo total óptimo: {costo:.2f}\n"]
            out.append("Lotes comprados x[s,w,t]:")
            for (s, w, t), val in sorted(x.items()):
                if val > 0:
                    out.append(f"  Proveedor {s+1}, Artículo {w+1}, Período {t+1}: {val} lotes")
            out.append("\nSuministro por artículo y período:")
            for w in range(W):
                out.append(f"  Artículo {w+1}: {suministro[w]}")
            out.append("Inventario final por período:")
            for w in range(W):
                out.append(f"  Artículo {w+1}: {inv[w]}")
            out.append("Backorder por período:")
            for w in range(W):
                out.append(f"  Artículo {w+1}: {bo[w]}")

            self.result.delete("1.0", tk.END)
            self.result.insert(tk.END, "\n".join(out))
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    App(root)
    root.mainloop()
