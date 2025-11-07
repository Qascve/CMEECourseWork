import numpy as np
import scipy as sc
import matplotlib.pylab as plt

def dCR_dt(pops, t=0):

    R = pops[0]
    C = pops[1]
    dRdt = r * R - a * R * C 
    dCdt = -z * C + e * a * R * C
    
    return np.array([dRdt, dCdt])

r = 1.
a = 0.1 
z = 1.5
e = 0.75
t = np.linspace(0, 15, 1000)

R0 = 10
C0 = 5 
RC0 = np.array([R0, C0])
pops, infodict = sc.integrate.odeint(dCR_dt, RC0, t, full_output=True)

type(infodict)
infodict.keys()
infodict['message']

f1 = plt.figure()

plt.plot(t, pops[:,0], 'g-', label='Resource density') # Plot
plt.plot(t, pops[:,1]  , 'b-', label='Consumer density')
plt.grid()
plt.legend(loc='best')
plt.xlabel('Time')
plt.ylabel('Population density')
plt.title('Consumer-Resource population dynamics')
# plt.show()# To display the figure

f1.savefig('../results/LV_model.pdf') #Save figure


f2 = plt.figure()
plt.plot(pops[:,0],pops[:,1]  , 'r-') # Plot
plt.grid()
plt.xlabel('Resource density')
plt.ylabel('Consumer density')
plt.title('Consumer-Resource population dynamics')
# plt.show()# To display the figure

f2.savefig('../results/LV_model2.pdf') #Save figure