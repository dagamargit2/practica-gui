import tkinter as tk
import time
import threading
from tkinter import ttk
from sense_emu import SenseHat  # pip3 install sense_emu


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

        self.ventana1=tk.Tk()
        self.labelframe1=ttk.LabelFrame(self.ventana1, text="Medidas")        
        self.labelframe1.grid(column=0, row=0)        

        self.mediciones()

        self.canvas1=tk.Canvas(self.ventana1, width=self.ANCHO_CANVAS, height=self.ALTO_CANVAS, background="black")
        self.canvas1.grid(column=1, row=0,rowspan = 2)
        self.columna_cursor = 0
        self.fila_cursor = 0

        self.crear_cuadrado()        

        self.labelframe2=ttk.LabelFrame(self.ventana1, text="Operaciones")        
        self.labelframe2.grid(column=0, row=1)        
        self.operaciones()

        self.labelframe3=ttk.LabelFrame(self.ventana1, text="Histórico")        
        self.labelframe3.grid(column=0, row=2, columnspan = 2, sticky=tk.W+tk.E)        

        self.listbox1=tk.Listbox(self.labelframe3)
        self.listbox1.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

        self.ventana1.bind("<KeyPress>", self.presion_tecla)

        #Lento
        # while True:
        #    self.medir()
        #    self.ventana1.update()
        #    time.sleep(1)

        #threading.Thread(target=self.hebra_medir)
        self.ventana1.after(1000,self.hebra_medir)
        self.ventana1.mainloop()

    def mediciones(self):
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


    def operaciones(self):
        self.boton2=ttk.Button(self.labelframe2, text="Lectura", command=self.medir)
        self.boton2.grid(column=0, row=0, padx=4, pady=4)
        self.boton3=ttk.Button(self.labelframe2, text="Añadir")
        self.boton3.grid(column=1, row=0, padx=4, pady=4)

    def medir(self):
        self.datoTemp.set(str(self.sense.temp))
        print(self.datoTemp.get())
        #self.canvas1.itemconfig(self.cuadrado,fill='red')
        self.canvas1.create_rectangle(self.columna_cursor*self.ANCHO_CURSOR,
                                                    self.fila_cursor*self.ALTO_CURSOR,
                                                    (self.columna_cursor+1)*self.ANCHO_CURSOR,
                                                    (self.fila_cursor+1)*self.ALTO_CURSOR,
                                                    fill = self.color(float(self.datoTemp.get())))        
    
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

    def color(self,temp):
        if temp>50:
            return 'red'
        else:
            return 'blue'

    def hebra_medir(self):
        #while True:     
        self.ventana1.after(1000,self.hebra_medir)
        self.medir()
        #time.sleep(1)


aplicacion1=Aplicacion()