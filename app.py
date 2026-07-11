import flet as ft
import os
from datetime import datetime

def main(page: ft.Page):
    page.title = "Sistema Universal - Venta Mixta"
    page.bgcolor = "#F0F4F8"
    page.scroll = None 

    ARCHIVO_VENTAS = "ventas_diarias.txt"

    header = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "NOMBRE DE TU TIENDA", 
                    size=24, 
                    weight="bold", 
                    color="white", 
                    text_align=ft.TextAlign.CENTER,
                    overflow=ft.TextOverflow.VISIBLE
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#1976D2",
        padding=15,
        border_radius=10,
    )

    # Ajuste: Se fuerza a que el Row ocupe el ancho total (expand=True)
    btn_nav_prod = ft.ElevatedButton("PRODUCTOS", bgcolor="yellow", color="black", style=ft.ButtonStyle(padding=5))
    btn_nav_cobro = ft.ElevatedButton("COBRO", bgcolor="green", color="white", style=ft.ButtonStyle(padding=5))
    btn_nav_resumen = ft.ElevatedButton("RESUMEN", bgcolor="green", color="white", style=ft.ButtonStyle(padding=5))

    nav_bar = ft.Row(
        [btn_nav_prod, btn_nav_cobro, btn_nav_resumen], 
        alignment=ft.MainAxisAlignment.CENTER, # Centrado absoluto
        spacing=10 # Espaciado fijo para evitar amontonamiento
    )

    catalogo_raw = [
        {"nombre": "Aceite de Oliva", "precio": 250, "tipo": "liquido"}, {"nombre": "Jabón Líquido", "precio": 80, "tipo": "liquido"},
        {"nombre": "Shampoo", "precio": 120, "tipo": "liquido"}, {"nombre": "Suavizante", "precio": 60, "tipo": "liquido"},
        {"nombre": "Cloro", "precio": 30, "tipo": "liquido"}, {"nombre": "Detergente Ropa", "precio": 90, "tipo": "liquido"},
        {"nombre": "Desinfectante", "precio": 70, "tipo": "liquido"}, {"nombre": "Limpia Vidrios", "precio": 55, "tipo": "liquido"},
        {"nombre": "Alcohol", "precio": 100, "tipo": "liquido"}, {"nombre": "Gel Antibacterial", "precio": 150, "tipo": "liquido"},
        {"nombre": "Aromatizante", "precio": 110, "tipo": "liquido"}, {"nombre": "Jabón de Manos", "precio": 65, "tipo": "liquido"},
        {"nombre": "Desengrasante", "precio": 95, "tipo": "liquido"}, {"nombre": "Vinagre Limpieza", "precio": 40, "tipo": "liquido"},
        {"nombre": "Jabón Trastes", "precio": 50, "tipo": "liquido"}, {"nombre": "Martillo", "precio": 150, "tipo": "pieza"},
        {"nombre": "Desarmador", "precio": 45, "tipo": "pieza"}, {"nombre": "Cinta Aislante", "precio": 20, "tipo": "pieza"},
        {"nombre": "Brocha", "precio": 35, "tipo": "pieza"}, {"nombre": "Cerradura", "precio": 300, "tipo": "pieza"},
        {"nombre": "Foco LED", "precio": 50, "tipo": "pieza"}, {"nombre": "Tornillos (paquete)", "precio": 25, "tipo": "pieza"},
        {"nombre": "Llave Inglesa", "precio": 180, "tipo": "pieza"}, {"nombre": "Pijas", "precio": 10, "tipo": "pieza"},
        {"nombre": "Tijeras", "precio": 60, "tipo": "pieza"}
    ]

    catalogo = sorted([p for p in catalogo_raw if p['tipo'] == 'liquido'], key=lambda x: x['nombre']) + \
               sorted([p for p in catalogo_raw if p['tipo'] == 'pieza'], key=lambda x: x['nombre'])
    
    carrito = []
    
    p_productos = ft.Container(content=ft.Column(scroll=ft.ScrollMode.AUTO), bgcolor="#E3F2FD", padding=10, border_radius=10, visible=True, expand=True)
    p_cobro = ft.Container(content=ft.Column(scroll=ft.ScrollMode.AUTO), bgcolor="#FFF3E0", padding=10, border_radius=10, visible=False, expand=True)
    p_resumen = ft.Container(content=ft.Column(scroll=ft.ScrollMode.AUTO), bgcolor="#E8F5E9", padding=10, border_radius=10, visible=False, expand=True)

    lista_desglose = ft.Column()
    total_text = ft.Text("Total a pagar: $0.00", size=20, weight="bold")
    cambio_text = ft.Text("Cambio a entregar: $0.00", size=22, weight="bold", color="blue")
    
    campo_pago = ft.TextField(label="Pago del cliente ($)", keyboard_type="number", border_color="#CCFF00", border_width=3)
    campo_otros = ft.TextField(label="Precio Libre ($)", keyboard_type="number", border_color="#CCFF00", border_width=3)
    campo_cantidad = ft.TextField(label="Cantidad (Piezas)", value="", keyboard_type="number")

    def cambiar_pantalla(destino):
        p_productos.visible = (destino == "productos")
        p_cobro.visible = (destino == "cobro")
        p_resumen.visible = (destino == "resumen")
        
        btn_nav_prod.bgcolor = "yellow" if destino == "productos" else "green"
        btn_nav_prod.color = "black" if destino == "productos" else "white"
        btn_nav_cobro.bgcolor = "yellow" if destino == "cobro" else "green"
        btn_nav_cobro.color = "black" if destino == "cobro" else "white"
        btn_nav_resumen.bgcolor = "yellow" if destino == "resumen" else "green"
        btn_nav_resumen.color = "black" if destino == "resumen" else "white"
        
        if destino == "resumen": actualizar_resumen()
        page.update()

    def agregar_item(nombre, precio, medida):
        if precio <= 0:
            page.snack_bar = ft.SnackBar(ft.Text("Error: El precio o cantidad debe ser mayor a 0"))
            page.snack_bar.open = True
            page.update()
            return
        carrito.append({"detalle": f"{nombre} ({medida}) - ${precio:.2f}", "precio": precio})
        campo_otros.value = ""; campo_cantidad.value = ""
        actualizar_lista_visual(); calcular_total_y_cambio()

    def calcular_total_y_cambio():
        total = sum(i["precio"] for i in carrito)
        total_text.value = f"Total a pagar: ${total:.2f}"
        try:
            pago = float(campo_pago.value or 0)
            cambio = pago - total
            cambio_text.value = f"Cambio: ${max(0, cambio):.2f}" if cambio >= 0 else f"Faltan: ${abs(cambio):.2f}"
            cambio_text.color = "green" if cambio >= 0 else "red"
        except: cambio_text.value = "Error"
        page.update()

    def eliminar_item(item_a_eliminar):
        carrito.remove(item_a_eliminar); actualizar_lista_visual(); calcular_total_y_cambio()

    def actualizar_lista_visual():
        lista_desglose.controls.clear()
        for item in carrito:
            lista_desglose.controls.append(ft.Row([ft.Text(item["detalle"]), ft.ElevatedButton("X", bgcolor="red", color="white", on_click=lambda e, i=item: eliminar_item(i))]))
        page.update()

    def finalizar_venta(e):
        total = sum(i["precio"] for i in carrito)
        pago = float(campo_pago.value or 0)
        if pago >= total and len(carrito) > 0:
            ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            num_venta = datetime.now().strftime("%H%M%S")
            with open(ARCHIVO_VENTAS, "a", encoding="utf-8") as f:
                f.write(f"\n--- VENTA #{num_venta} | {ts} | TOTAL: ${total:.2f} ---\n")
                for item in carrito: f.write(f"{item['detalle']}\n")
            carrito.clear(); lista_desglose.controls.clear(); total_text.value = "Total a pagar: $0.00"
            campo_pago.value = ""; campo_otros.value = ""; campo_cantidad.value = ""
            cambio_text.value = "Cambio a entregar: $0.00"; cambio_text.color = "blue"; page.update()

    def hacer_corte(e):
        if os.path.exists(ARCHIVO_VENTAS): os.remove(ARCHIVO_VENTAS)
        actualizar_resumen()

    def actualizar_resumen():
        p_resumen.content.controls.clear()
        p_resumen.content.controls.append(ft.Text("Historial de Ventas:", size=20, weight="bold"))
        acumulado = 0; conteo_ventas = 0
        if os.path.exists(ARCHIVO_VENTAS):
            with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as f:
                for linea in f:
                    p_resumen.content.controls.append(ft.Text(linea.strip()))
                    if "--- VENTA #" in linea:
                        conteo_ventas += 1
                        try: acumulado += float(linea.split('TOTAL: $')[-1].split(' ---')[0])
                        except: pass
        p_resumen.content.controls.extend([ft.Divider(), ft.Text(f"TOTAL VENTAS: {conteo_ventas}", size=18), ft.Text(f"DINERO TOTAL: ${acumulado:.2f}", size=22, weight="bold", color="green"), ft.ElevatedButton("CORTE DE CAJA", bgcolor="red", color="white", on_click=hacer_corte)])
        page.update()

    btn_nav_prod.on_click = lambda e: cambiar_pantalla("productos")
    btn_nav_cobro.on_click = lambda e: cambiar_pantalla("cobro")
    btn_nav_resumen.on_click = lambda e: cambiar_pantalla("resumen")

    for i, p in enumerate(catalogo):
        if i > 0 and p['tipo'] == 'pieza' and catalogo[i-1]['tipo'] == 'liquido':
            p_productos.content.controls.extend([ft.Divider(), ft.Text("--- PRODUCTOS POR PIEZA ---", weight="bold", color="blue")])
        
        def accion(e, prod=p):
            p_cobro.content.controls.clear()
            p_cobro.content.controls.append(ft.Text(f"Venta: {prod['nombre']}", size=20, weight="bold"))
            if prod['tipo'] == "liquido":
                p_cobro.content.controls.extend([
                    ft.ElevatedButton(f"Litro (${prod['precio']})", on_click=lambda e: agregar_item(prod['nombre'], prod['precio'], "L")),
                    ft.ElevatedButton(f"Medio (${int(prod['precio']/2)})", on_click=lambda e: agregar_item(prod['nombre'], prod['precio']/2, "M")),
                    ft.ElevatedButton(f"Cuarto (${int(prod['precio']/4)})", on_click=lambda e: agregar_item(prod['nombre'], prod['precio']/4, "C")),
                    ft.Divider(), campo_otros, ft.ElevatedButton("AGREGAR LIBRE", bgcolor="orange", on_click=lambda e: agregar_item(prod['nombre'], float(campo_otros.value or 0), "Libre"))
                ])
            else:
                p_cobro.content.controls.extend([campo_cantidad, ft.ElevatedButton("AGREGAR PIEZA(S)", bgcolor="orange", on_click=lambda e: agregar_item(prod['nombre'], prod['precio'] * int(campo_cantidad.value or 0), "Pz"))])
            p_cobro.content.controls.extend([ft.Divider(), ft.Text("Lista de productos:"), lista_desglose, total_text, campo_pago, cambio_text, ft.ElevatedButton("FINALIZAR", bgcolor="green", color="white", on_click=finalizar_venta)])
            cambiar_pantalla("cobro")
        
        p_productos.content.controls.append(ft.ElevatedButton(f"{p['nombre']} - ${p['precio']}", on_click=accion, bgcolor="orange", color="black"))

    campo_pago.on_change = lambda e: calcular_total_y_cambio()
    
    # Estructura final con centrado en el nav_bar
    page.add(ft.Column([header, nav_bar, ft.Divider(), ft.Stack([p_productos, p_cobro, p_resumen], expand=True)], expand=True))
    cambiar_pantalla("productos")

ft.app(target=main)
