import tkinter as tk
import time
import threading
import queue
from tkinter import ttk
from sense_emu import SenseHat  # pip3 install sense_emu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Aplicacion:
    ANCHO_CANVAS = 200
    ALTO_CANVAS = 200

    NUM_FILAS = 10
    NUM_COLUMNAS = 10

    ANCHO_CURSOR = ANCHO_CANVAS // NUM_COLUMNAS
    ALTO_CURSOR = ALTO_CANVAS // NUM_FILAS

    def __init__(self):
        self.sense = SenseHat()
        #  temp = sense.temp

        self.data_points=list()

        self.queue=queue.Queue()    # Para comunicacion con hebra worker

        self.ventana1=tk.Tk()
        # self.ventana1.title("Prueba del control Notebook")

        self.cuaderno1 = ttk.Notebook(self.ventana1)
        self.pagina1 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina1, text="Monitorización")

        self.pagina2 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina2, text="Matplotlib")

        self.cuaderno1.grid(column=0, row=0)        

        self.mediciones()
        self.canvas()
        self.operaciones()
        self.historico()

        self.matplotlib()

        #self.ventana1.bind("<KeyPress>", self.presion_tecla)
        #self.ventana1.bind("<Button-1>", self.presion_raton)

        #Lento
        # while True:
        #    self.medir()
        #    self.ventana1.update()
        #    time.sleep(1)

        #threading.Thread(target=self.hebra_medir)
        self.ventana1.after(1000,self.llamada_medir)
        self.ventana1.after(1000,self.comprobar_joystick)

        self.ventana1.mainloop()



    def mediciones(self):
        self.labelframe1=ttk.LabelFrame(self.pagina1, text="Medidas")        
        self.labelframe1.grid(column=0, row=0)        

        self.label1=ttk.Label(self.labelframe1, text="Temperatura:")
        self.label1.grid(column=0, row=0, padx=4, pady=4)
        
        self.datoTemp=tk.StringVar()
        self.entryTemp=ttk.Entry(self.labelframe1,textvariable=self.datoTemp)
        self.entryTemp.grid(column=1, row=0, padx=4, pady=4)
        self.label2=ttk.Label(self.labelframe1, text="Presión:")        
        self.label2.grid(column=0, row=1, padx=4, pady=4)
        self.entry2=ttk.Entry(self.labelframe1)
        self.entry2.grid(column=1, row=1, padx=4, pady=4)
        self.label3=ttk.Label(self.labelframe1, text="Humedad:")
        self.label3.grid(column=0, row=2, padx=4, pady=4)
        self.entry3=ttk.Entry(self.labelframe1)
        self.entry3.grid(column=1, row=2, padx=4, pady=4)

    def canvas(self):
        self.canvas1=tk.Canvas(self.pagina1, width=self.ANCHO_CANVAS, height=self.ALTO_CANVAS, background="black")
        self.canvas1.grid(column=1, row=0,rowspan = 2)
        self.columna_cursor = 0
        self.fila_cursor = 0

        self.crear_cuadrado()        


    def operaciones(self):
        self.labelframe2=ttk.LabelFrame(self.pagina1, text="Operaciones")        
        self.labelframe2.grid(column=0, row=1)        

        self.boton2=ttk.Button(self.labelframe2, text="Lectura", command=self.medir)
        self.boton2.grid(column=0, row=0, padx=4, pady=4)
        self.boton3=ttk.Button(self.labelframe2, text="Calcular Media", command=self.comenzar_calculo)
        self.boton3.grid(column=1, row=0, padx=4, pady=4)

        self.label_worker=ttk.Label(self.labelframe2, text="Tarea parada")        
        self.label_worker.grid(column=0, row=1, padx=4, pady=4)


    def historico(self):
        self.labelframe3=ttk.LabelFrame(self.pagina1, text="Histórico")        
        self.labelframe3.grid(column=0, row=2, columnspan = 2, sticky=tk.W+tk.E)        

        self.listbox1=tk.Listbox(self.labelframe3)
        self.listbox1.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

    def matplotlib(self):
        tk.Label(self.pagina2, text="Live Plotting", bg = 'white').pack()
        self.fig = Figure()
    
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X axis")
        self.ax.set_ylabel("Y axis")
        self.ax.grid()
 
        self.graph = FigureCanvasTkAgg(self.fig, master=self.pagina2)
        self.graph.get_tk_widget().pack(side="top",fill='both',expand=True)        



    # Esta operación crea un cuadrado relleno según la temperatura en la posición
    # actual del cursor.
    # Actualiza también el cuadro de texto con la temperatura
    #
    # TODO: Comprobar si llamadas continuas a create_rectangle agotan recursos
    def medir(self):
        self.datoTemp.set(str(self.sense.temp))
        #print(self.datoTemp.get())
        #self.canvas1.itemconfig(self.cuadrado,fill='red')
        self.canvas1.create_rectangle(self.columna_cursor*self.ANCHO_CURSOR,
                                                    self.fila_cursor*self.ALTO_CURSOR,
                                                    (self.columna_cursor+1)*self.ANCHO_CURSOR,
                                                    (self.fila_cursor+1)*self.ALTO_CURSOR,
                                                    fill = self.color(float(self.datoTemp.get())))        
        self.canvas1.tag_raise(self.cuadrado)                                                    

    # Esta función utiliza las coordenadas actuales del cursor para crear el
    # cuadrado con marco rojo    
    def crear_cuadrado(self):
        self.cuadrado=self.canvas1.create_rectangle(self.columna_cursor*self.ANCHO_CURSOR,
                                                    self.fila_cursor*self.ALTO_CURSOR,
                                                    (self.columna_cursor+1)*self.ANCHO_CURSOR,
                                                    (self.fila_cursor+1)*self.ALTO_CURSOR,
                                                    outline = 'red')
    
    def presion_tecla(self, evento):        
        if evento.keysym=='Right':
            self.columna_cursor=self.columna_cursor+1
            self.canvas1.move(self.cuadrado, self.ANCHO_CURSOR, 0)
        if evento.keysym=='Left':
            self.columna_cursor=self.columna_cursor-1            
            self.canvas1.move(self.cuadrado, -self.ANCHO_CURSOR, 0)
        if evento.keysym=='Down':
            self.fila_cursor=self.fila_cursor+1            
            self.canvas1.move(self.cuadrado, 0, self.ALTO_CURSOR)
        if evento.keysym=='Up':
            self.fila_cursor=self.fila_cursor-1            
            self.canvas1.move(self.cuadrado, 0, -self.ALTO_CURSOR)

    # TODO: deshabilitar cuando está en otra ventana
    def presion_raton(self, evento):        
        nueva_fila=int(evento.y/self.ANCHO_CURSOR)
        nueva_columna=int(evento.x/self.ALTO_CURSOR)

        difc = nueva_columna-self.columna_cursor
        diff = nueva_fila-self.fila_cursor

        self.fila_cursor=nueva_fila
        self.columna_cursor=nueva_columna

        self.canvas1.move(self.cuadrado, difc*self.ANCHO_CURSOR, 
                                         diff*self.ALTO_CURSOR)


    def color(self,temp):
        if temp<25:
            return 'cyan'
        elif temp<50:
            return 'blue'
        elif temp<75:
            return 'yellow'
        else:
            return 'red'


    def pinta_grafica(self):
        self.ax.cla()
        self.ax.grid()
        self.data_points.append(self.sense.temp)
        if len(self.data_points)>10:
            del self.data_points[0]
        dpts = self.data_points
        self.ax.plot(range(10), dpts, marker='o', color='orange')
        self.graph.draw()



    def llamada_medir(self):
        self.ventana1.after(1000,self.llamada_medir)
        self.medir()
        self.pinta_grafica()


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


    def process_queue(self):
        try:
            msg = self.queue.get(0)
            self.label_worker.configure(text=msg)
            # Show result of the task if needed
        except queue.Empty:
            self.ventana1.after(1000, self.process_queue)

    def comenzar_calculo(self):
        self.label_worker.configure(text='Tarea arrancada')
        ThreadedTask(self.queue).start()
        self.ventana1.after(1000, self.process_queue)



class ThreadedTask(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        time.sleep(10)  # Simulate long running process
        self.queue.put("Tarea parada")



aplicacion1=Aplicacion()