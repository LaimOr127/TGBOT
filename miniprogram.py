##1) в 7

import numpy as np
import matplotlib.pyplot as plt

# определяем функцию f(x,y)


def f(x, y):
    return 2 * np.sin(3.8 * x) * np.cos(4.4 * y)


# задаем область по x и y
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)

# создаем сетку значений x и y
X, Y = np.meshgrid(x, y)

# получаем значения функции на сетке
Z = f(X, Y)

# строим график
fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis')

# определяем минимальное значение функции и его координаты
min_val = np.min(Z)
min_x, min_y = np.unravel_index(np.argmin(Z), Z.shape)
print('Минимальное значение функции: {}, координаты: ({}, {})'.format(min_val, x[min_x], y[min_y]))

# отображаем график
plt.show()

##2)

import numpy as np
import matplotlib.pyplot as plt

# Определяем функцию f(x, y)


def f(x, y):
    return 2 * np.sin(3.8 * x) * np.cos(4.4 * y)


# Задаем диапазон значений x и y
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)

# Создаем координатную сетку
X, Y = np.meshgrid(x, y)

# Вычисляем значения функции на координатной сетке
Z = f(X, Y)

# Строим график линий уровня
plt.contour(X, Y, Z, 20)
plt.xlabel('x')
plt.ylabel('y')
plt.title('График линий уровня функции f(x, y)')

# Задаем начальное приближение
x0, y0 = (-4, -4)

# Добавляем начальное приближение к графику
plt.scatter(x0, y0, color='red')
plt.annotate('Начальное приближение', xy=(x0, y0), xytext=(-4.5, -3.5), fontsize=10, arrowprops={'arrowstyle': '->'})

plt.show()

##3)

import numpy as np

# Определяем функцию f(x,y)


def f(x, y):
    return 2 * np.sin(3.8 * x) * np.cos(4.4 * y)


# Определяем градиент функции f(x,y)
def grad_f(x, y):
    dx = 7.6 * np.cos(3.8 * x) * np.cos(4.4 * y)
    dy = -8.8 * np.sin(3.8 * x) * np.sin(4.4 * y)
    return np.array([dx, dy])


# Определяем функцию градиентного спуска для поиска минимума функции
def gradient_descent(f, grad_f, start, lr=0.01, precision=0.0001, max_iters=1000):
    x = np.array(start)
    for i in range(max_iters):
        grad = grad_f(x[0], x[1])
    x_new = x - lr * grad
    if abs(f(x_new[0], x_new[1]) - f(x[0], x[1])) < precision:
        break
    x = x_new
    return x_new


# Пример использования функции градиентного спуска для поиска минимума функции f(x,y)
start = [0, 0]
min = gradient_descent(f, grad_f, start)
print(f"Минимум функции f(x,y) равен {f(min[0], min[1])} и достигается в точке ({min[0]}, {min[1]})")