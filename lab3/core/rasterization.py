import time
import numpy as np

def step_line(x0, y0, x1, y1):
    """Пошаговый алгоритм растеризации отрезка."""
    start_time = time.perf_counter()
    pixels = []
    
    dx = x1 - x0
    dy = y1 - y0
    
    if abs(dx) >= abs(dy):
        if x0 > x1:
            x0, x1, y0, y1 = x1, x0, y1, y0
        k = (y1 - y0) / dx if dx != 0 else 0.0
        b = y0 - k * x0
        for x in range(int(x0), int(x1) + 1):
            y = round(k * x + b)
            pixels.append((x, y))
    else:
        if y0 > y1:
            x0, x1, y0, y1 = x1, x0, y1, y0
        k_inv = (x1 - x0) / dy if dy != 0 else 0.0
        b_inv = x0 - k_inv * y0
        for y in range(int(y0), int(y1) + 1):
            x = round(k_inv * y + b_inv)
            pixels.append((x, y))
            
    elapsed_time = (time.perf_counter() - start_time) * 1000  # в миллисекундах
    return pixels, elapsed_time


def dda_line(x0, y0, x1, y1):
    """Алгоритм ЦДА (Цифровой дифференциальный анализатор)."""
    start_time = time.perf_counter()
    pixels = []
    
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))
    
    if steps == 0:
        return [(x0, y0)], (time.perf_counter() - start_time) * 1000
        
    x_inc = dx / steps
    y_inc = dy / steps
    
    x = x0
    y = y0
    for _ in range(int(steps) + 1):
        pixels.append((round(x), round(y)))
        x += x_inc
        y += y_inc
        
    elapsed_time = (time.perf_counter() - start_time) * 1000
    return pixels, elapsed_time


def bresenham_line(x0, y0, x1, y1):
    """Целочисленный алгоритм Брезенхема для отрезка."""
    start_time = time.perf_counter()
    pixels = []
    
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
        
    dx = x1 - x0
    dy = abs(y1 - y0)
    error = dx // 2
    ystep = 1 if y0 < y1 else -1
    
    y = y0
    for x in range(x0, x1 + 1):
        coord = (y, x) if steep else (x, y)
        pixels.append(coord)
        error -= dy
        if error < 0:
            y += ystep
            error += dx
            
    elapsed_time = (time.perf_counter() - start_time) * 1000
    return pixels, elapsed_time


def bresenham_circle(xc, yc, r):
    """Целочисленный алгоритм Брезенхема для окружности (с симметрией по 8 октантам)."""
    start_time = time.perf_counter()
    pixels = set()
    
    x = 0
    y = r
    e = 3 - 2 * r
    
    def add_symmetric_points(xc, yc, x, y):
        points = [
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x)
        ]
        for p in points:
            pixels.add(p)

    add_symmetric_points(xc, yc, x, y)
    
    while x < y:
        x += 1
        if e >= 0:
            y -= 1
            e = e + 4 * (x - y) + 10
        else:
            e = e + 4 * x + 6
        add_symmetric_points(xc, yc, x, y)
        
    elapsed_time = (time.perf_counter() - start_time) * 1000
    return list(pixels), elapsed_time