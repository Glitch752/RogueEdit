import math

def exp_decay(a: float, b: float, decay: float, dt: float) -> float:
    """
    lmao https://www.youtube.com/watch?v=LSNQuFEDOyQ
    Useful range approximation of decay: 1 to 25, slow to fast
    """
    return b+(a-b)*math.exp(-decay*dt)

def clamp(a: float, minv: float, maxv: float) -> float:
    return min(max(minv, a), maxv)

def format_seconds(duration: float, short: bool = False) -> str:
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    milliseconds = int((duration - int(duration)) * 1000)
    if short:
        return f"{seconds}.{int(milliseconds // 10):02}"
    return f"{minutes:02}:{seconds:02}.{milliseconds:03}"