import tkinter as tk
from tkinter import ttk, messagebox
import proyectJeep as ia

class QuestionsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto: Análisis Predictivo de Mantenimiento Automotriz")
        self.centrar_ventana(900, 650)
        self.configure(bg="#f0f0f0")
        
        self.inputs = {}
        self.timer = None 
        
        self.main_frame = ttk.Frame(self, padding="30")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.result_frame = tk.Frame(self, bg="#f0f0f0")
        
        self.create_widgets()

        self.creditos_label = tk.Label(self, text="Traductores e Intérpretes, Grupo 6. 03/02/2026", font=("Segoe UI", 9, "italic", "bold"))
        self.creditos_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

    def centrar_ventana(self, ancho, alto):
        x = self.winfo_screenwidth() // 2 - ancho // 2
        y = self.winfo_screenheight() // 2 - alto // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def create_widgets(self):
        tk.Label(self.main_frame, text="INTELIGENCIA ARTIFICIAL PARA \n DETECCIÓN DE FALLAS DEL AUTOMÓVIL",
                 font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))
        
        marco = tk.LabelFrame(self.main_frame, text=" Datos del vehículo ", font=("Comic Sans MS", 15, "bold"), bg="white", padx=20, pady=20)
        marco.pack(fill=tk.BOTH, expand=True)
        marco.columnconfigure((0,1), weight=1)

        preguntas = [
            ("Marca:", "text"), 
            ("Modelo del Auto:", "text"),
            ("Año:", "text"), 
            ("Kilometraje:", "text"),
            ("Uso del vehículo", "combo", ['Ciudad', 'Carretera', 'Mixto']),
            ("Estado del motor:", "combo", ['Normal', 'Fuga Aceite', 'Sobrecalentamiento', 'Ruido Valvulas']),
            ("Estado del Tren Delantero:", "combo", ['Alineado', 'Desgaste', 'Holgura', 'Ruidos']),
            ("Estado de la Caja:", "combo", ['Suave', 'Golpes', 'Deslizamiento'])
        ]

        for i, (label, tipo, *opts) in enumerate(preguntas):
            cell = tk.Frame(marco, bg="white")
            cell.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")
            tk.Label(cell, text=label, bg="white", font=("Arial", 13, "bold"), pady=10).pack(anchor="w")
            
            if tipo == "text":
                if label == "Kilometraje:":
                    w = ttk.Entry(cell, font=("Segoe UI", 11))
                else:
                    w = ttk.Combobox(cell, font=("Segoe UI", 11))
                    if label == "Marca:":
                        w.bind('<KeyRelease>', lambda e: self.agendar_sugerencia(e, "make"))
                    elif label == "Modelo del Auto:":
                        w.bind('<KeyRelease>', lambda e: self.agendar_sugerencia(e, "model"))
                    elif label == "Año:":
                        w.bind('<KeyRelease>', lambda e: self.agendar_sugerencia(e, "year"))
            else:
                w = ttk.Combobox(cell, values=opts[0], state="readonly", font=("Segoe UI", 11))
            
            w.pack(fill=tk.X)
            self.inputs[label] = w

        tk.Button(self.main_frame, text="ANALIZAR VEHÍCULO", command=self.submit_action, 
                   bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", height=2, cursor="hand2", 
                   activebackground="#27ae60").pack(pady=20, fill=tk.X, padx=300)

    def agendar_sugerencia(self, event, tipo):
        if self.timer: self.after_cancel(self.timer)
        self.timer = self.after(500, lambda: self.obtener_sugerencias(event.widget, tipo))

    def obtener_sugerencias(self, widget, tipo):
        val = widget.get().strip()
        if len(val) < 2: return
        marca_actual = self.inputs["Marca:"].get().strip()
        modelo_actual = self.inputs["Modelo del Auto:"].get().strip()
        m_filtro = marca_actual if tipo in ["model", "year"] else None
        mod_filtro = modelo_actual if tipo == "year" else None
        sugerencias = ia.buscar_sugerencias(tipo, val, m_filtro, mod_filtro)
        if sugerencias:
            widget['values'] = sugerencias
            widget.event_generate('<Down>')

    def submit_action(self):
        try:
            # Ahora recibimos 3 valores de la función
            resumen, diag, color = ia.analizar_vehiculo_completo(
                self.inputs["Marca:"].get(), self.inputs["Modelo del Auto:"].get(),
                int(self.inputs["Año:"].get()), int(self.inputs["Kilometraje:"].get()),
                self.inputs["Uso del vehículo"].get(), self.inputs["Estado del motor:"].get(),
                self.inputs["Estado del Tren Delantero:"].get(), self.inputs["Estado de la Caja:"].get()
            )
            self.mostrar_resultados(resumen, color)
        except:
            messagebox.showerror("Error", "Verifica haber llenado todos los campos")

    def mostrar_resultados(self, texto, color_ia):
        self.main_frame.pack_forget()
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        for w in self.result_frame.winfo_children(): w.destroy()
        
        tk.Label(self.result_frame, text="DIAGNÓSTICO DE LA IA", font=("Segoe UI", 24, "bold")).pack(pady=10)
        
        # Se aplica el color_ia al parámetro fg (foreground/color de letra)
        tk.Label(self.result_frame, text=texto, font=("Consolas", 12), bg="white", relief="solid", 
                 fg=color_ia, padx=20, pady=20, wraplength=500).pack(expand=True, fill=tk.BOTH)
        
        tk.Button(self.result_frame, text="NUEVO ANÁLISIS", command=self.volver, bg="#3498db", fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10, pady=10)
        
        tk.Button(self.result_frame, text="SALIR", command=self.destroy, bg="#e74c3c", fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10, pady=10)

    def volver(self):
        self.result_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    QuestionsApp().mainloop()