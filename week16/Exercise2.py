import numpy as np
import matplotlib.pyplot as plt


# Exercise 2
D = np.linspace(0.5, 5, 200)
T = np.linspace(0.5, 5, 200)

L = D**1.84
S = T**(-0.49)

plt.figure(1)
plt.plot(D, L)
plt.xlabel("Stem diameter D")
plt.ylabel("Leaf area L (k=1)")
plt.show()

plt.figure(2)
plt.plot(T, S)
plt.xlabel("Leaf thickness T")
plt.ylabel("Spongy mesophyll fraction S (c=1)")
plt.show()



# 2. Log L= log k + 1.84 log D ; Log S= log c -0.49 log T

# 3. 
D =(1,2,4)
T =(1,2,4)
L = np.array(D)**1.84
S = np.array(T)**(-0.49)
for i in range(len(D)):
    print(f"For D={D[i]}, L={L[i]:.2f}")

for i in range(len(T)):
    print(f"For T={T[i]}, S={S[i]:.2f}")
