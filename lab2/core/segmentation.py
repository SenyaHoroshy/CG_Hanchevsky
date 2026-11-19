import cv2
import numpy as np

def detect_points(image: np.ndarray) -> np.ndarray:
    """Обнаружение точек с помощью маски Лапласиана (плавные оттенки серого)."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    kernel = np.array([[1, 1, 1],
                       [1, -8, 1],
                       [1, 1, 1]], dtype=np.float32)
    filtered = cv2.filter2D(gray.astype(np.float32), -1, kernel)
    result = np.abs(filtered)
    return cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def detect_lines(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
    """Обнаружение линий по заданному направлению"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    kernels = {
        'horizontal': np.array([[-1, -1, -1],
                                 [2, 2, 2],
                                 [-1, -1, -1]], dtype=np.float32),
        'vertical': np.array([[-1, 2, -1],
                               [-1, 2, -1],
                               [-1, 2, -1]], dtype=np.float32),
        'diag_45': np.array([[-1, -1, 2],
                              [-1, 2, -1],
                              [2, -1, -1]], dtype=np.float32),
        'diag_135': np.array([[2, -1, -1],
                               [-1, 2, -1],
                               [-1, -1, 2]], dtype=np.float32)
    }
    
    kernel = kernels.get(direction, kernels['horizontal'])
    filtered = cv2.filter2D(gray.astype(np.float32), -1, kernel)
    result = np.clip(filtered, 0, 255).astype(np.uint8)
    return cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def detect_edges(image: np.ndarray) -> np.ndarray:
    """Обнаружение перепадов яркости с помощью оператора Собеля (плавные оттенки серого)."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    
    magnitude = cv2.magnitude(grad_x, grad_y)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def colorize_segments(image_result: np.ndarray) -> np.ndarray:
    if len(image_result.shape) == 3:
        gray = cv2.cvtColor(image_result, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_result.copy()
        
    if np.max(gray) == np.min(gray):
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
    # Глобальная пороговая обработка методом Отсу для получения сплошных зон
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Проверка углов для гарантии того, что фон — черный (0), а объекты — белые (255)
    h, w = thresh.shape
    corner_pixels = [thresh[0, 0], thresh[0, w-1], thresh[h-1, 0], thresh[h-1, w-1]]
    if np.mean(corner_pixels) > 127:
        thresh = cv2.bitwise_not(thresh)
        
    # Минимальное удаление пиксельного мусора (MORPH_OPEN), 
    # которое НЕ склеивает соседние объекты и оставляет черные зазоры нетронутыми.
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Поиск связных компонент по чистым сплошным объектам
    num_labels, labels = cv2.connectedComponents(cleaned)
    
    # Генерация яркой палитры (фон строго черный, объекты — цветные)
    np.random.seed(42)
    colors = np.random.randint(50, 255, size=(num_labels, 3), dtype=np.uint8)
    if num_labels > 0:
        colors[0] = [0, 0, 0]
        
    colored = colors[labels]
    return colored