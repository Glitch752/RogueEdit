import math

def exp_decay(a: float, b: float, decay: float, dt: float) -> float:
    """
    lmao https://www.youtube.com/watch?v=LSNQuFEDOyQ
    Useful range approximation of decay: 1 to 25, slow to fast
    """
    return b+(a-b)*math.exp(-decay*dt)

def clamp(a: float, minv: float, maxv: float) -> float:
    return min(max(minv, a), maxv)