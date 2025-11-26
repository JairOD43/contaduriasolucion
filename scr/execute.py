import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
from datetime import datetime, date
from usuario import Usuario
from cliente import Cliente
from transaccion import Transaccion
from auditoria import Auditoria
from auditoria_ia import detectar_errores

current_user = None
cliente_seleccionado = None

root = tk.Tk()
root.title("Contabilidad Executive • Despacho Premium")
root.geometry("1400x900")
root.configure(bg="#0a0e17")
root.state('zoomed')

title_font = tkfont.Font(family="Segoe UI Semibold", size=24, weight="bold")
header_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
menu_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
text_font = tkfont.Font(family="Consolas", size=11)

bg_main = "#0a0e17"
bg_sidebar = "#111822"
bg_card = "#141a28"
accent = "#00d4ff"
text_color = "#e0e6ff"
success = "#00ff9d"
danger = "#ff6b9d"

def login_window():
    global current_user
    login = tk.Toplevel(root)
    login.title("Acceso al Sistema")
    login.geometry("460x640")
    login.configure(bg="#0f1422")
    login.resizable(False, False)
    login.grab_set()
    login.focus_force()
    login.transient(root)
    login.geometry("+%d+%d" % (root.winfo_screenwidth()//2 - 230, root.winfo_screenheight()//2 - 320))

    tk.Label(login, text="Contabilidad", font=("Segoe UI", 32, "bold"), fg=accent, bg="#0f1422").pack(pady=40)
    tk.Label(login, text="Executive Suite", font=("Segoe UI", 14), fg="#00a1d6", bg="#0f1422").pack(pady=5)

    frame = tk.Frame(login, bg="#141a28")
    frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Acceso seguro al sistema contable", fg="#88aaff", bg="#141a28", font=("Segoe UI", 10)).pack(pady=(20,30))

    entry_user = ttk.Entry(frame, font=("Segoe UI", 12), width=35)
    entry_user.pack(pady=12)
    entry_user.insert(0, "Nombre completo")
    entry_user.bind("<FocusIn>", lambda e: entry_user.delete(0, tk.END) if entry_user.get() == "Nombre completo" else None)

    entry_pwd = ttk.Entry(frame, font=("Segoe UI", 12), width=35, show='•')
    entry_pwd.pack(pady=12)

    combo_rol = ttk.Combobox(frame, values=["cliente", "contador_principal"], state="readonly")
    combo_rol.set("cliente")
    combo_rol.pack(pady=18)

    def iniciar():
        user = entry_user.get().strip()
        pwd = entry_pwd.get()
        if not user:
            return messagebox.showerror("Error", "Ingresa tu nombre")
        u = Usuario.autenticar(user, pwd if pwd else None)
        if u:
            global current_user
            current_user = u
            login.destroy()
            actualizar_interfaz()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def registrar():
        nombre = entry_user.get().strip()
        rol = combo_rol.get()
        pwd = entry_pwd.get()
        if not nombre:
            return messagebox.showerror("Error", "Nombre requerido")
        if Usuario.buscar_por_nombre(nombre):
            return messagebox.showerror("Error", "El nombre de usuario ya existe")
        if rol == "admin":
            if simpledialog.askstring("Código Admin", "Código secreto:", show='*') != "XAI2025ADMIN":
                return messagebox.showerror("Denegado", "Código incorrecto")
        Usuario.crear(nombre, rol, pwd if pwd else None)
        global current_user
        current_user = Usuario.autenticar(nombre, pwd if pwd else None)
        login.destroy()
        actualizar_interfaz()
        messagebox.showinfo("Éxito", f"Bienvenido, {nombre}")

    ttk.Button(frame, text="Iniciar Sesión", command=iniciar).pack(pady=12, fill=tk.X)
    ttk.Button(frame, text="Crear Cuenta Nueva", command=registrar).pack(pady=8, fill=tk.X)

def actualizar_interfaz():
    lbl_user.config(text=f"Usuario: {current_user.nombre} ({current_user.role})")
    actualizar_permisos_menu()

def actualizar_permisos_menu():
    for texto, (btn, roles) in botones_widgets.items():
        if current_user and current_user.role in roles:
            btn.config(state=tk.NORMAL)
        else:
            btn.config(state=tk.DISABLED)

def seleccionar_cliente():
    if not current_user:
        return
    clientes = Cliente.listar_todos()
    if not clientes:
        messagebox.showinfo("Info", "No hay clientes registrados.")
        return
    nombres = [c.nombre for c in clientes]
    seleccion = simpledialog.askstring("Seleccionar Cliente", "Nombre del cliente:", initialvalue=nombres[0] if nombres else "")
    if seleccion:
        global cliente_seleccionado
        cliente_seleccionado = Cliente.buscar_por_nombre(seleccion)
        if cliente_seleccionado:
            lbl_cliente.config(text=f"Cliente: {cliente_seleccionado.nombre} | RFC: {cliente_seleccionado.rfc}")
            output.delete(1.0, tk.END)
            output.insert(tk.END, f"Cliente seleccionado: {cliente_seleccionado.nombre}\n\n", "success")
            cargar_transacciones()
        else:
            messagebox.showerror("Error", "Cliente no encontrado")

def formulario_nuevo_cliente():
    if current_user.role not in ["admin", "contador_principal"]:
        messagebox.showerror("Acceso Denegado", "Solo admins y contadores principales pueden crear clientes")
        return
    nombre = simpledialog.askstring("Nuevo Cliente", "Nombre del cliente:")
    if nombre:
        rfc = simpledialog.askstring("Nuevo Cliente", "RFC:")
        regimen = simpledialog.askstring("Nuevo Cliente", "Régimen fiscal (default: Régimen General):", initialvalue="Régimen General")
        try:
            Cliente.crear(nombre, rfc, regimen)
            messagebox.showinfo("Éxito", f"Cliente {nombre} creado.")
            output.insert(tk.END, f"Nuevo cliente: {nombre} (RFC: {rfc})\n", "success")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear: {e}")

def actualizar_cliente():
    if not cliente_seleccionado:
        messagebox.showerror("Error", "Selecciona un cliente primero")
        return
    nuevo_nombre = simpledialog.askstring("Actualizar Cliente", f"Nuevo nombre para {cliente_seleccionado.nombre} :", initialvalue=cliente_seleccionado.nombre)
    nuevo_rfc = simpledialog.askstring("Actualizar Cliente", f"Nuevo RFC para {cliente_seleccionado.nombre} :", initialvalue=cliente_seleccionado.rfc)
    nuevo_regimen = simpledialog.askstring("Actualizar Cliente", f"Nuevo régimen fiscal para {cliente_seleccionado.nombre} :", initialvalue=cliente_seleccionado.regimen_fiscal)
    try:
        cliente_seleccionado.actualizar(nuevo_nombre if nuevo_nombre.strip() else None, nuevo_rfc if nuevo_rfc.strip() else None, nuevo_regimen if nuevo_regimen.strip() else None)
        lbl_cliente.config(text=f"Cliente: {cliente_seleccionado.nombre} | RFC: {cliente_seleccionado.rfc}")
        output.insert(tk.END, f"Cliente actualizado: {cliente_seleccionado.nombre} | RFC: {cliente_seleccionado.rfc}\n", "success")
        messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al actualizar: {e}")
        output.insert(tk.END, f"Error al actualizar cliente: {e}\n", "danger")

def eliminar_cliente():
    global cliente_seleccionado
    if not cliente_seleccionado:
        messagebox.showerror("Error", "Selecciona un cliente primero")
        return
    if messagebox.askyesno("Confirmar", f"Eliminar {cliente_seleccionado.nombre}? Esta acción eliminará también las transacciones relacionadas."):
        try:
            nombre_eliminado = cliente_seleccionado.nombre
            cliente_seleccionado.eliminar()
            cliente_seleccionado = None
            lbl_cliente.config(text="Ningún cliente seleccionado")
            output.insert(tk.END, f"Cliente eliminado: {nombre_eliminado}\n", "danger")
            output.insert(tk.END, "Transacciones asociadas eliminadas por cascada.\n", "warning")
            messagebox.showinfo("Éxito", f"Cliente {nombre_eliminado} eliminado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")
            output.insert(tk.END, f"Error al eliminar cliente: {e}\n", "danger")

def registrar_transaccion():
    if not cliente_seleccionado:
        messagebox.showerror("Error", "Selecciona un cliente primero")
        return
    concepto = simpledialog.askstring("Nueva Transacción", "Concepto:")
    if concepto:
        monto_str = simpledialog.askstring("Nueva Transacción", "Monto:")
        tipo = simpledialog.askstring("Nueva Transacción", "Tipo (ingreso/gasto):")
        fecha = simpledialog.askstring("Nueva Transacción", "Fecha (YYYY-MM-DD):", initialvalue=datetime.now().strftime("%Y-%m-%d"))
        try:
            monto = float(monto_str)
            Transaccion.crear(cliente_seleccionado.id, fecha, concepto, monto, tipo)
            output.insert(tk.END, f"Transacción registrada: {concepto} - ${monto}\n", "success")
            cargar_transacciones()
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")

def eliminar_transaccion():
    global cliente_seleccionado
    if not cliente_seleccionado:
        messagebox.showerror("Error", "Selecciona un cliente primero")
        return
    transaccion_id_str = simpledialog.askstring("Eliminar Transacción", "Ingresa el ID de la transacción a eliminar:")
    if transaccion_id_str:
        try:
            transaccion_id = int(transaccion_id_str)
            transaccion = Transaccion.buscar_por_id(transaccion_id)
            if not transaccion:
                messagebox.showerror("Error", "Transacción no encontrada")
                return
            if transaccion.cliente_id != cliente_seleccionado.id:
                messagebox.showerror("Error", "Esta transacción no pertenece al cliente seleccionado")
                return
            if messagebox.askyesno("Confirmar", f"Eliminar transacción ID {transaccion.id}: {transaccion.concepto}? Esta acción eliminará también las auditorías relacionadas."):
                transaccion.eliminar()
                output.insert(tk.END, f"Transacción eliminada: ID {transaccion.id} - {transaccion.concepto}\n", "danger")
                output.insert(tk.END, "Auditorías asociadas eliminadas por cascada.\n", "warning")
                cargar_transacciones()
                messagebox.showinfo("Éxito", f"Transacción {transaccion.id} eliminada correctamente.")
        except ValueError:
            messagebox.showerror("Error", "ID de transacción inválido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")
            output.insert(tk.END, f"Error al eliminar transacción: {e}\n", "danger")

def detectar_errores_ia():
    global cliente_seleccionado
    if not cliente_seleccionado:
        messagebox.showerror("Error", "Selecciona un cliente primero")
        return
    transacciones = Transaccion.listar_por_cliente(cliente_seleccionado.id)
    if not transacciones:
        output.insert(tk.END, "No hay transacciones para auditar.\n", "warning")
        return
    trans_list = []
    for t in transacciones:
        obj = type('TransObj', (object,), {'tipo': t.tipo, 'monto': t.monto, 'concepto': t.concepto})()
        trans_list.append(obj)
    errores = detectar_errores(trans_list)
    output.insert(tk.END, f"AUDITORÍA IA EJECUTADA EL {date.today()} PARA {cliente_seleccionado.nombre}\n", "title")
    if errores and errores[0] != "Ningún error crítico detectado por IA.":
        num_errores = len(errores)
        output.insert(tk.END, f"Se detectaron {num_errores} error potencial:\n\n", "critical")
        for i, error in enumerate(errores, 1):
            tag = "critical" if "ALTA" in error or "IA -" in error else "warning"
            output.insert(tk.END, f"{i}. {error}\n", tag)
            
            if current_user:
                Auditoria.crear(transacciones[0].id, current_user.id, date.today(), error, 'pendiente')
        output.insert(tk.END, f"\n{num_errores} auditoría creada en la base de datos.\n", "success")
    else:
        output.insert(tk.END, "Ningún error crítico detectado. Auditoría registrada como 'limpia'.\n", "success")
        if current_user:
            Auditoria.crear(transacciones[0].id, current_user.id, date.today(), "Auditoría IA: Sin anomalías detectadas", 'aprobada')
    output.insert(tk.END, f"\nAuditoría completada. Revisa 'Ver Auditorías' para detalles.\n", "line")
    messagebox.showinfo("Auditoría IA Completada", f"Procesadas {len(transacciones)} transacciones. {len(errores) if errores else 0} alertas generadas.")

def ver_auditorias():
    if not cliente_seleccionado:
        messagebox.showerror("Error", "Selecciona un cliente primero")
        return
    transacciones = Transaccion.listar_por_cliente(cliente_seleccionado.id)
    output.insert(tk.END, f"AUDITORÍAS PARA {cliente_seleccionado.nombre}\n", "title")
    total_auds = 0
    for t in transacciones:
        auds = Auditoria.listar_por_transaccion(t.id)
        if auds:
            output.insert(tk.END, f"\n--- Transacción ID {t.id}: {t.concepto} (${t.monto} - {t.tipo}) ---\n", "line")
            for a in auds:
                tag = "success" if a.resultado == "aprobada" else "warning" if a.resultado == "pendiente" else "danger"
                output.insert(tk.END, f"  {a.descripcion} | Resultado: {a.resultado} | Fecha: {a.fecha_auditoria}\n", tag)
                total_auds += 1
    if total_auds == 0:
        output.insert(tk.END, "No hay auditorías registradas para este cliente.\n", "warning")
    else:
        output.insert(tk.END, f"\nTotal de auditorías: {total_auds}\n", "line")

def eliminar_auditoria():
    output.insert(tk.END, "Eliminar auditoría \n", "warning")

def ver_todos_clientes():
    clientes = Cliente.listar_todos()
    if not clientes:
        messagebox.showinfo("Info", "No hay clientes registrados.")
        return
    ventana = tk.Toplevel(root)
    ventana.title("Todos los Clientes")
    ventana.geometry("600x500")
    ventana.configure(bg="#0f1422")
    ventana.resizable(True, True)
    ventana.transient(root)

    frame = tk.Frame(ventana, bg="#141a28")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    tk.Label(frame, text="Lista de Clientes", font=("Segoe UI", 16, "bold"), fg=accent, bg="#141a28").pack(pady=(0,10))

    columns = ("ID", "Nombre", "RFC", "Régimen Fiscal")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor=tk.W)

    for c in clientes:
        tree.insert("", tk.END, values=(c.id, c.nombre, c.rfc, c.regimen_fiscal))

    tree.pack(fill=tk.BOTH, expand=True, pady=(0,10))

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack(pady=10)

def ver_todos_usuarios():
    if current_user.role not in ["admin", "contador_principal"]:
        messagebox.showerror("Acceso Denegado", "Solo admins y contadores principales pueden ver usuarios")
        return
    usuarios = Usuario.listar_todos()
    if not usuarios:
        output.insert(tk.END, "No hay usuarios registrados.\n", "warning")
        return
    output.insert(tk.END, "LISTA DE USUARIOS\n", "title")
    output.insert(tk.END, "=" * 50 + "\n\n", "line")
    for u in usuarios:
        output.insert(tk.END, f"ID: {u.id} | {u.nombre} ({u.role})\n\n", "line")
    output.see(tk.END)

def cargar_transacciones():
    if not cliente_seleccionado:
        return
    transacciones = Transaccion.listar_por_cliente(cliente_seleccionado.id)
    output.insert(tk.END, f"TRANSSACCIONES DE {cliente_seleccionado.nombre}\n", "title")
    saldo = 0
    for t in transacciones:
        tag = "saldo" if t.tipo == "ingreso" else "negative"
        output.insert(tk.END, f"{t.fecha} | {t.concepto} | ${t.monto:.2f} ({t.tipo}) | ID: {t.id}\n", tag)
        if t.tipo == "ingreso":
            saldo += t.monto
        else:
            saldo -= t.monto
    output.insert(tk.END, f"\nSaldo total: ${saldo:.2f}\n", "saldo" if saldo >= 0 else "negative")

def cerrar_sesion():
    global current_user, cliente_seleccionado
    if messagebox.askyesno("Cerrar sesión", "¿Cerrar sesión actual?"):
        current_user = None
        cliente_seleccionado = None
        lbl_user.config(text="Usuario: No autenticado")
        lbl_cliente.config(text="Ningún cliente seleccionado")
        output.delete(1.0, tk.END)
        output.insert(tk.END, "Sesión cerrada.\n\nInicia sesión para continuar.", "title")
        actualizar_permisos_menu()
        root.after(1000, login_window)

sidebar = tk.Frame(root, bg=bg_sidebar, width=300)
sidebar.pack(side=tk.LEFT, fill=tk.Y)
sidebar.pack_propagate(False)

tk.Label(sidebar, text="Contabilidad", font=("Segoe UI", 22, "bold"), fg=accent, bg=bg_sidebar).pack(pady=(50,8))
tk.Label(sidebar, text="Executive Suite", font=("Segoe UI", 11), fg="#0088cc", bg=bg_sidebar).pack(pady=(0,40))

botones_config = [
    ("Seleccionar Cliente", seleccionar_cliente, ["cliente", "contador_principal", "admin"]),
    ("Registrar Nuevo Cliente", formulario_nuevo_cliente, ["contador_principal", "admin"]),
    ("Actualizar Cliente", actualizar_cliente, ["contador_principal", "admin"]),
    ("Eliminar Cliente", eliminar_cliente, ["contador_principal", "admin"]),
    ("Nueva Transacción", registrar_transaccion, ["contador_principal", "admin"]),
    ("Ver Todos los Clientes", ver_todos_clientes, ["contador_principal", "admin"]),
    ("Eliminar Transacción", eliminar_transaccion, ["contador_principal", "admin"]),
    ("Auditoría con IA (CU-12)", detectar_errores_ia, ["contador_principal", "admin"]),
    ("Ver Auditorías", ver_auditorias, ["contador_principal", "admin"]),
    ("Eliminar Auditoría", eliminar_auditoria, ["contador_principal", "admin"]),
    ("Ver Todos los Usuarios", ver_todos_usuarios, ["contador_principal", "admin"]),
    ("Cerrar Sesión", cerrar_sesion, ["cliente", "contador_principal", "admin"]),
]

botones_widgets = {}
for texto, cmd, roles in botones_config:
    b = tk.Button(sidebar, text=f"   {texto}", font=menu_font, fg=text_color, bg="#141a28",
                  activebackground="#00ffaa", activeforeground="white", relief=tk.FLAT,
                  anchor="w", padx=30, pady=18, command=cmd, cursor="hand2", state=tk.DISABLED)
    b.pack(fill=tk.X, pady=5, padx=20)
    b.bind("<Enter>", lambda e, btn=b: btn.config(bg="#1e2538") if btn.cget("state") != "disabled" else None)
    b.bind("<Leave>", lambda e, btn=b: btn.config(bg="#141a28") if btn.cget("state") != "disabled" else None)
    botones_widgets[texto] = (b, roles)

main = tk.Frame(root, bg=bg_main)
main.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

header = tk.Frame(main, bg=bg_card, height=90)
header.pack(fill=tk.X, pady=(0,20))
header.pack_propagate(False)
tk.Label(header, text="Contabilidad Executive", font=title_font, fg=accent, bg=bg_card).pack(side=tk.LEFT, padx=30, pady=20)
lbl_user = tk.Label(header, text="Usuario: No autenticado", font=header_font, fg="#88aaff", bg=bg_card)
lbl_user.pack(side=tk.RIGHT, padx=30, pady=20)

cliente_frame = tk.LabelFrame(main, text=" Cliente Actual ", font=("Segoe UI", 12, "bold"), fg=accent, bg=bg_card, bd=2, relief=tk.FLAT, labelanchor="n")
cliente_frame.pack(fill=tk.X, pady=(0,20), padx=10)
lbl_cliente = tk.Label(cliente_frame, text="Ningún cliente seleccionado", font=("Segoe UI", 14), fg="#88aaff", bg=bg_card, padx=30, pady=20)
lbl_cliente.pack(fill=tk.X, anchor="w")

output_frame = tk.Frame(main, bg=bg_main)
output_frame.pack(fill=tk.BOTH, expand=True)

output = tk.Text(output_frame, font=text_font, bg="#0c1018", fg=text_color, wrap=tk.WORD, relief=tk.FLAT, bd=12, insertbackground=accent, height=30)
scroll = ttk.Scrollbar(output_frame, command=output.yview)
output.configure(yscrollcommand=scroll.set)
output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

output.tag_config("title", font=("Segoe UI", 18, "bold"), foreground=accent, justify="center")
output.tag_config("line", foreground="#333333")
output.tag_config("green", foreground=success, font=("Consolas", 12, "bold"))
output.tag_config("red", foreground=danger, font=("Consolas", 12, "bold"))
output.tag_config("date", foreground="#8899ff")
output.tag_config("success", foreground=success, font=("Segoe UI", 12, "bold"))
output.tag_config("critical", foreground="#ff3366", font=("Segoe UI", 12, "bold"))
output.tag_config("warning", foreground="#ffaa00")
output.tag_config("saldo", foreground=success, font=("Consolas", 13, "bold"))
output.tag_config("negative", foreground=danger, font=("Consolas", 13, "bold"))

actualizar_permisos_menu()
root.after(500, login_window)
root.mainloop()