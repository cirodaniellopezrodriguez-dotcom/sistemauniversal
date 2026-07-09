import flet as ft
import os
from datetime import datetime

def main(page: ft.Page):
    page.title = "Sistema Universal - Venta Mixta"
    page.scroll = "adaptive"

    ARCHIVO_VENTAS = "ventas_diarias.txt"

    # --- HEADER CORREGIDO PARA COMPATIBILIDAD TOTAL ---
    # Usamos Row con alignment=ft.MainAxisAlignment.CENTER
    # Esto evita el problema con el módulo 'alignment'
    header = ft.Container(
        content=ft.Row(
            controls=[ft.Text("NOMBRE DE TU TIENDA", size=30, weight="bold", color="white")],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor="blue",
        padding=20,
        border_radius=10,
    )
    # --------------------------------------------------

    catalogo_raw = [
        {"nombre": "Aceite de Oliva", "precio": 250, "tipo": "liquido"}, 
        {"nombre": "Jabón Líquido", "precio": 80, "tipo": "liquido"},
        {"nombre": "Shampoo", "precio": 120, "tipo": "liquido"}, {"nombre": "Suavizante", "precio": 60, "tipo": "liquido"},
        {"nombre": "Cloro", "precio": 30, "tipo": "liquido"}, {"nombre": "Detergente Ropa", "precio": 90, "tipo": "liquido"},
        {"nombre": "Desinfectante", "precio": 70, "tipo": "liquido"}, {"nombre": "Limpia Vidrios", "precio": 55, "tipo": "liquido"},
        {"nombre": "Alcohol", "precio": 100, "tipo": "liquido"}, {"nombre": "Gel Antibacterial", "precio": 150, "tipo": "liquido"},
        {"nombre": "Aromatizante", "precio": 110, "tipo": "liquido"}, {"nombre": "Jabón de Manos", "precio": 65, "tipo": "liquido"},
        {"nombre": "Desengrasante", "precio": 95, "tipo": "liquido"}, {"nombre": "Vinagre Limpieza", "precio": 40, "tipo": "liquido"},
        {"nombre": "Jabón Trastes", "precio": 50, "tipo": "liquido"},
        {"nombre": "Martillo", "precio": 150, "tipo": "pieza"}, {"nombre": "Desarmador", "precio": 45, "tipo": "pieza"},
        {"nombre": "Cinta Aislante", "precio": 20, "tipo": "pieza"}, {"nombre": "Brocha", "precio": 35, "tipo": "pieza"},
        {"nombre": "Cerradura", "precio": 300, "tipo": "pieza"}, {"nombre": "Foco LED", "precio": 50, "tipo": "pieza"},
        {"nombre": "Tornillos (paquete)", "precio": 25, "tipo": "pieza"}, {"nombre": "Llave Inglesa", "precio": 180, "tipo": "pieza"},
        {"nombre": "Pijas", "precio": 10, "tipo": "pieza"}, {"nombre": "Tijeras", "precio": 60, "tipo": "pieza"}
    ]

    liquidos = sorted([p for p in catalogo_raw if p['tipo'] == 'liquido'], key=lambda x: x['nombre'])
    piezas = sorted([p for p in catalogo_raw if p['tipo'] == 'pieza'], key=lambda x: x['nombre'])
    catalogo = liquidos + piezas
    
    carrito = []
    p_productos = ft.Column(visible=True)
    p_cobro = ft.Column(visible=False)
    p_resumen = ft.Column(visible=False)

    lista_desglose = ft.ListView(height=150, expand=True)
    total_text = ft.Text("Total a pagar: $0.00", size=20, weight="bold")
    cambio_text = ft.Text("Cambio a entregar: $0.00", size=22, weight="bold", color="blue")
    campo_pago = ft.TextField(label="Pago del cliente ($)", keyboard_type="number")
    campo_otros = ft.TextField(label="Precio Libre ($)", keyboard_type="number")
    campo_cantidad = ft.TextField(label="Cantidad (Piezas)", value="", keyboard_type="number")

    def agregar_item(nombre, precio, medida):
        detalle = f"{nombre} ({medida}) - ${precio}"
        carrito.append({"detalle": detalle, "precio": precio})
        actualizar_lista_visual()
        calcular_total_y_cambio()

    def procesar_precio_libre(e, btn, nombre_prod):
        valor = float(campo_otros.value or 0)
        if valor > 0:
            btn.disabled = True
            page.update()
            agregar_item(nombre_prod, valor, "Otros")
            campo_otros.value = ""
            btn.disabled = False
            page.update()

    def procesar_piezas(e, btn, nombre_prod, precio_unitario):
        try:
            cantidad = int(campo_cantidad.value or 0)
            if cantidad > 0:
                btn.disabled = True
                page.update()
                agregar_item(nombre_prod, precio_unitario * cantidad, f"{cantidad} pz")
                campo_cantidad.value = ""
                btn.disabled = False
                page.update()
        except: pass

    def calcular_total_y_cambio():
        total = sum(i["precio"] for i in carrito)
        total_text.value = f"Total a pagar: ${total}"
        try:
            pago = float(campo_pago.value or 0)
            cambio = pago - total
            cambio_text.value = f"Cambio: ${max(0, cambio):.2f}" if cambio >= 0 else f"Faltan: ${abs(cambio):.2f}"
            cambio_text.color = "green" if cambio >= 0 else "red"
        except: cambio_text.value = "Error"
        page.update()

    def eliminar_item(item_a_eliminar):
        carrito.remove(item_a_eliminar)
        actualizar_lista_visual()
        calcular_total_y_cambio()

    def actualizar_lista_visual():
        lista_desglose.controls.clear()
        for item in carrito:
            lista_desglose.controls.append(ft.Row([
                ft.Text(item["detalle"]),
                ft.ElevatedButton("X", bgcolor="red", color="white", on_click=lambda e, i=item: eliminar_item(i))
            ]))
        page.update()

    campo_pago.on_change = lambda e: calcular_total_y_cambio()

    def cambiar_pantalla(destino):
        p_productos.visible = (destino == "productos")
        p_cobro.visible = (destino == "cobro")
        p_resumen.visible = (destino == "resumen")
        if destino == "resumen": actualizar_resumen()
        page.update()

    def actualizar_resumen():
        p_resumen.controls.clear()
        p_resumen.controls.append(ft.Text("Historial de Ventas:", size=20, weight="bold"))
        acumulado = 0
        conteo_ventas = 0
        if os.path.exists(ARCHIVO_VENTAS):
            with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as f:
                lineas = f.readlines()
                for linea in lineas:
                    p_resumen.controls.append(ft.Text(linea.strip()))
                    if "--- VENTA #" in linea: conteo_ventas += 1
                    try:
                        if "$" in linea:
                            precio_str = linea.split('$')[-1].strip()
                            acumulado += float(precio_str)
                    except: pass
            
            p_resumen.controls.append(ft.Divider())
            p_resumen.controls.append(ft.Text(f"TOTAL VENTAS (Transacciones): {conteo_ventas}", size=18))
            p_resumen.controls.append(ft.Text(f"DINERO TOTAL: ${acumulado:.2f}", size=22, weight="bold", color="green"))
            p_resumen.controls.append(ft.ElevatedButton("CORTE DE CAJA", bgcolor="red", color="white", on_click=hacer_corte))
        page.update()

    def hacer_corte(e):
        if os.path.exists(ARCHIVO_VENTAS): os.remove(ARCHIVO_VENTAS)
        actualizar_resumen()

    def finalizar_venta(e):
        total = sum(i["precio"] for i in carrito)
        pago = float(campo_pago.value or 0)
        if pago >= total and len(carrito) > 0:
            ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            num_venta = datetime.now().strftime("%H%M%S")
            with open(ARCHIVO_VENTAS, "a", encoding="utf-8") as f:
                f.write(f"\n--- VENTA #{num_venta} ({ts}) ---\n")
                for item in carrito: f.write(f"{item['detalle']}\n")
            carrito.clear(); lista_desglose.controls.clear(); total_text.value = "Total: $0.00"; campo_pago.value = ""; campo_otros.value = ""; campo_cantidad.value = ""; page.update()

    nav_bar = ft.Row([ft.ElevatedButton("PROD", on_click=lambda e: cambiar_pantalla("productos")), 
                      ft.ElevatedButton("COBRO", on_click=lambda e: cambiar_pantalla("cobro")), 
                      ft.ElevatedButton("RESUMEN", on_click=lambda e: cambiar_pantalla("resumen"))])

    for i, p in enumerate(catalogo):
        if i > 0 and p['tipo'] == 'pieza' and catalogo[i-1]['tipo'] == 'liquido':
            p_productos.controls.append(ft.Divider(color="blue", height=20))
            p_productos.controls.append(ft.Text("--- PRODUCTOS POR PIEZA ---", weight="bold", color="blue"))
        
        def accion(e, prod=p):
            p_cobro.controls.clear()
            p_cobro.controls.append(ft.Text(f"Venta: {prod['nombre']}", size=20, weight="bold"))
            
            if prod['tipo'] == "liquido":
                btn_ag = ft.ElevatedButton("AGREGAR", bgcolor="orange", color="white")
                btn_ag.on_click = lambda e: procesar_precio_libre(e, btn_ag, prod['nombre'])
                p_cobro.controls.extend([
                    ft.ElevatedButton(f"Litro (${prod['precio']})", on_click=lambda e: agregar_item(prod['nombre'], prod['precio'], "L")),
                    ft.ElevatedButton(f"Medio (${int(prod['precio']/2)})", on_click=lambda e: agregar_item(prod['nombre'], prod['precio']/2, "M")),
                    ft.ElevatedButton(f"Cuarto (${int(prod['precio']/4)})", on_click=lambda e: agregar_item(prod['nombre'], prod['precio']/4, "C")),
                    ft.Divider(), campo_otros, btn_ag
                ])
            else:
                btn_pz = ft.ElevatedButton("AGREGAR PIEZA(S)", bgcolor="orange", color="white")
                btn_pz.on_click = lambda e: procesar_piezas(e, btn_pz, prod['nombre'], prod['precio'])
                p_cobro.controls.extend([campo_cantidad, btn_pz])
            
            p_cobro.controls.extend([ft.Divider(), ft.Text("Bitácora:"), lista_desglose, total_text, campo_pago, cambio_text, ft.ElevatedButton("FINALIZAR", bgcolor="green", color="white", on_click=finalizar_venta)])
            cambiar_pantalla("cobro")
        
        p_productos.controls.append(ft.ElevatedButton(f"{p['nombre']} - ${p['precio']}", on_click=accion))

    page.add(header, nav_bar, ft.Divider(), p_productos, p_cobro, p_resumen)

ft.app(target=main)