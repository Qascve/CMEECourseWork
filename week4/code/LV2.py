import numpy as np
import scipy as sc
import matplotlib.pylab as plt
import sys

# Define the Lotka-Volterra model with resource density dependence
def dCR_dt(pops, t=0):
    R = pops[0]
    C = pops[1]
    # Calculate rate of change for resource and consumer
    dRdt = r * R * (1 - R/K) - a * R * C  # Resource density dependence added
    dCdt = -z * C + e * a * R * C
    
    return np.array([dRdt, dCdt])

# Get command line arguments
if len(sys.argv) != 6:
    print("Error: Need 5 arguments: r, a, z, e, K")
    sys.exit(1)

# Assign command line arguments to parameters
r = float(sys.argv[1])  # Resource growth rate
a = float(sys.argv[2])  # Consumer search rate
z = float(sys.argv[3])  # Consumer mortality rate
e = float(sys.argv[4])  # Consumer efficiency
K = float(sys.argv[5])  # Resource carrying capacity

# Create time array
t = np.linspace(0, 15, 1000)

# Set initial conditions
R0 = 10
C0 = 5 
RC0 = np.array([R0, C0])

# Run the model using scipy's integrator
pops, infodict = sc.integrate.odeint(dCR_dt, RC0, t, full_output=True)

# Plot the results
f1 = plt.figure()
plt.plot(t, pops[:,0], 'g-', label='Resource density')
plt.plot(t, pops[:,1], 'b-', label='Consumer density')
plt.grid()
plt.legend(loc='best')
plt.xlabel('Time')
plt.ylabel('Population density')
plt.title('Consumer-Resource population dynamics\n' + \
         f'r={r:.1f} a={a:.1f} z={z:.1f} e={e:.1f} K={K:.1f}')
f1.savefig('../results/LV2_model.pdf')

# Create the phase plot
f2 = plt.figure()
plt.plot(pops[:,0], pops[:,1], 'r-')
plt.grid()
plt.xlabel('Resource density')
plt.ylabel('Consumer density')
plt.title('Consumer-Resource phase plot\n' + \
         f'r={r:.1f} a={a:.1f} z={z:.1f} e={e:.1f} K={K:.1f}')
f2.savefig('../results/LV2_phase.pdf')

# Print final populations
print(f"Final Resource population: {pops[-1,0]:.3f}")
print(f"Final Consumer population: {pops[-1,1]:.3f}")

plt.show()