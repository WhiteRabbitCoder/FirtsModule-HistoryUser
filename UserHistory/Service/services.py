
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import os
import csv

# Determina un directorio base seguro dentro del proyecto
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BASE_INTERNA = os.path.join(_PROJECT_ROOT, "Data")

# Fallback al HOME si la interna no es escribible
_HOME_BASE = os.path.join(os.path.expanduser("~"), "UserHistory", "Data")

def _seleccionar_base() -> str:
    for cand in (_BASE_INTERNA, _HOME_BASE):
        try:
            os.makedirs(cand, exist_ok=True)
            test_path = os.path.join(cand, ".writable.test")
            with open(test_path, "w") as f:
                f.write("ok")
            os.remove(test_path)
            return cand
        except Exception:
            continue
    raise RuntimeError("No se encontró un directorio escribible para almacenar datos.")

BASE_DIR = _seleccionar_base()  # Directorio por defecto seguro

@dataclass
class Product:
    nombre: str
    precio: float
    cantidad: int
    def calcular_subtotal(self) -> float:
        return self.precio * self.cantidad

def _resolver_ruta(archivo: str | None, defecto: str = "inventario.csv") -> str:
    nombre = (archivo or "").strip() or defecto
    # Si el usuario da ruta relativa, se guarda bajo BASE_DIR
    if not os.path.isabs(nombre):
        nombre = os.path.join(BASE_DIR, nombre)
    # Si es absoluta, se intenta crear su directorio; si falla, se redirige a BASE_DIR
    try:
        os.makedirs(os.path.dirname(nombre), exist_ok=True)
    except PermissionError:
        nombre = os.path.join(BASE_DIR, os.path.basename(nombre))
        os.makedirs(os.path.dirname(nombre), exist_ok=True)
    return nombre

def agregar_producto(inventario: Dict[str, Product], nombre: str, precio: float, cantidad: int) -> bool:
    if nombre in inventario or precio < 0 or cantidad < 0:
        return False
    inventario[nombre] = Product(nombre, float(precio), int(cantidad))
    return True

def mostrar_inventario(inventario: Dict[str, Product]) -> None:
    if not inventario:
        print("Inventario vacío.")
        return
    print(f"{'Nombre':<20}{'Precio':>10}{'Cantidad':>12}{'Subtotal':>12}")
    print("-" * 56)
    for producto in inventario.values():
        subtotal = producto.calcular_subtotal()
        print(f"{producto.nombre:<20}{producto.precio:>10.2f}{producto.cantidad:>12d}{subtotal:>12.2f}")

def buscar_producto(inventario: Dict[str, Product], nombre: str) -> Optional[Product]:
    return inventario.get(nombre)

def actualizar_producto(inventario: Dict[str, Product], nombre: str,
                        nuevo_precio: Optional[float] = None,
                        nueva_cantidad: Optional[int] = None) -> bool:
    producto = buscar_producto(inventario, nombre)
    if not producto:
        return False
    actualizado = False
    if nuevo_precio is not None:
        if nuevo_precio < 0:
            return False
        producto.precio = float(nuevo_precio)
        actualizado = True
    if nueva_cantidad is not None:
        if nueva_cantidad < 0:
            return False
        producto.cantidad = int(nueva_cantidad)
        actualizado = True
    return actualizado

def eliminar_producto(inventario: Dict[str, Product], nombre: str) -> bool:
    if nombre in inventario:
        del inventario[nombre]
        return True
    return False

def calcular_estadisticas(inventario: Dict[str, Product]) -> Dict[str, object]:
    if not inventario:
        return {
            "unidades_totales": 0,
            "valor_total": 0.0,
            "producto_mas_caro": None,
            "producto_mayor_stock": None
        }
    productos = list(inventario.values())
    unidades_totales = sum(p.cantidad for p in productos)
    valor_total = sum(p.calcular_subtotal() for p in productos)
    mas_caro = max(productos, key=lambda p: p.precio)
    mayor_stock = max(productos, key=lambda p: p.cantidad)
    return {
        "unidades_totales": unidades_totales,
        "valor_total": valor_total,
        "producto_mas_caro": (mas_caro.nombre, mas_caro.precio),
        "producto_mayor_stock": (mayor_stock.nombre, mayor_stock.cantidad)
    }

def guardar_csv(inventario: Dict[str, Product], archivo: str | None = None) -> bool:
    ruta = _resolver_ruta(archivo)
    try:
        with open(ruta, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['nombre', 'precio', 'cantidad'])
            for p in inventario.values():
                writer.writerow([p.nombre, p.precio, p.cantidad])
        return True
    except IOError:
        return False

def cargar_csv(inventario: Dict[str, Product], archivo: str | None,
               reemplazar: bool, politica_precio: str) -> Tuple[bool, int, int, int]:
    ruta = _resolver_ruta(archivo)
    nuevos = actualizados = errores = 0
    inventario_temporal: Dict[str, Product] = {}
    try:
        with open(ruta, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    nombre = row['nombre'].strip()
                    precio = float(row['precio'])
                    cantidad = int(row['cantidad'])
                    if not nombre or precio < 0 or cantidad < 0:
                        raise ValueError()
                    if reemplazar:
                        inventario_temporal[nombre] = Product(nombre, precio, cantidad)
                        nuevos += 1
                    else:
                        if nombre in inventario:
                            inventario[nombre].cantidad += cantidad
                            if politica_precio == 'csv':
                                inventario[nombre].precio = precio
                            actualizados += 1
                        else:
                            inventario[nombre] = Product(nombre, precio, cantidad)
                            nuevos += 1
                except Exception:
                    errores += 1
        if reemplazar:
            inventario.clear()
            inventario.update(inventario_temporal)
        return True, nuevos, actualizados, errores
    except FileNotFoundError:
        return False, 0, 0, 0
    except IOError:
        return False, 0, 0, 0
