#------------------- ПРИКЛАД - корегування кольору -------------

'''
Package                      Version
---------------------------- -----------
pip                          23.1
opencv-python                3.4.18.65
numpy                        1.23.5
Pillow                       9.4.0
matplotlib                   3.6.2

'''

import cv2
import numpy as np
from matplotlib import pyplot as plt

#----------------- 1 Гистограма  яскравості зображення ---------
img = cv2.imread('sentinel_2023.jpg')
imS = cv2.resize(img, (600, 500))
cv2.imshow("img", imS)
plt.hist(img.ravel(), 256, [0, 256])
plt.show()
cv2.waitKey(0)
cv2.destroyAllWindows()

#-------------------- 2 Маскування зображення  -----------------
mask = np.zeros(img.shape[:2], np.uint8)
mask[350:550, 300:700] = 255
masked_img = cv2.bitwise_and(img, img, mask=mask)

hist_full = cv2.calcHist([img], [0], None, [256], [0,256])
hist_mask = cv2.calcHist([img], [0], mask, [256], [0, 256])

plt.subplot(221), plt.imshow(img, 'gray')
plt.subplot(222), plt.imshow(mask,'gray')
plt.subplot(223), plt.imshow(masked_img, 'gray')
plt.subplot(224), plt.plot(hist_full), plt.plot(hist_mask)
plt.xlim([0,256])
plt.show()

#-------------------- 3 Вирівнювання гістограми  --------------
img = cv2.imread('sentinel_2023.jpg', 0)
hist, bins = np.histogram(img.flatten(),256,[0,256])
cdf = hist.cumsum()
cdf_normalized = cdf * hist.max() / cdf.max()        # Визначення нормалізоуючої кривої
plt.plot(cdf_normalized, color = 'b')
plt.hist(img.flatten(),256,[0,256], color = 'r')
plt.xlim([0,256])
plt.legend(('cdf','histogram'), loc = 'upper left')
plt.show()

cdf_m = np.ma.masked_equal(cdf,0)
cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())

cdf = np.ma.filled(cdf_m,0).astype('uint8')
img2 = cdf[img]

img = cv2.imread('sentinel_2023.jpg', 0)
equ = cv2.equalizeHist(img)
res = np.hstack((img,equ))
cv2.imwrite('sentinel_2023_Rez_equalizeHist.jpg',res)

imS = cv2.resize(res, (800, 300))
plt.imshow(imS)
plt.show()

