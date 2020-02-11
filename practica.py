import tkinter as tk
from tkinter import ttk
from sense_emu import SenseHat  # pip3 install sense_emu

class Aplicacion:
    def __init__(self):
        self.sense = SenseHat()
        #  temp = sense.temp

        self.ventana1=tk.Tk()
        self.labelframe1=ttk.LabelFrame(self.ventana1, text="Medidas")        
        self.labelframe1.grid(column=0, row=0)        

        self.mediciones()

        self.canvas1=tk.Canvas(self.ventana1, width=200, height=200, background="black")
        self.canvas1.grid(column=1, row=0,rowspan = 2)

        self.labelframe2=ttk.LabelFrame(self.ventana1, text="Operaciones")        
        self.labelframe2.grid(column=0, row=1)        
        self.operaciones()

        self.labelframe3=ttk.LabelFrame(self.ventana1, text="Histórico")        
        self.labelframe3.grid(column=0, row=2, columnspan = 2, sticky=tk.W+tk.E)        

        self.listbox1=tk.Listbox(self.labelframe3)
        self.listbox1.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

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


aplicacion1=Aplicacion()