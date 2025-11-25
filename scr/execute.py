import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
from datetime import datetime
from usuario import Usuario
from cliente import Cliente
from transaccion import Transaccion
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

    combo_rol = ttk.Combobox(frame, values=["cliente", "contador_principal", "admin"], state="readonly")
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
        # Nueva verificación para evitar duplicados
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
    if cliente_seleccionado:
        lbl_cliente.config(text=f"Cliente: {cliente_seleccionado.nombre} | RFC: {cliente_seleccionado.rfc}")

def actualizar_permisos_menu():
    rol = current_user.role if current_user else "none"
    for texto, (boton, roles) in botones_widgets.items():
        if rol in roles:
            boton.config(state="normal", bg="#141a28")
        else:
            boton.config(state="disabled", bg="#0f131a")

def seleccionar_cliente():
    global cliente_seleccionado
    busqueda = simpledialog.askstring("Buscar Cliente", "Nombre o parte del nombre:")
    if busqueda:
        cliente = Cliente.buscar_por_nombre(busqueda)
        if cliente:
            cliente_seleccionado = cliente
            lbl_cliente.config(text=f"Cliente: {cliente.nombre} | RFC: {cliente_seleccionado.rfc}")
            listar_transacciones()
        else:
            messagebox.showinfo("No encontrado", "Cliente no encontrado")

def formulario_nuevo_cliente():
    win = tk.Toplevel(root)
    win.title("Registrar Nuevo Cliente")
    win.geometry("520x480")
    win.configure(bg="#0f1422")

    tk.Label(win, text="Nuevo Cliente", font=("Segoe UI", 18, "bold"), fg=accent, bg="#0f1422").pack(pady=25)

    form = ttk.Frame(win, padding=40)
    form.pack(fill=tk.BOTH, expand=True)

    ttk.Label(form, text="Razón Social:").grid(row=0, column=0, sticky="w", pady=10)
    e_nombre = ttk.Entry(form, width=40)
    e_nombre.grid(row=0, column=1, pady=10)

    ttk.Label(form, text="RFC:").grid(row=1, column=0, sticky="w", pady=10)
    e_rfc = ttk.Entry(form, width=40)
    e_rfc.grid(row=1, column=1, pady=10)

    ttk.Label(form, text="Régimen Fiscal:").grid(row=2, column=0, sticky="w", pady=10)
    e_regimen = ttk.Entry(form, width=40)
    e_regimen.grid(row=2, column=1, pady=10)

    def submit():
        nombre = e_nombre.get().strip()
        rfc = e_rfc.get().strip()
        regimen = e_regimen.get().strip() or "Régimen General"
        if not nombre or not rfc:
            return messagebox.showerror("Error", "Nombre y RFC requeridos")
        try:
            cliente = Cliente.crear(nombre, rfc, regimen)
            messagebox.showinfo("Éxito", f"Cliente registrado: {cliente}")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {str(e)}")

    ttk.Button(form, text="Registrar", command=submit).grid(row=3, column=0, columnspan=2, pady=20)

def registrar_transaccion():
    if not cliente_seleccionado:
        return messagebox.showerror("Error", "Selecciona un cliente primero")
    win = tk.Toplevel(root)
    win.title("Nueva Transacción")
    win.geometry("520x480")
    win.configure(bg="#0f1422")

    tk.Label(win, text="Nueva Transacción", font=("Segoe UI", 18, "bold"), fg=accent, bg="#0f1422").pack(pady=25)

    form = ttk.Frame(win, padding=40)
    form.pack(fill=tk.BOTH, expand=True)

    ttk.Label(form, text="Fecha:").grid(row=0, column=0, sticky="w", pady=10)
    e_fecha = ttk.Entry(form, width=40)
    e_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
    e_fecha.grid(row=0, column=1, pady=10)

    ttk.Label(form, text="Concepto:").grid(row=1, column=0, sticky="w", pady=10)
    e_concepto = ttk.Entry(form, width=40)
    e_concepto.grid(row=1, column=1, pady=10)

    ttk.Label(form, text="Monto:").grid(row=2, column=0, sticky="w", pady=10)
    e_monto = ttk.Entry(form, width=40)
    e_monto.grid(row=2, column=1, pady=10)

    ttk.Label(form, text="Tipo:").grid(row=3, column=0, sticky="w", pady=10)
    combo_tipo = ttk.Combobox(form, values=["ingreso", "gasto"], state="readonly")
    combo_tipo.set("ingreso")
    combo_tipo.grid(row=3, column=1, pady=10)

    def submit():
        try:
            fecha = datetime.strptime(e_fecha.get(), "%Y-%m-%d").date()
            concepto = e_concepto.get().strip()
            monto = float(e_monto.get())
            tipo = combo_tipo.get()
            if not concepto or monto <= 0:
                raise ValueError("Datos inválidos")
            Transaccion.crear(cliente_seleccionado.id, fecha, concepto, monto, tipo)
            messagebox.showinfo("Éxito", "Transacción registrada")
            win.destroy()
            listar_transacciones()
        except ValueError as e:
            messagebox.showerror("Error", f"Error en datos: {e}")

    ttk.Button(form, text="Registrar", command=submit).grid(row=4, column=0, columnspan=2, pady=20)

def detectar_errores_ia():
    if not cliente_seleccionado:
        return messagebox.showerror("Error", "Selecciona un cliente primero")
    transacciones = Transaccion.listar_por_cliente(cliente_seleccionado.id)
    errores = detectar_errores(transacciones)
    output.delete(1.0, tk.END)
    output.insert(tk.END, f"AUDITORÍA IA - {cliente_seleccionado.nombre.upper()}\n", "title")
    output.insert(tk.END, "-" * 80 + "\n\n")
    for err in errores:
        if "ALTA" in err or "IA" in err:
            tag = "critical"
        elif "MEDIA" in err:
            tag = "warning"
        else:
            tag = "success"
        output.insert(tk.END, f"{err}\n", tag)

def ver_todos_clientes():
    output.delete(1.0, tk.END)
    clientes = Cliente.listar_todos()
    output.insert(tk.END, "CLIENTES REGISTRADOS\n", "title")
    output.insert(tk.END, "-" * 80 + "\n\n")
    if not clientes:
        output.insert(tk.END, "No hay clientes registrados.\n")
    else:
        for c in clientes:
            output.insert(tk.END, f"{c.nombre}\n")
            output.insert(tk.END, f"RFC: {c.rfc} | Régimen: {c.regimen_fiscal}\n\n")

def listar_transacciones():
    if not cliente_seleccionado:
        return
    output.delete(1.0, tk.END)
    transacciones = Transaccion.listar_por_cliente(cliente_seleccionado.id)
    total_i = total_g = 0

    output.insert(tk.END, f"TRANSACCIONES - {cliente_seleccionado.nombre.upper()}\n", "title")
    output.insert(tk.END, "-" * 80 + "\n\n")

    for t in transacciones:
        signo = "+" if t.tipo == "ingreso" else "-"
        color = "green" if t.tipo == "ingreso" else "red"
        output.insert(tk.END, f"{t.fecha}  ", "date")
        output.insert(tk.END, f"{signo}${t.monto:,.2f}  ", color)
        output.insert(tk.END, f"{t.concepto}\n")
        if t.tipo == "ingreso":
            total_i += t.monto
        else:
            total_g += t.monto

    output.insert(tk.END, "\n" + "-" * 80 + "\n", "line")
    output.insert(tk.END, f"TOTAL INGRESOS:  ${total_i:,.2f}\n", "green")
    output.insert(tk.END, f"TOTAL GASTOS:    ${total_g:,.2f}\n", "red")
    saldo = total_i - total_g
    output.insert(tk.END, f"SALDO:           ${saldo:,.2f}\n", "saldo" if saldo >= 0 else "negative")

def cerrar_sesion():
    if messagebox.askyesno("Cerrar sesión", "¿Cerrar sesión actual?"):
        global current_user, cliente_seleccionado
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
    ("Nueva Transacción", registrar_transaccion, ["contador_principal", "admin"]),
    ("Auditoría con IA (CU-12)", detectar_errores_ia, ["contador_principal", "admin"]),
    ("Ver Todos los Clientes", ver_todos_clientes, ["contador_principal", "admin"]),
    ("Cerrar Sesión", cerrar_sesion, ["cliente", "contador_principal", "admin"]),
]

botones_widgets = {}
for texto, cmd, roles in botones_config:
    b = tk.Button(sidebar, text=f"   {texto}", font=menu_font, fg=text_color, bg="#141a28",
                  activebackground="#00ffaa", activeforeground="white", relief=tk.FLAT,
                  anchor="w", padx=30, pady=18, command=cmd, cursor="hand2")
    b.pack(fill=tk.X, pady=5, padx=20)
    b.bind("<Enter>", lambda e, btn=b: btn.config(bg="#1e2538"))
    b.bind("<Leave>", lambda e, btn=b: btn.config(bg="#141a28"))
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

output = tk.Text(output_frame, font=text_font, bg="#0c1018", fg=text_color, wrap=tk.WORD, relief=tk.FLAT, bd=12, insertbackground=accent)
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

root.after(500, login_window)
root.mainloop()