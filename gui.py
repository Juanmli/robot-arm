import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from analisis import generar_grafico, generar_reporte


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Robot Analyzer')
        self.geometry('800x600')
        self.config()        
        self.filtros = {
            'time_filter':tk.StringVar(self,value='realtime'),
            'productivity':tk.BooleanVar(value=True),
            'errors':tk.BooleanVar(value=True),
            'program':tk.BooleanVar(value=True),
            'modes':tk.BooleanVar(value=True),
            'hora_var_inicio':tk.StringVar(value='00'),
            'minuto_var_inicio': tk.StringVar(value='00'),
            'hora_var_fin' : tk.StringVar(value='00'),
            'minuto_var_fin':tk.StringVar(value='00')

        }        
        #contenedor izquierdo

        self.frame_izq = tk.Frame(self)
        self.frame_izq.grid()


        

        #radios
        self.frame_radios = tk.LabelFrame(self.frame_izq, text='Filtro de tiempo')
        opciones = [('Tiempo real', 'realtime'),('Anual','anual'),('Mensual','mensual'),('Diario','diario')]
        for texto, valor in opciones:
            rb = tk.Radiobutton(self.frame_radios, text=texto, variable=self.filtros['time_filter'], value=valor)
            rb.pack(anchor=tk.W)
        self.frame_radios.grid(sticky='ew')
        

        #checkboxes

        self.frame_checkboxes = tk.LabelFrame(self.frame_izq, text='Mostrar')
        info_to_show = [('Productivity','productivity'),('Errors','errors'), ('Program','program'), ('Modes','modes')]
        for clave,valor in info_to_show:
            checkbox = tk.Checkbutton(self.frame_checkboxes, text=clave, variable=self.filtros[valor], onvalue= True, offvalue=False)
            checkbox.pack(anchor=tk.W)

        self.frame_checkboxes.grid(sticky='ew')

        #Calendars y horas

        self.frame_calendars = tk.LabelFrame(self.frame_izq, text='Fecha y hora')
        self.frame_horas = tk.Frame(self.frame_calendars)

        self.calendario_inicio = Calendar(self.frame_calendars)
        self.label_calendario_inicio = tk.Label(self.frame_calendars, text='Desde')
        self.calendario_fin = Calendar(self.frame_calendars)
        self.label_calendario_fin = tk.Label(self.frame_calendars,text='Hasta')
        
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
        #self.frame_der.grid(row = 0, column =1, padx=5, pady=5, sticky='nsew')
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

    def mostrar_figura_en_canvas(self, fig):
        # Si ya hay un canvas viejo, lo destruimos (para evitar superposición)
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        # Crear nuevo canvas
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
   

        self.canvas.draw()

        # Insertar en el widget
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
       



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
            'program': self.filtros['program'].get(),
            'modes': self.filtros['modes'].get()
        }
        return filtros

    def graficar(self):
        filtros = self.obtener_filtros()
        fig = generar_grafico(filtros)  # Esta función está en kuka.py

        self.mostrar_figura_en_canvas(fig)
    
    def reporte(self):
        filtros = self.obtener_filtros()
        generar_reporte(filtros)

    

if __name__ == "__main__":
    app = App()
    app.mainloop()
        