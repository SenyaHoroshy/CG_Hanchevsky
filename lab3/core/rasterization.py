import time
import math


def step_line(x0, y0, x1, y1):
    """Пошаговый алгоритм растеризации отрезка"""
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
            pixels.append((x, y, 1.0))
    else:
        if y0 > y1:
            x0, x1, y0, y1 = x1, x0, y1, y0
        k_inv = (x1 - x0) / dy if dy != 0 else 0.0
        b_inv = x0 - k_inv * y0
        for y in range(int(y0), int(y1) + 1):
            x = round(k_inv * y + b_inv)
            pixels.append((x, y, 1.0))

    elapsed_time = (time.perf_counter() - start_time) * 1000
    return pixels, elapsed_time


def dda_line(x0, y0, x1, y1):
    """Алгоритм ЦДА (Цифровой дифференциальный анализатор)"""
    start_time = time.perf_counter()
    pixels = []

    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        return [(x0, y0, 1.0)], (time.perf_counter() - start_time) * 1000

    x_inc = dx / steps
    y_inc = dy / steps

    x = float(x0)
    y = float(y0)
    for _ in range(int(steps) + 1):
        pixels.append((round(x), round(y), 1.0))
        x += x_inc
        y += y_inc

    elapsed_time = (time.perf_counter() - start_time) * 1000
    return pixels, elapsed_time


def bresenham_line(x0, y0, x1, y1):
    """Целочисленный алгоритм Брезенхема для отрезка"""
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
        coord = (y, x, 1.0) if steep else (x, y, 1.0)
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

    if r < 0:
        return [], (time.perf_counter() - start_time) * 1000

    pixels = set()
    x = 0
    y = int(r)
    e = 3 - 2 * y

    def add_symmetric_points(cx, cy, px, py):
        points = [
            (cx + px, cy + py), (cx - px, cy + py),
            (cx + px, cy - py), (cx - px, cy - py),
            (cx + py, cy + px), (cx - py, cy + px),
            (cx + py, cy - px), (cx - py, cy - px)
        ]
        for p in points:
            pixels.add(p)

    add_symmetric_points(xc, yc, x, y)

    while x <= y:
        if e >= 0:
            e = e + 4 * (x - y) + 10
            y -= 1
        else:
            e = e + 4 * x + 6
        x += 1
        add_symmetric_points(xc, yc, x, y)

    elapsed_time = (time.perf_counter() - start_time) * 1000
    return [(px, py, 1.0) for px, py in pixels], elapsed_time


def wu_line(x0, y0, x1, y1):
    """Алгоритм Ву для рисования сглаженных отрезков"""
    start_time = time.perf_counter()
    intensity_map = {}

    def fpart(val):
        return val - math.floor(val)

    def rfpart(val):
        return 1.0 - fpart(val)

    def plot(px, py, c):
        if c <= 0.0:
            return
        key = (int(px), int(py))
        prev = intensity_map.get(key, 0.0)
        intensity_map[key] = max(prev, min(1.0, c))

    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1.0

    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = rfpart(x0 + 0.5)
    xpxl1 = int(xend)
    ypxl1 = math.floor(yend)

    if steep:
        plot(ypxl1, xpxl1, rfpart(yend) * xgap)
        plot(ypxl1 + 1, xpxl1, fpart(yend) * xgap)
    else:
        plot(xpxl1, ypxl1, rfpart(yend) * xgap)
        plot(xpxl1, ypxl1 + 1, fpart(yend) * xgap)

    intery = yend + gradient

    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = fpart(x1 + 0.5)
    xpxl2 = int(xend)
    ypxl2 = math.floor(yend)

    if steep:
        plot(ypxl2, xpxl2, rfpart(yend) * xgap)
        plot(ypxl2 + 1, xpxl2, fpart(yend) * xgap)
    else:
        plot(xpxl2, ypxl2, rfpart(yend) * xgap)
        plot(xpxl2, ypxl2 + 1, fpart(yend) * xgap)

    for x in range(xpxl1 + 1, xpxl2):
        floor_y = math.floor(intery)
        if steep:
            plot(floor_y, x, rfpart(intery))
            plot(floor_y + 1, x, fpart(intery))
        else:
            plot(x, floor_y, rfpart(intery))
            plot(x, floor_y + 1, fpart(intery))
        intery += gradient

    elapsed_time = (time.perf_counter() - start_time) * 1000
    pixels = [(px, py, val) for (px, py), val in intensity_map.items()]
    return pixels, elapsed_time