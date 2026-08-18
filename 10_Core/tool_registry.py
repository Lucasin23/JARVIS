class ToolRegistry:
    def __init__(self): self.tools={}
    def register(self,name,fn): self.tools[name]=fn
    def call(self,name,*a,**kw): return self.tools[name](*a,**kw)
    def names(self): return list(self.tools)
