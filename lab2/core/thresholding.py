import cv2
import numpy as np

def global_threshold_otsu(image: np.ndarray) -> tuple[np.ndarray, float]:
    """Глобальная пороговая обработка методом Отсу."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary, float(thresh_val)

def global_threshold_entropy(image: np.ndarray) -> tuple[np.ndarray, float]:
    """Глобальная пороговая обработка на основе энтропии гистограммы (метод Капура)."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    hist = hist.astype(np.float32)
    total_pixels = gray.size
    p = hist / total_pixels
    
    P = np.cumsum(p)
    max_entropy = -1.0
    optimal_t = 0
    eps = 1e-10
    
    for t in range(1, 255):
        p1 = P[t]
        p2 = 1.0 - p1
        
        if p1 < eps or p2 < eps:
            continue
            
        h1 = 0.0
        for i in range(0, t + 1):
            if p[i] > eps:
                val = p[i] / p1
                h1 -= val * np.log(val)
                
        h2 = 0.0
        for i in range(t + 1, 256):
            if p[i] > eps:
                val = p[i] / p2
                h2 -= val * np.log(val)
                
        total_entropy = h1 + h2
        
        if total_entropy > max_entropy:
            max_entropy = total_entropy
            optimal_t = t
            
    binary = np.where(gray > optimal_t, 255, 0).astype(np.uint8)
    return binary, float(optimal_t)