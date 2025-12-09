import cv2
import matplotlib.pyplot as plt

img = cv2.imread('tennis.png')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(gray, (5, 5), 0)

edges = cv2.Canny(blurred, 50, 150) 
plt.figure(figsize=(10, 5))
plt.subplot(1, 3, 1); plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)); plt.title('Original')
plt.subplot(1, 3, 2); plt.imshow(gray, cmap='gray'); plt.title('Grayscale')
plt.subplot(1, 3, 3); plt.imshow(edges, cmap='gray'); plt.title('Canny Edges')
plt.show()

contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f'{len(contours)} контурів') 