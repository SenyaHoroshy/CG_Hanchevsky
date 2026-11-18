import cv2
import numpy as np

def global_threshold_otsu(image: np.ndarray) -> tuple[np.ndarray, float]:
    """Глобальная пороговая обработка методом Отсу."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    # Вычисление порога методом Отсу из OpenCV
    thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary, float(thresh_val)

def global_threshold_iterative(image: np.ndarray, tolerance: float = 0.5, max_iter: int = 50) -> tuple[np.ndarray, float]:
    """
    Глобальная пороговая обработка итеративным методом по гистограмме (из лекции):
    1. Выбрать начальную оценку t (например, средняя яркость).
    2. Разделить изображение на две группы G1 (> t) и G2 (<= t).
    3. Вычислить новые средние значения m1 и m2 для этих групп.
    4. Вычислить новый порог t = (m1 + m2) / 2.
    5. Повторять до тех пор, пока разница порогов меньше tolerance.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    # Начальный порог — среднее значение яркости по изображению
    t = float(np.mean(gray))
    
    for _ in range(max_iter):
        mask1 = gray > t
        mask2 = gray <= t
        
        m1 = np.mean(gray[mask1]) if np.any(mask1) else 0.0
        m2 = np.mean(gray[mask2]) if np.any(mask2) else 0.0
        
        new_t = (m1 + m2) / 2.0
        
        if abs(new_t - t) < tolerance:
            t = new_t
            break
        t = new_t
        
    # Применение найденного порога
    binary = np.where(gray > t, 255, 0).astype(np.uint8)
    return binary, float(t)