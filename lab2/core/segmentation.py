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
    # Возвращаем нормализованные плавные переходы (оттенки серого)
    return cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def detect_lines(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
    """Обнаружение линий по заданному направлению (плавные оттенки серого)."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    kernels = {
        'horizontal': np.array([[-1, -1, -1],
                                 [ 2,  2,  2],
                                 [-1, -1, -1]], dtype=np.float32),
        'vertical': np.array([[-1,  2, -1],
                               [-1,  2, -1],
                               [-1,  2, -1]], dtype=np.float32),
        'diag_43': np.array([[ 2, -1, -1],
                              [-1,  2, -1],
                              [-1, -1,  2]], dtype=np.float32),
        'diag_135': np.array([[-1, -1,  2],
                               [-1,  2, -1],
                               [ 2, -1, -1]], dtype=np.float32)
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
    """
    Создает цветную карту сегментов для третьей панели.
    Выполняет пороговую обработку локально только для построения регионов, 
    не затрагивая основную картинку результата.
    """
    if len(image_result.shape) == 3:
        gray = cv2.cvtColor(image_result, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_result.copy()
        
    # Локальный порог для выделения значимых контуров/объектов в цветную карту
    _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
    
    num_labels, labels = cv2.connectedComponents(thresh)
    
    np.random.seed(42)
    colors = np.random.randint(50, 240, size=(num_labels, 3), dtype=np.uint8)
    if num_labels > 0:
        colors[0] = [255, 255, 255]  # Фон остается белым
        
    colored = colors[labels]
    return colored