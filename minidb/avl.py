"""Árbol AVL propio (clave -> valor).

Invariante AVL: para todo nodo, |altura(izq) - altura(der)| <= 1.
Si una inserción/eliminación lo rompe, se corrige con rotaciones.
Por eso la altura es O(log n) y insertar/buscar/eliminar son O(log n).
"""


class Nodo:
    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izq = None
        self.der = None
        self.altura = 1


class AVL:
    def __init__(self, log=None):
        self.raiz = None
        self.tamano = 0
        self.log = log or (lambda msg: None)   # función para explicar pasos

    # ---------- utilidades de altura y balance ----------
    def _h(self, n):
        return n.altura if n else 0

    def _factor(self, n):
        return self._h(n.izq) - self._h(n.der) if n else 0

    def _actualizar(self, n):
        n.altura = 1 + max(self._h(n.izq), self._h(n.der))

    # ---------- rotaciones ----------
    def _rot_der(self, y):
        x = y.izq
        y.izq = x.der
        x.der = y
        self._actualizar(y)
        self._actualizar(x)
        return x

    def _rot_izq(self, x):
        y = x.der
        x.der = y.izq
        y.izq = x
        self._actualizar(x)
        self._actualizar(y)
        return y

    def _balancear(self, n):
        self._actualizar(n)
        f = self._factor(n)
        if f > 1:                                   # pesa a la izquierda
            if self._factor(n.izq) < 0:             # caso izquierda-derecha
                self.log(f"Rotación doble (izq-der) en nodo {n.clave}")
                n.izq = self._rot_izq(n.izq)
            else:
                self.log(f"Rotación simple a la derecha en nodo {n.clave}")
            return self._rot_der(n)
        if f < -1:                                  # pesa a la derecha
            if self._factor(n.der) > 0:             # caso derecha-izquierda
                self.log(f"Rotación doble (der-izq) en nodo {n.clave}")
                n.der = self._rot_der(n.der)
            else:
                self.log(f"Rotación simple a la izquierda en nodo {n.clave}")
            return self._rot_izq(n)
        return n

    # ---------- insertar ----------
    def insertar(self, clave, valor):
        self.log(f"Insertar clave {clave}")
        self.raiz = self._insertar(self.raiz, clave, valor)
        self.tamano += 1

    def _insertar(self, n, clave, valor):
        if n is None:
            self.log(f"Lugar vacío encontrado: creo nodo {clave}")
            return Nodo(clave, valor)
        if clave < n.clave:
            self.log(f"{clave} < {n.clave}: bajo por la izquierda")
            n.izq = self._insertar(n.izq, clave, valor)
        elif clave > n.clave:
            self.log(f"{clave} > {n.clave}: bajo por la derecha")
            n.der = self._insertar(n.der, clave, valor)
        else:
            raise KeyError(f"La clave {clave} ya existe")
        return self._balancear(n)

    # ---------- buscar ----------
    def buscar(self, clave):
        self.log(f"Buscar clave {clave}")
        n = self.raiz
        while n:
            if clave == n.clave:
                self.log(f"Encontrada en nodo {n.clave}")
                return n.valor
            self.log(f"{clave} {'<' if clave < n.clave else '>'} {n.clave}: "
                     f"voy a la {'izquierda' if clave < n.clave else 'derecha'}")
            n = n.izq if clave < n.clave else n.der
        self.log("No existe en el árbol")
        return None

    # ---------- eliminar ----------
    def eliminar(self, clave):
        self.log(f"Eliminar clave {clave}")
        self.raiz = self._eliminar(self.raiz, clave)
        self.tamano -= 1

    def _eliminar(self, n, clave):
        if n is None:
            raise KeyError(f"La clave {clave} no existe")
        if clave < n.clave:
            n.izq = self._eliminar(n.izq, clave)
        elif clave > n.clave:
            n.der = self._eliminar(n.der, clave)
        else:
            if n.izq is None or n.der is None:      # 0 o 1 hijo
                self.log(f"Nodo {n.clave} tiene 0 o 1 hijo: lo reemplazo por su hijo")
                return n.izq or n.der
            suc = n.der                              # 2 hijos: sucesor inorder
            while suc.izq:
                suc = suc.izq
            self.log(f"Nodo {n.clave} tiene 2 hijos: copio el sucesor {suc.clave}")
            n.clave, n.valor = suc.clave, suc.valor
            n.der = self._eliminar(n.der, suc.clave)
        return self._balancear(n)

    # ---------- recorridos ----------
    def inorder(self):
        """Devuelve (clave, valor) en orden ascendente."""
        def rec(n):
            if n:
                yield from rec(n.izq)
                yield n.clave, n.valor
                yield from rec(n.der)
        return rec(self.raiz)

    def rango(self, minimo=None, maximo=None):
        """Valores con minimo <= clave <= maximo (None = sin límite). O(log n + k)."""
        self.log(f"Búsqueda por rango [{minimo}, {maximo}] podando ramas")
        def rec(n):
            if n is None:
                return
            if minimo is None or n.clave > minimo:
                yield from rec(n.izq)
            if (minimo is None or n.clave >= minimo) and (maximo is None or n.clave <= maximo):
                yield n.clave, n.valor
            if maximo is None or n.clave < maximo:
                yield from rec(n.der)
        return rec(self.raiz)

    def altura(self):
        return self._h(self.raiz)

    def dibujar(self):
        """Dibuja el árbol girado 90°: raíz a la izquierda, derecha arriba."""
        lineas = []
        def rec(n, nivel):
            if n:
                rec(n.der, nivel + 1)
                lineas.append("      " * nivel + f"{n.clave} (h={n.altura})")
                rec(n.izq, nivel + 1)
        rec(self.raiz, 0)
        return "\n".join(lineas) if lineas else "(árbol vacío)"
