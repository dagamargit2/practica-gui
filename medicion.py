class Medicion:
        def __init__(self, id, valor, tiempo, tipo):
            self.id = id
            self.valor = valor
            self.tiempo = tiempo
            self.tipo = tipo
        
        def get_valor(self):
            return float(self.valor)  

        def __str__(self):
            return self.id+" ("+self.tiempo+"): "+self.valor+" "+self.tipo

