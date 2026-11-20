import numpy as np
from typing import Tuple, List

def estimate_motion_phase_correlation(frame1: np.ndarray, frame2: np.ndarray) -> Tuple[float,float]:
    """
    Estimate motion vector between two frames using phase correlation (FFT).
    Works on 2D arrays.
    """
    # Ensure float
    f1 = frame1.astype(np.float32)
    f2 = frame2.astype(np.float32)
    # FFT
    F1 = np.fft.fft2(f1)
    F2 = np.fft.fft2(f2)
    # Cross-power spectrum
    eps = 1e-8
    R = F1 * np.conj(F2)
    R /= (np.abs(R) + eps)
    # inverse FFT -> correlation surface
    corr = np.fft.ifft2(R).real
    # find peak
    max_idx = np.unravel_index(np.argmax(corr), corr.shape)
    # Convert to shift
    shifts = np.array(max_idx, dtype=float)
    # Wrap-around correction: if shift > N/2, it's negative
    for i in range(len(shifts)):
        if shifts[i] > corr.shape[i] // 2:
            shifts[i] -= corr.shape[i]
    # motion vector is negative of shift? phase correlation gives shift that aligns f2 to f1.
    # So vector to warp frame1 towards frame2 is -shifts
    vy, vx = -shifts[0], -shifts[1]
    return float(vx), float(vy)

def estimate_motion_block_matching(frame1: np.ndarray, frame2: np.ndarray, block_size=8, search_range=4) -> Tuple[float,float]:
    """
    Fallback block matching averaging motion vectors.
    """
    h, w = frame1.shape
    vectors = []
    for y in range(0, h-block_size, block_size*2):
        for x in range(0, w-block_size, block_size*2):
            block = frame1[y:y+block_size, x:x+block_size]
            best_err = float('inf')
            best_dx, best_dy = 0,0
            for dy in range(-search_range, search_range+1):
                for dx in range(-search_range, search_range+1):
                    yy = y+dy
                    xx = x+dx
                    if yy<0 or yy+block_size>h or xx<0 or xx+block_size>w:
                        continue
                    cand = frame2[yy:yy+block_size, xx:xx+block_size]
                    err = np.mean((block-cand)**2)
                    if err < best_err:
                        best_err = err
                        best_dx, best_dy = dx, dy
            vectors.append((best_dx, best_dy))
    if not vectors:
        return 0.0, 0.0
    avg = np.mean(vectors, axis=0)
    return float(avg[0]), float(avg[1])

def estimate_motion(frame1: np.ndarray, frame2: np.ndarray) -> Tuple[float,float]:
    try:
        return estimate_motion_phase_correlation(frame1, frame2)
    except Exception as e:
        return estimate_motion_block_matching(frame1, frame2)

def advect_frame(frame: np.ndarray, vector: Tuple[float,float], steps: int) -> List[np.ndarray]:
    from scipy.ndimage import shift
    frames = []
    cur = frame.copy()
    vx, vy = vector
    for _ in range(steps):
        cur = shift(cur, shift=(vy, vx), mode='wrap', order=1)
        frames.append(cur.copy())
    return frames
