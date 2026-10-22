def rgb_to_cmyk(r, g, b):
    # RGB -> CMYK
    rf = r / 255.0
    gf = g / 255.0
    bf = b / 255.0
    
    K = min(1.0 - rf, 1.0 - gf, 1.0 - bf)
    if K >= 1.0:
        return 0.0, 0.0, 0.0, 1.0
        
    C = (1.0 - rf - K) / (1.0 - K)
    M = (1.0 - gf - K) / (1.0 - K)
    Y = (1.0 - bf - K) / (1.0 - K)
    return float(C), float(M), float(Y), float(K)

def cmyk_to_rgb(C, M, Y, K):
    # CMYK -> RGB
    r = round(255 * (1.0 - C) * (1.0 - K))
    g = round(255 * (1.0 - M) * (1.0 - K))
    b = round(255 * (1.0 - Y) * (1.0 - K))
    return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

def rgb_to_hsv(r, g, b):
    # RGB -> HSV
    R = r / 255.0
    G = g / 255.0
    B = b / 255.0
    
    MAX = max(R, G, B)
    MIN = min(R, G, B)
    V = MAX
    
    if MAX == 0:
        S = 0.0
    else:
        S = (MAX - MIN) / MAX
        
    if MAX == MIN:
        H = 0.0
    else:
        delta = MAX - MIN
        if MAX == R:
            H = 60.0 * ((G - B) / delta)
            if G < B:
                H += 360.0
        elif MAX == G:
            H = 60.0 * ((B - R) / delta) + 120.0
        else:
            H = 60.0 * ((R - G) / delta) + 240.0
            
    return float(H), float(S), float(V)

def hsv_to_rgb(H, S, V):
    # HSV -> RGB
    if S == 0:
        r = round(V * 255)
        g = round(V * 255)
        b = round(V * 255)
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        
    if H == 360:
        H = 0
        
    H = H / 60.0
    I = int(H)
    F = H - I
    
    M = V * (1.0 - S)
    N = V * (1.0 - S * F)
    K = V * (1.0 - S * (1.0 - F))
    
    if I == 0:
        rf, gf, bf = V, K, M
    elif I == 1:
        rf, gf, bf = N, V, M
    elif I == 2:
        rf, gf, bf = M, V, K
    elif I == 3:
        rf, gf, bf = M, N, V
    elif I == 4:
        rf, gf, bf = K, M, V
    else:
        rf, gf, bf = V, M, N
        
    r = round(rf * 255)
    g = round(gf * 255)
    b = round(bf * 255)
    return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

def rgb_to_hls(r, g, b):
    # RGB -> HLS
    R = r / 255.0
    G = g / 255.0
    B = b / 255.0
    
    MAX = max(R, G, B)
    MIN = min(R, G, B)
    L = (MAX + MIN) / 2.0
    
    if MAX == MIN:
        H = 0.0
        S = 0.0
    else:
        delta = MAX - MIN
        if L <= 0.5:
            S = delta / (MAX + MIN)
        else:
            S = delta / (2.0 - MAX - MIN)
            
        if MAX == R:
            H = 60.0 * ((G - B) / delta)
            if G < B:
                H += 360.0
        elif MAX == G:
            H = 60.0 * ((B - R) / delta) + 120.0
        else:
            H = 60.0 * ((R - G) / delta) + 240.0
            
    return float(H), float(L), float(S)

def hls_to_rgb(H, L, S):
    # HLS -> RGB
    if S == 0:
        r = round(L * 255)
        g = round(L * 255)
        b = round(L * 255)
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        
    if L < 0.5:
        M2 = L * (1.0 + S)
    else:
        M2 = L + S - L * S
        
    M1 = 2.0 * L - M2
    
    def value_func(hue, m1, m2):
        if hue < 0:
            hue += 360.0
        if hue > 360:
            hue -= 360.0
        if hue < 60:
            return m1 + (m2 - m1) * hue / 60.0
        if hue < 180:
            return m2
        if hue < 240:
            return m1 + (m2 - m1) * (240.0 - hue) / 60.0
        return m1
        
    rf = value_func(H + 120.0, M1, M2)
    gf = value_func(H, M1, M2)
    bf = value_func(H - 120.0, M1, M2)
    
    r = round(rf * 255)
    g = round(gf * 255)
    b = round(bf * 255)
    return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))