class Test :
    i = 1
    def __init__ (self) :
        self.id = Test.i
        Test.i +=1
        #print(self.id)

a = Test()
b = Test()