import tkinter as tk
import queue
from tkinter import ttk
from sense_emu import SenseHat  # pip3 install sense_emu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import worker
import datetime


class Aplicacion:
    ANCHO_CANVAS = 200
    ALTO_CANVAS = 200

    NUM_FILAS = 10
    NUM_COLUMNAS = 10

    ANCHO_CURSOR = ANCHO_CANVAS // NUM_COLUMNAS
    ALTO_CURSOR = ALTO_CANVAS // NUM_FILAS

    TEMPERATURA = 1
    PRESION = 2
    HUMEDAD = 3

    def __init__(self):
        self.sense = SenseHat()        

        self.midiendo = True        # Mediciones activas
        self.data_points=list()     # Puntos para la gráfica

        self.queue=queue.Queue()    # Para comunicacion con hebra worker
        self.cuadrados = dict()       # Para ahorrar recursos GUI guardamos los cuadrados

        self.list_max = [105, 1260, 100]    # Temp, pres, hum


        self.ventana1=tk.Tk()
        self.ventana1.title("Práctica GUI SenseHat")

        self.cuaderno1 = ttk.Notebook(self.ventana1)
        self.pagina1 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina1, text="Monitorización")

        self.pagina2 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina2, text="Matplotlib")

        self.cuaderno1.grid(column=0, row=0)        

        # Página 1
        self.operaciones()
        self.mediciones()
        self.canvas()
        self.historico()

        # Página 2
        self.matplotlib()

        # Ya no utilizado. Controlando posición desde el emulador
        #self.ventana1.bind("<KeyPress>", self.presion_tecla)
        #self.ventana1.bind("<Button-1>", self.presion_raton)

        # Lento
        # while True:
        #    self.medir()
        #    self.ventana1.update()
        #    time.sleep(1)

        self.ventana1.after(1000,self.llamada_medir)
        self.ventana1.after(1000,self.comprobar_joystick)
        self.ventana1.mainloop()


    # Métodos para colocar controles en interfaz gráfica

    def mediciones(self):
        self.labelframe1=ttk.LabelFrame(self.pagina1, text="Medidas")        
        self.labelframe1.grid(column=0, row=1)        

        self.seleccion_tipo_dato=tk.IntVar(value=self.TEMPERATURA)

        self.radio1=tk.Radiobutton(self.labelframe1,text="Temperatura", variable=self.seleccion_tipo_dato, value=self.TEMPERATURA)
        self.radio1.grid(column=0, row=1, padx=4, pady=4)
        
        self.datoSense=tk.StringVar()
        self.entryTemp=ttk.Entry(self.labelframe1,textvariable=self.datoSense)
        self.entryTemp.grid(column=1, row=0, padx=4, pady=4)

        self.radio2=tk.Radiobutton(self.labelframe1,text="Presión", variable=self.seleccion_tipo_dato, value=self.PRESION)
        self.radio2.grid(column=1, row=1, padx=4, pady=4)

        self.radio3=tk.Radiobutton(self.labelframe1,text="Humedad", variable=self.seleccion_tipo_dato, value=self.HUMEDAD)
        self.radio3.grid(column=2, row=1, padx=4, pady=4)


    def canvas(self):
        self.canvas1=tk.Canvas(self.pagina1, width=self.ANCHO_CANVAS, height=self.ALTO_CANVAS, background="black")
        self.canvas1.grid(column=1, row=0,rowspan = 2)
        self.columna_cursor = 0
        self.fila_cursor = 0

        self.crear_cuadrado()        


    def operaciones(self):
        self.labelframe2=ttk.LabelFrame(self.pagina1, text="Operaciones")        
        self.labelframe2.grid(column=0, row=0)        

        self.frame=tk.Frame(self.labelframe2)
        self.frame.grid(column=0, row=0)

        self.boton_start_stop=ttk.Button(self.frame, text="Parar", command=self.start_stop)
        self.boton_start_stop.pack(side=tk.LEFT)
        self.boton3=ttk.Button(self.frame, text="Calcular Media", command=self.comenzar_calculo)
        self.boton3.pack(side=tk.RIGHT)

        self.label_worker=ttk.Label(self.labelframe2, text="Tarea parada")        
        self.label_worker.grid(column=0, row=1, padx=4, pady=4)


    def historico(self):
        self.labelframe3=ttk.LabelFrame(self.pagina1, text="Histórico")        
        self.labelframe3.grid(column=0, row=2, columnspan = 2, sticky=tk.W+tk.E)        

        self.frame2=tk.Frame(self.labelframe3)
        self.frame2.pack(side = tk.TOP, fill = tk.BOTH, expand=True)
        #self.listbox1=tk.Listbox(self.frame2)
        #self.listbox1.pack(side = tk.LEFT, fill = tk.BOTH, expand=True)
        self.tree = ttk.Treeview(self.frame2)
        self.tree.pack(side = tk.LEFT, fill = tk.BOTH, expand=True)

        self.scroll1 = tk.Scrollbar(self.frame2, orient=tk.VERTICAL)
        self.scroll1.configure(command=self.tree.yview)         
        self.scroll1.pack(side = tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=self.scroll1.set)   # 2 conexiones tree <-> scroll

        self.tree['columns'] = ('value', 'when', 'type')

        self.tree.heading('#0', text='#Num')
        self.tree.heading('value', text='Valor')
        self.tree.heading('when', text='Fecha/Hora')
        self.tree.heading('type', text='Tipo')


        self.seleccion=tk.IntVar()
        self.check1=tk.Checkbutton(self.labelframe3,text="Añadir a lista", variable=self.seleccion)
        self.check1.pack(side = tk.BOTTOM)

        self.boton_limpiar=tk.Button(self.labelframe3, text="Limpiar", command=self.limpiar_historico)
        self.boton_limpiar.pack(side = tk.BOTTOM)



    def matplotlib(self):
        tk.Label(self.pagina2, text="Live Plotting", bg = 'white').pack()
        self.fig = Figure()
    
        self.ax = self.fig.add_subplot(111) # https://matplotlib.org/3.1.3/api/_as_gen/matplotlib.pyplot.subplot.html: nºfilas, nºcolumnas, índice subplotcd
        self.ax.set_xlabel("X axis")
        self.ax.set_ylabel("Y axis")
        self.ax.cla()   # clear axis
        self.ax.grid()  # configura grid
        self.ax.set_xlim(0, 9)
        self.ax.set_ylim(0, 100)

        self.line, = self.ax.plot([], [], marker='o', color='orange')


        self.graph = FigureCanvasTkAgg(self.fig, master=self.pagina2)   # Agg: Anti-Grain geometry rendering engine
        self.graph.get_tk_widget().pack(side="top",fill='both',expand=True)        

        self.ani = animation.FuncAnimation(self.fig, self.pinta_grafica, interval=1000, blit=False)



    # Esta función utiliza las coordenadas actuales del cursor para crear el
    # cuadrado con marco rojo    
    def crear_cuadrado(self):
        # Solo se crea una vez. No se "desperdician" recursos
        self.cuadrado=self.canvas1.create_rectangle(self.columna_cursor*self.ANCHO_CURSOR,
                                                    self.fila_cursor*self.ALTO_CURSOR,
                                                    (self.columna_cursor+1)*self.ANCHO_CURSOR,
                                                    (self.fila_cursor+1)*self.ALTO_CURSOR,
                                                    outline = 'red')

    

    # Métodos relacionados con mediciones periódicas


    def start_stop(self):
        if self.midiendo:
            self.midiendo = False
            self.boton_start_stop.configure(text='Comenzar')
        else:
            self.midiendo = True
            self.boton_start_stop.configure(text='Parar')


    def limpiar_historico(self):
        self.tree.delete(*self.tree.get_children()) # * "desempaqueta" argumento     


    def str_tipo_medicion(self,tipo_medicion):
        if tipo_medicion==self.TEMPERATURA:
            res="Temperatura"
        elif tipo_medicion==self.PRESION:
            res="Presión"
        else:
            res="Humedad"
        
        return res


    # Esta operación crea un cuadrado relleno según la temperatura en la posición
    # actual del cursor.
    # Actualiza también el cuadro de texto con la temperatura
    #
    # TODO: Comprobar si llamadas continuas a create_rectangle agotan recursos
    def medir(self):
        if self.seleccion_tipo_dato.get()==self.TEMPERATURA:
            self.datoSense.set(str(self.sense.temp))
        elif self.seleccion_tipo_dato.get()==self.PRESION:
            self.datoSense.set(str(self.sense.pressure))
        else:
           self.datoSense.set(str(self.sense.humidity))
 
        #print(self.datoSense.get())
        #self.canvas1.itemconfig(self.cuadrado,fill='red')

        # Evitamos crear rectángulos indefinidamente
        clave = (self.fila_cursor,self.columna_cursor)
        if clave in self.cuadrados:
            cuadrado = self.cuadrados[clave]
            self.canvas1.itemconfig(cuadrado,fill=self.color(float(self.datoSense.get()),
                                                                self.seleccion_tipo_dato.get()))
        else:
            self.cuadrados[clave] = self.canvas1.create_rectangle(self.columna_cursor*self.ANCHO_CURSOR,
                                                    self.fila_cursor*self.ALTO_CURSOR,
                                                    (self.columna_cursor+1)*self.ANCHO_CURSOR,
                                                    (self.fila_cursor+1)*self.ALTO_CURSOR,
                                                    fill = self.color(float(self.datoSense.get()),
                                                                self.seleccion_tipo_dato.get()))
        

        self.canvas1.tag_raise(self.cuadrado) # Para que el cursor siempre esté en primer plano                                                   

        if self.seleccion.get()==1:
        #    self.listbox1.insert(0,self.datoSense.get())
            now = datetime.datetime.now()
            self.tree.insert('', 0, text=str(len(self.tree.get_children())), values=(self.datoSense.get(),now.strftime("%Y-%m-%d %H:%M:%S"),
                            self.str_tipo_medicion(self.seleccion_tipo_dato.get())))


    # def presion_tecla(self, evento):        
    #     if evento.keysym=='Right':
    #         self.columna_cursor=self.columna_cursor+1
    #         self.canvas1.move(self.cuadrado, self.ANCHO_CURSOR, 0)
    #     if evento.keysym=='Left':
    #         self.columna_cursor=self.columna_cursor-1            
    #         self.canvas1.move(self.cuadrado, -self.ANCHO_CURSOR, 0)
    #     if evento.keysym=='Down':
    #         self.fila_cursor=self.fila_cursor+1            
    #         self.canvas1.move(self.cuadrado, 0, self.ALTO_CURSOR)
    #     if evento.keysym=='Up':
    #         self.fila_cursor=self.fila_cursor-1            
    #         self.canvas1.move(self.cuadrado, 0, -self.ALTO_CURSOR)

    # # TODO: deshabilitar cuando está en otra ventana
    # def presion_raton(self, evento):        
    #     nueva_fila=int(evento.y/self.ANCHO_CURSOR)
    #     nueva_columna=int(evento.x/self.ALTO_CURSOR)

    #     difc = nueva_columna-self.columna_cursor
    #     diff = nueva_fila-self.fila_cursor

    #     self.fila_cursor=nueva_fila
    #     self.columna_cursor=nueva_columna

    #     self.canvas1.move(self.cuadrado, difc*self.ANCHO_CURSOR, 
    #                                      diff*self.ALTO_CURSOR)


    def color(self,valor,tipo):
        if valor<0.25*self.list_max[tipo-1]:
            return 'cyan'
        elif valor<0.5*self.list_max[tipo-1]:
            return 'blue'
        elif valor<0.75*self.list_max[tipo-1]:
            return 'yellow'
        else:
            return 'red'



    def pinta_grafica(self,i):
        self.data_points.append(self.sense.temp)
        if len(self.data_points)>10:
            del self.data_points[0]
        self.line.set_data(range(len(self.data_points)),self.data_points)
        self.ax.set_ylim(min(self.data_points)-1,max(self.data_points)+1)



    def llamada_medir(self):
        self.ventana1.after(100,self.llamada_medir)
        if self.midiendo:
            self.medir()


    # Métodos relacionados con movimiento cursor

    def move_dot(self,event):
        #print(event)
        if event.action in ('pressed', 'held'):
            if event.direction=='right':
                self.columna_cursor=self.columna_cursor+1
                self.canvas1.move(self.cuadrado, self.ANCHO_CURSOR, 0)
            if event.direction=='left':
                self.columna_cursor=self.columna_cursor-1            
                self.canvas1.move(self.cuadrado, -self.ANCHO_CURSOR, 0)
            if event.direction=='down':
                self.fila_cursor=self.fila_cursor+1            
                self.canvas1.move(self.cuadrado, 0, self.ALTO_CURSOR)
            if event.direction=='up':
                self.fila_cursor=self.fila_cursor-1            
                self.canvas1.move(self.cuadrado, 0, -self.ALTO_CURSOR)


    def comprobar_joystick(self):
        self.ventana1.after(1000,self.comprobar_joystick)
        for event in self.sense.stick.get_events():
            self.move_dot(event)


    # Metodos relacionados con "tarea larga duración"

    def process_queue(self):
        try:
            msg = self.queue.get(0)
            self.label_worker.configure(text=msg)
            # Show result of the task if needed
        except queue.Empty:
            self.ventana1.after(1000, self.process_queue)

    def comenzar_calculo(self):
        self.label_worker.configure(text='Tarea arrancada')        
        worker.ThreadedTask(self.queue).start()
        self.ventana1.after(1000, self.process_queue)

aplicacion1=Aplicacion()
