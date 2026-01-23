#------------------- ПРИКЛАД - фільтрація зображень в opencv ------

'''
Цифрова обробка зображень: фільтрація

Package                      Version
---------------------------- -----------
opencv-python                3.4.18.65
numpy                        1.23.5
pip                          23.1
Pillow                       9.4.0
matplotlib                   3.6.2

'''

import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageEnhance

#----------------- 1: Усереднення зображення через згортку ---------
img = cv2.imread('sentinel_2023.jpg')
kernel = np.ones((5,5),np.float32)/25
#------------------ виклик методу 2D Convolution ------------------
blur1 = cv2.filter2D(img,-1,kernel)
#-------------- відображення результату ----------------------------
plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(blur1),plt.title('Averaging')
plt.xticks([]), plt.yticks([])
plt.show()
cv2.imwrite('sentinel_2023_filter2D.jpg',blur1)


#---------------- 2: Розмиття через згладжування ------------------
img = cv2.imread('sentinel_2023.jpg')
#------------------- виклик методу - blur --------------------------
blur2 = cv2.blur(img,(5,5))
#------------------- відображення результату -----------------------
plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(blur2),plt.title('Blurred')
plt.xticks([]), plt.yticks([])
plt.show()
cv2.imwrite('sentinel_2023_blur.jpg',blur2)


#-------------------- 3: Гауссова фільтрація  -----------------------
img = cv2.imread('sentinel_2023.jpg')
#------------------- виклик методу - GaussianBlur ------------------
blur3 = cv2.GaussianBlur(img,(5,5),0)
#------------------- відображення результату -----------------------
plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(blur3),plt.title('GaussianBlur')
plt.xticks([]), plt.yticks([])
plt.show()
cv2.imwrite('sentinel_2023_GaussianBlur.jpg',blur3)


#-------------------- 4: Медіанний фільтр  -------------------------
img = cv2.imread('sentinel_2023.jpg')
#------------------- виклик методу -blur ---------------------------
blur4 = cv2.medianBlur(img,5)
#------------------- відображення результату -----------------------
plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(blur4),plt.title('Median Filtering')
plt.xticks([]), plt.yticks([])
plt.show()
cv2.imwrite('sentinel_2023_medianBlur.jpg',blur4)


#------------------- 5: Двостороння фільтрація ---------------------
img = cv2.imread('sentinel_2023.jpg')
#------------------- виклик методу -blur ---------------------------
blur5 = cv2.bilateralFilter(img,9,75,75)
#------------------- відображення результату -----------------------
plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(blur5),plt.title('Bilateral Filtering')
plt.xticks([]), plt.yticks([])
plt.show()
cv2.imwrite('sentinel_2023_bilateralFilter.jpg',blur5)


#----------------- 6: підвищення чіткості зображення -------------------
im = Image.open("sentinel_2023.jpg")
enhancer = ImageEnhance.Sharpness(im)
factor = 1
im_s_1 = enhancer.enhance(factor)
im_s_1.save('sentinel_2023_ImageEnhance_1.jpg')
factor = 0.05
im_s_1 = enhancer.enhance(factor)
im_s_1.save('sentinel_2023_ImageEnhance_2.jpg')
factor = 2
im_s_1 = enhancer.enhance(factor)
im_s_1.save('sentinel_2023_ImageEnhance_3.jpg')