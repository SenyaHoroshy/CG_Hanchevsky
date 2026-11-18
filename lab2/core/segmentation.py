import cv2
import numpy as np

def detect_points(image: np.ndarray) -> np.ndarray:
    """Обнаружение точек с помощью маски Лапласиана."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    # Маска Лапласиана для точек
    kernel = np.array([[1, 1, 1],
                       [1, -8, 1],
                       [1, 1, 1]], dtype=np.float32)
    filtered = cv2.filter2D(gray.astype(np.float32), -1, kernel)
    # Пороговая обработка для выделения изолированных точек
    result = np.abs(filtered)
    result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return result

def detect_lines(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
    """Обнаружение линий по заданному направлению."""
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
    return result

def detect_edges(image: np.ndarray) -> np.ndarray:
    """Обнаружение перепадов яркости (границ) с помощью оператора Собеля."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    
    # Амплитуда градиента G(x, y) = max(|G_x|, |G_y|) или евклидова норма
    magnitude = cv2.magnitude(grad_x, grad_y)
    result = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return result