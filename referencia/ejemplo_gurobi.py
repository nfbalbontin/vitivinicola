from gurobipy import *
import numpy
import time

numpy.random.seed(1)

m = 15
n = 30
I = range(m)
J = range(n)
K = range(m)

d = 0.1
b = numpy.random.randint(1,10,m)
p = -numpy.sort(-numpy.random.randint(3*m,5*m,m)) #orden decreciente
#p = numpy.sort(numpy.random.randint(3*m,5*m,m)) #orden creciente

print("b =", b)
print("p =", p)

mip = Model()

x = mip.addVars(I, J, vtype=GRB.BINARY, name="x")
y = mip.addVars(I, K, J, vtype=GRB.BINARY, name="y")

mip.setObjective(sum(p[i]*(1-d)**k*y[i,k,j] for i in I for k in K for j in J), GRB.MAXIMIZE)

mip.addConstrs(sum(x[i,j] for j in J) <= b[i] for i in I)
mip.addConstrs(sum(y[i,k,j] for k in K) == x[i,j] for i in I for j in J)
mip.addConstrs(sum(y[i,k,j] for i in I) <= 1 for k in K for j in J)
mip.addConstrs(y[i,k,j] + y[ii,kk,j] <= 1 for i in I for ii in I for k in K for kk in K for j in J if i < ii and k > kk)

mip.optimize()
