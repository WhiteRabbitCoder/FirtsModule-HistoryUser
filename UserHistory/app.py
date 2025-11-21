import sys
import os
sys.path.append("../../Utils")

from UserHistory.Service.services import (
    agregar_producto, mostrar_inventario, buscar_producto,
    actualizar_producto, eliminar_producto, calcular_estadisticas,
    guardar_csv, cargar_csv, BASE_DIR
)
from UserHistory.Utils.Decorators import color
from UserHistory.Utils.Validator import (
    is_valid_name, parse_positive_decimal, parse_positive_int, clean_string
)


def decorar_mensaje(texto: str, simbolo: str = "-", col: str = "reset") -> str:
    linea = simbolo * max(len(texto), 40)
    return f"\n{linea}\n{color(texto, col)}\n{linea}\n"


def pedir_nombre(prompt: str, inventario: dict | None = None, debe_existir: bool = False) -> str | None:
    while True:
        entrada = input(prompt).strip()
        if entrada == "":
            return None
        if not is_valid_name(entrada):
            print(color(" Nombre inválido. Debe tener 1-100 caracteres y no iniciar con dígito.", "red"))
            continue
        nombre = clean_string(entrada)
        if inventario is not None:
            if debe_existir and nombre not in inventario:
                print(color(f" El producto '{nombre}' no existe.", "red"))
                continue
            if not debe_existir and nombre in inventario:
                print(color(f" El producto '{nombre}' ya existe.", "red"))
                continue
        return nombre


def pedir_valor_numeric(prompt: str, parser, opcional: bool = False) -> int | float | None:
    while True:
        entrada = input(prompt).strip()
        if opcional and entrada == "":
            return None
        try:
            return parser(entrada)
        except ValueError as e:
            print(color(f" {e}", "red"))
        except Exception:
            print(color(" Valor inválido.", "red"))


def gestionar_agregar_producto(inventario: dict):
    """Gestiona la lógica para agregar un nuevo producto."""
    print(decorar_mensaje("Agregar Producto", "-", "blue"))
    nombre = pedir_nombre("Nombre del producto: ", inventario, debe_existir=False)
    if not nombre:
        print(color("\nOperación cancelada o nombre inválido.\n", "yellow"))
        return
    precio = pedir_valor_numeric("Precio: ", parse_positive_decimal)
    cantidad = pedir_valor_numeric("Cantidad: ", parse_positive_int)
    if agregar_producto(inventario, nombre, precio, cantidad):
        print(color("\n Producto agregado exitosamente.\n", "green"))
    else:
        print(color("\n Error al agregar producto.\n", "red"))


def gestionar_mostrar_inventario(inventario: dict):
    """Gestiona la lógica para mostrar el inventario."""
    print(decorar_mensaje("Inventario Actual", "-", "blue"))
    if not inventario:
        print(color("El inventario está vacío.\n", "yellow"))
    else:
        mostrar_inventario(inventario)
        input(color("\n\nPresiona cualquier tecla para continuar.", "green"))


def gestionar_buscar_producto(inventario: dict):
    """Gestiona la lógica para buscar un producto."""
    print(decorar_mensaje("Buscar Producto", "-", "blue"))
    if not inventario:
        print(color("El inventario está vacío. No hay productos para buscar.\n", "yellow"))
        return
    nombre = pedir_nombre("Nombre del producto: ", inventario, debe_existir=True)
    if not nombre:
        print(color("\nOperación cancelada o producto no encontrado.\n", "yellow"))
        return
    producto = buscar_producto(inventario, nombre)
    if producto:
        print(color(
            f"\n Encontrado: {producto.nombre} | Precio: ${producto.precio:.2f} | "
            f"Cantidad: {producto.cantidad} | Subtotal: ${producto.calcular_subtotal():.2f}\n", "green"
        ))
    else:
        print(color(" Producto no encontrado.\n", "yellow"))


def gestionar_actualizar_producto(inventario: dict):
    """Gestiona la lógica para actualizar un producto."""
    print(decorar_mensaje("Actualizar Producto", "-", "blue"))
    if not inventario:
        print(color("El inventario está vacío. No hay productos para actualizar.\n", "yellow"))
        return
    nombre = pedir_nombre("Nombre del producto: ", inventario, debe_existir=True)
    if not nombre:
        print(color("\nOperación cancelada o producto no encontrado.\n", "yellow"))
        return

    producto_actual = buscar_producto(inventario, nombre)
    print(color(f" Precio actual: ${producto_actual.precio:.2f} | Cantidad actual: {producto_actual.cantidad} uds\n",
                "cyan"))
    nuevo_precio = pedir_valor_numeric(f"Nuevo precio (Enter para omitir): ", parse_positive_decimal, opcional=True)
    nueva_cantidad = pedir_valor_numeric(f"Nueva cantidad (Enter para omitir): ", parse_positive_int, opcional=True)

    if actualizar_producto(inventario, nombre, nuevo_precio, nueva_cantidad):
        print(color("\n Producto actualizado.\n", "green"))
    else:
        print(color("\n No se proporcionaron nuevos datos para actualizar.\n", "yellow"))


def gestionar_eliminar_producto(inventario: dict):
    """Gestiona la lógica para eliminar un producto."""
    print(decorar_mensaje("Eliminar Producto", "-", "blue"))
    if not inventario:
        print(color("El inventario está vacío. No hay productos para eliminar.\n", "yellow"))
        return
    nombre = pedir_nombre("Nombre del producto: ", inventario, debe_existir=True)
    if not nombre:
        print(color("\nOperación cancelada o producto no encontrado.\n", "yellow"))
        return
    if eliminar_producto(inventario, nombre):
        print(color("\n Producto eliminado.\n", "green"))
    else:
        print(color("\n Error al eliminar.\n", "red"))


def gestionar_estadisticas(inventario: dict):
    """Gestiona la lógica para mostrar estadísticas."""
    print(decorar_mensaje("ESTADÍSTICAS DEL INVENTARIO", "=", "magenta"))
    if not inventario:
        print(color("El inventario está vacío. No se pueden calcular estadísticas.\n", "yellow"))
        return
    stats = calcular_estadisticas(inventario)
    print("Unidades totales: " + color(str(stats['unidades_totales']), "cyan"))
    print("Valor total: " + color(f"${stats['valor_total']:.2f}", "green"))
    if stats["producto_mas_caro"]:
        n, pr = stats["producto_mas_caro"]
        print(f"Producto más caro: {color(n, 'yellow')} (${pr:.2f})")
    if stats["producto_mayor_stock"]:
        n, c = stats["producto_mayor_stock"]
        print(f"Mayor stock: {color(n, 'yellow')} ({c} uds)")
    print("\n" + "=" * 40 + "\n")


def gestionar_guardar_csv(inventario: dict):
    print(decorar_mensaje("Guardar Inventario", "-", "blue"))
    if not inventario:
        print(color("El inventario está vacío. No hay nada que guardar.\n", "yellow"))
        return
    entrada = input(f"Nombre de archivo (Enter para '{os.path.join(BASE_DIR, 'inventario.csv')}'): ").strip()
    archivo = entrada if entrada else None
    if guardar_csv(inventario, archivo):
        ruta_final = os.path.join(BASE_DIR, 'inventario.csv') if archivo is None else archivo
        if not os.path.isabs(ruta_final):
            ruta_final = os.path.join(BASE_DIR, ruta_final)
        print(color(f"\n Inventario guardado en '{ruta_final}'.\n", "green"))
    else:
        print(color("\n Error al guardar el archivo.\n", "red"))


def gestionar_cargar_csv(inventario: dict):
    print(decorar_mensaje("Cargar Inventario", "-", "blue"))
    entrada = input(f"Nombre de archivo (Enter para '{os.path.join(BASE_DIR, 'inventario.csv')}'): ").strip()
    archivo = entrada if entrada else None

    # Resolución previa para mostrar errores tempranos
    from UserHistory.Service.services import _resolver_ruta
    ruta = _resolver_ruta(archivo)

    if not os.path.exists(ruta):
        print(color(f"\n El archivo '{ruta}' no fue encontrado.\n", "red"))
        return

    reemplazar = False
    politica_precio = 'existente'
    if inventario:
        while True:
            accion = input("¿Sobrescribir (S) o Fusionar (F)? [S/F]: ").strip().upper()
            if accion in ['S', 'F']:
                reemplazar = (accion == 'S')
                break
            print(color("Opción no válida.", "red"))
        if not reemplazar:
            while True:
                pol = input("Precio (C)SV o (E)xistente? [C/E]: ").strip().upper()
                if pol in ['C', 'E']:
                    politica_precio = 'csv' if pol == 'C' else 'existente'
                    break
                print(color("Opción no válida.", "red"))

    exito, nuevos, actualizados, errores = cargar_csv(inventario, archivo, reemplazar, politica_precio)
    if not exito:
        print(color(f"\n Error al procesar '{ruta}'.\n", "red"))
        return

    print(color(f"\n--- Resumen de Carga ({'Reemplazo' if reemplazar else 'Fusión'}) ---", "cyan"))
    print(f"Archivo: '{ruta}'")
    if nuevos: print(color(f"Productos nuevos: {nuevos}", "green"))
    if actualizados: print(color(f"Actualizados: {actualizados}", "yellow"))
    if errores: print(color(f"Filas con error: {errores}", "red"))
    if not (nuevos or actualizados): print(color("Sin cambios.", "yellow"))
    print(color("----------------------------------\n", "cyan"))

def mostrar_menu():
    print(decorar_mensaje("MENÚ INVENTARIO", "=", "cyan"))
    print("1. Agregar producto")
    print("2. Mostrar inventario")
    print("3. Buscar producto")
    print("4. Actualizar producto")
    print("5. Eliminar producto")
    print("6. Estadísticas")
    print("7. Guardar CSV")
    print("8. Cargar CSV")
    print("9. Salir")
    print("=" * 40 + "\n")


def main():
    inventario = {}
    opciones = {
        "1": gestionar_agregar_producto,
        "2": gestionar_mostrar_inventario,
        "3": gestionar_buscar_producto,
        "4": gestionar_actualizar_producto,
        "5": gestionar_eliminar_producto,
        "6": gestionar_estadisticas,
        "7": gestionar_guardar_csv,
        "8": gestionar_cargar_csv,
    }
    while True:
        try:
            mostrar_menu()
            opcion = input(color("Selecciona una opción (1-9): ", "yellow")).strip()

            if opcion == "9":
                print(decorar_mensaje("¡Hasta pronto!", "-", "blue"))
                break

            accion = opciones.get(opcion)
            if accion:
                accion(inventario)
            else:
                print(color(" Opción inválida. Selecciona 1-9.\n", "red"))

        except KeyboardInterrupt:
            print(color("\n Operación cancelada. Saliendo...\n", "yellow"))
            break
        except Exception as e:
            print(color(f"\n Error inesperado: {e}\n", "red"))


if __name__ == "__main__":
    main()