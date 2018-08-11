class A(object):
    def tp(self):
        print("TP of A")
        
    def kk(self):
        print("KK")
    k = 56
    
class B(A):
    def tp(self):
        print("TP of B")
        
    k = 60
    j = 70
    
a = A()
b = B()
a.tp()
a.kk()
b.tp()
b.kk()
print(a.k, b.k, b.j)
