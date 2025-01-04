'''
Raw time trace:
- By default stores reference-substracted data 
- simple class to have access to x,y,z,t positions 
'''

class RawTrace():
    '''
    basic x,y,z time trace 
    '''
    def __init__(self,x,y,z,t) -> None:
        self.x = x
        self.y = y 
        self.z = z
        self.t = t 
        pass