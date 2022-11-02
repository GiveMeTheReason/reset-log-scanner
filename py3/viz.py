import numpy as np
import matplotlib.pyplot as plt

r = 1
l = 3
sensors = 12
alpha_step = 2 * np.pi / sensors


x0 = r * np.cos(np.linspace(0, 2 * np.pi, sensors))
y0 = r * np.sin(np.linspace(0, 2 * np.pi, sensors))
z0 = 0 * np.ones(sensors)

x1 = r * np.cos(np.linspace(0, 2 * np.pi, sensors))
y1 = r * np.sin(np.linspace(0, 2 * np.pi, sensors))
z1 = l * np.ones(sensors)

n = 50
x0_arc = r * np.cos(np.linspace(0, 2 * np.pi / sensors, n))
y0_arc = r * np.sin(np.linspace(0, 2 * np.pi / sensors, n))
z0_arc = 0 * np.ones(n)

x1_arc = r * np.cos(np.linspace(0, 2 * np.pi / sensors, n))
y1_arc = r * np.sin(np.linspace(0, 2 * np.pi / sensors, n))
z1_arc = l * np.ones(n)


fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.scatter(x0, y0, z0, marker='o')
ax.scatter(x1, y1, z1, marker='o')

ax.plot(x0_arc, y0_arc, z0_arc)
ax.plot(x1_arc, y1_arc, z1_arc)

ax.plot(r * np.cos(np.array([0, 0]) * alpha_step), r * np.sin(np.array([0, 0]) * alpha_step), np.array([0, l]))
ax.plot(r * np.cos(np.array([1, 1]) * alpha_step), r * np.sin(np.array([1, 1]) * alpha_step), np.array([0, l]))

ax.plot(np.array([0, 0]), np.array([0, 0]), np.array([0, l]))
ax.plot(r * np.array([0, np.cos(0 * alpha_step)]), r * np.array([0, np.sin(0 * alpha_step)]), np.array([0, 0])) 
ax.plot(r * np.array([0, np.cos(1 * alpha_step)]), r * np.array([0, np.sin(1 * alpha_step)]), np.array([0, 0]))
ax.plot(r * np.array([0, np.cos(0 * alpha_step)]), r * np.array([0, np.sin(0 * alpha_step)]), np.array([l, l])) 
ax.plot(r * np.array([0, np.cos(1 * alpha_step)]), r * np.array([0, np.sin(1 * alpha_step)]), np.array([l, l]))

ax.axis('equal')
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
plt.show()
