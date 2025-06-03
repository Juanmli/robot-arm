import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from graficos import crear_graficos
from exportador import generar_reporte
from calendar import monthrange
from analisis import crear_dataframes

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Robot Analyzer')
        self.geometry('800x600')
        self.config()        
        self.filtros = {
            'time_filter':tk.StringVar(self,value='hora'),
            'productivity':tk.BooleanVar(value=True),
            'errors':tk.BooleanVar(value=True),
            'programs':tk.BooleanVar(value=True),
            'modes':tk.BooleanVar(value=True),
            'hora_var_inicio':tk.StringVar(value='00'),
            'minuto_var_inicio': tk.StringVar(value='00'),
            'hora_var_fin' : tk.StringVar(value='00'),
            'minuto_var_fin':tk.StringVar(value='00'),
        }     

        
        #contenedor izquierdo
        # Contenedor izquierdo con scroll
        self.canvas_izq = tk.Canvas(self, width=210)
        self.scrollbar_izq = tk.Scrollbar(self, orient='vertical', command=self.canvas_izq.yview)
        self.frame_izq = tk.Frame(self.canvas_izq)

        self.frame_izq.bind("<Configure>", lambda e: self.canvas_izq.configure(scrollregion=self.canvas_izq.bbox("all")))
        self.canvas_izq.create_window((0, 0), window=self.frame_izq, anchor='nw')
        self.canvas_izq.configure(yscrollcommand=self.scrollbar_izq.set)

        self.canvas_izq.grid(row=0, column=0, sticky='ns')
        self.scrollbar_izq.grid(row=0, column=0, sticky='nse')

        # Soporte para rueda del mouse
        def _on_mousewheel_izq(event):
            self.canvas_izq.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas_izq.bind_all("<MouseWheel>", _on_mousewheel_izq)

        self.habilitar_scroll_con_mouse(self.canvas_izq, self.frame_izq)
        

        #radios
        self.frame_radios = tk.LabelFrame(self.frame_izq, text='Filtro de tiempo')
        opciones = [('Anual','anual'),('Mensual','mensual'),('Diario','diario'),('Hora', 'hora')]
        for texto, valor in opciones:
            rb = tk.Radiobutton(self.frame_radios, text=texto, variable=self.filtros['time_filter'], value=valor, command=self.radio_presionado)
            rb.pack(anchor=tk.W)
        self.frame_radios.grid(sticky='ew')
        

        #checkboxes

        self.frame_checkboxes = tk.LabelFrame(self.frame_izq, text='Mostrar')
        info_to_show = [('Productivity','productivity'),('Errors','errors'), ('Programs','programs'), ('Modes','modes')]
        for clave,valor in info_to_show:
            checkbox = tk.Checkbutton(self.frame_checkboxes, text=clave, variable=self.filtros[valor], onvalue= True, offvalue=False, command=self.graficar)
            checkbox.pack(anchor=tk.W)

        self.frame_checkboxes.grid(sticky='ew')

        #Calendars y horas

        self.frame_calendars = tk.LabelFrame(self.frame_izq, text='Fecha y hora')
        self.frame_horas = tk.Frame(self.frame_calendars)

        self.calendario_inicio = Calendar(self.frame_calendars, font='Arial 6')
        self.label_calendario_inicio = tk.Label(self.frame_calendars, text='Desde')
        self.calendario_fin = Calendar(self.frame_calendars, font='Arial 6')
        self.label_calendario_fin = tk.Label(self.frame_calendars,text='Hasta')
        self.calendario_fin.bind("<<CalendarSelected>>", lambda e: self.sincronizar_fechas_si_horario())
        self.calendario_inicio.bind("<<CalendarSelected>>", lambda e: self.sincronizar_fechas_si_horario())
        #hora de inicio
        self.frame_hora_inicio = tk.Frame(self.frame_calendars)
        self.hora_inicio_spinbox = tk.Spinbox(self.frame_hora_inicio, from_=0, to=23 , textvariable=self.filtros['hora_var_inicio'],width=2, format="%02.0f",wrap=True)
        self.minuto_inicio_spinbox=tk.Spinbox(self.frame_hora_inicio, from_=0, to=59, textvariable=self.filtros['minuto_var_inicio'],width=2, format="%02.0f",wrap=True)

        self.hora_inicio_spinbox.grid(row=0, column=0)
        tk.Label(self.frame_hora_inicio, text=':').grid(row=0, column=1)
        self.minuto_inicio_spinbox.grid(row=0,column=2)

        #hora final
        self.frame_hora_fin = tk.Frame(self.frame_calendars)
        self.hora_fin_spinbox = tk.Spinbox(self.frame_hora_fin, from_=0, to=23 , textvariable=self.filtros['hora_var_fin'],width=2, format="%02.0f",wrap=True)
        self.minuto_fin_spinbox=tk.Spinbox(self.frame_hora_fin, from_=0, to=59, textvariable=self.filtros['minuto_var_fin'],width=2, format="%02.0f",wrap=True)

        self.hora_fin_spinbox.grid(row=0, column=0)
        tk.Label(self.frame_hora_inicio, text=':').grid(row=0, column=1)
        self.minuto_fin_spinbox.grid(row=0,column=2)


        self.label_calendario_inicio.pack(anchor=tk.W)
        self.calendario_inicio.pack(padx= 5, pady=2)
        self.frame_hora_inicio.pack(padx=5, pady= 2)
        self.label_calendario_fin.pack(anchor=tk.W)
        self.calendario_fin.pack(padx=5, pady=2)
        self.frame_hora_fin.pack(padx=5, pady= 2)
        self.frame_calendars.grid()

        self.boton_fechas = tk.Button(self.frame_calendars,text='Graficar',command=self.graficar)
        self.boton_fechas.pack()


        #frame derecho

        self.frame_der = tk.LabelFrame(self)    
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame_der.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        #Frame graficos

        self.frame_grafico = tk.Frame(self.frame_der, bg='white')
        self.frame_grafico.pack(fill='both' ,expand=True)

        #Frame exportar


        self.frame_exportar = tk.Frame(self.frame_der)
        self.frame_exportar.pack()

        self.boton_reporte = tk.Button(self.frame_exportar, text='generar_reporte', command=self.reporte)
        self.boton_reporte.pack(side='right')
    
        #Crear diccionario con todos los dfs.    
        self.dataframes = crear_dataframes(self.obtener_filtros())


    def radio_presionado(self):    
        self.graficar()
        
    def sincronizar_fechas_si_horario(self):
        self.hora_inicio_spinbox.config(state="normal")
        self.hora_fin_spinbox.config(state="normal")
        self.minuto_inicio_spinbox.config(state="normal")
        self.minuto_fin_spinbox.config(state="normal")
    
        print("sicnronizar calendarios")
        if self.filtros["time_filter"].get() == "hora":
            fecha = self.calendario_inicio.selection_get()
            self.calendario_fin.selection_set(fecha)
        else:        
                # Ajustar los calendarios
            fecha_ini = self.ajustar_fecha_inicio_a_mes(self.calendario_inicio.get_date())
            fecha_fin = self.ajustar_fecha_fin_a_mes(self.calendario_fin.get_date())

            self.calendario_inicio.selection_set(fecha_ini)
            self.calendario_fin.selection_set(fecha_fin)

            # Deshabilitar spinboxes de hora si los tenés
            self.hora_inicio_spinbox.config(state="disabled")
            self.hora_fin_spinbox.config(state="disabled")
            self.minuto_inicio_spinbox.config(state="disabled")
            self.minuto_fin_spinbox.config(state="disabled")

        
    def ajustar_fecha_inicio_a_mes(self, fecha_str):
        fecha = datetime.strptime(fecha_str, "%m/%d/%y")
        return datetime(fecha.year, fecha.month, 1)

    def ajustar_fecha_fin_a_mes(self, fecha_str):
        fecha = datetime.strptime(fecha_str, "%m/%d/%y")
        ultimo_dia = monthrange(fecha.year, fecha.month)[1]
        return datetime(fecha.year, fecha.month, ultimo_dia)
       

    def mostrar_figura_en_canvas(self, fig):
        # Eliminar canvas viejo si existe
        if hasattr(self, 'canvas_frame'):
            self.canvas_frame.destroy()

        # Contenedor con scroll
        self.canvas_frame = tk.Frame(self.frame_grafico)
        self.canvas_frame.pack(fill='both', expand=True)

        # Canvas de Tkinter
        canvas_tk = tk.Canvas(self.canvas_frame, bg='white')
        canvas_tk.pack(side='left', fill='both', expand=True)

        # Scrollbar vertical
        scrollbar = tk.Scrollbar(self.canvas_frame, orient='vertical', command=canvas_tk.yview)
        scrollbar.pack(side='right', fill='y')
        canvas_tk.configure(yscrollcommand=scrollbar.set)


        # Frame interno dentro del canvas
        frame_interno = tk.Frame(canvas_tk, bg='white')
        canvas_tk.create_window((0, 0), window=frame_interno, anchor='nw')

        # Canvas de matplotlib dentro del frame interno
        self.canvas = FigureCanvasTkAgg(fig, master=frame_interno)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        # Ajustar scroll al tamaño del contenido
        def ajustar_scroll(event):
            canvas_tk.configure(scrollregion=canvas_tk.bbox('all'))

        frame_interno.bind("<Configure>", ajustar_scroll)

        # Vincular solo cuando el mouse entra/sale del área scrollable
        def _on_mousewheel(event):
            canvas_tk.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bound_to_mousewheel(event):
            canvas_tk.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbound_to_mousewheel(event):
            canvas_tk.unbind_all("<MouseWheel>")

        frame_interno.bind("<Enter>", _bound_to_mousewheel)
        frame_interno.bind("<Leave>", _unbound_to_mousewheel)
        self.habilitar_scroll_con_mouse(canvas_tk, self.frame_grafico)

    def habilitar_scroll_con_mouse(self, canvas, widget_scrollable):
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bound_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbound_to_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        widget_scrollable.bind("<Enter>", _bound_to_mousewheel)
        widget_scrollable.bind("<Leave>", _unbound_to_mousewheel)

    

    def obtener_timestamp(self,calendar):
        
        fecha_str = calendar.get_date()

        hora = 0
        minuto = 0

        if (calendar == self.calendario_inicio):
            hora = int(self.filtros['hora_var_inicio'].get())
            minuto = int(self.filtros['minuto_var_inicio'].get())
        else:
            hora = int(self.filtros['hora_var_fin'].get())
            minuto = int(self.filtros['minuto_var_fin'].get())

        fecha = datetime.strptime(fecha_str, "%m/%d/%y")
    
    
        fecha_completa = datetime(
        year=fecha.year,
        month=fecha.month,
        day=fecha.day,
        hour=int(hora),
        minute=int(minuto)
        )        
        return fecha_completa


    def obtener_filtros(self) ->dict :
        filtros = dict
        filtros = {

            'tiempo_inicial' : self.obtener_timestamp(self.calendario_inicio),
            'tiempo_final' : self.obtener_timestamp(self.calendario_fin),
            'time_filter': self.filtros['time_filter'].get(),
            'productivity': self.filtros['productivity'].get(),
            'errors':  self.filtros['errors'].get(),
            'programs': self.filtros['programs'].get(),
            'modes': self.filtros['modes'].get()
        }
        return filtros

    def graficar(self):
        self.sincronizar_fechas_si_horario()
        filtros = self.obtener_filtros()
        fig = crear_graficos(self.dataframes,filtros)
        self.mostrar_figura_en_canvas(fig)
        print('grafico hecho')                

    def reporte(self):
        filtros = self.obtener_filtros()
        generar_reporte(filtros)
    

if __name__ == "__main__":
    app = App()
    app.mainloop()
        
