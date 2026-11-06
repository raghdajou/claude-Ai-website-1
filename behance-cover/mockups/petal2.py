# Petal masks for the wedding-style scene: GrabCut inside a box around each of the four petals.
import numpy as np, cv2
from PIL import Image
im = cv2.imread('../../images/152.webp'); H, W = im.shape[:2]
BOXES = [(1585, 195, 1808, 422), (238, 532, 437, 768), (58, 1006, 482, 1284), (1538, 982, 1888, 1342)]
pet = np.zeros((H, W), np.uint8)
for (l, t, r, b) in BOXES:
    m = 12; L, T, R, B = max(l - m, 0), max(t - m, 0), min(r + m, W), min(b + m, H)
    crop = im[T:B, L:R].copy(); mask = np.zeros(crop.shape[:2], np.uint8)
    bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
    cv2.grabCut(crop, mask, (l - L, t - T, r - l, b - t), bg, fg, 8, cv2.GC_INIT_WITH_RECT)
    pet[T:B, L:R] |= np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
cv2.imwrite('petal_mask.png', pet)
vis = im.astype(float); sel = pet > 0; vis[sel] = vis[sel] * 0.4 + np.array([0, 0, 255]) * 0.6
cv2.imwrite('petal_vis.png', cv2.resize(vis.astype(np.uint8), (1000, 750)))
