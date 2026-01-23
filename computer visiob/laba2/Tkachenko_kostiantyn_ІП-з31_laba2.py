import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, label, binary_erosion, binary_dilation, binary_fill_holes
from scipy.ndimage import distance_transform_edt
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
import warnings

warnings.simplefilter("ignore", category=RuntimeWarning)

def rgb_to_hsv(rgb):
    rgb = rgb / 255.0 if rgb.max() > 1 else rgb
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    max_c = np.max(rgb, axis=-1)
    min_c = np.min(rgb, axis=-1)
    delta = max_c - min_c

    h = np.zeros_like(max_c)
    s = np.zeros_like(max_c)
    v = max_c

    mask = delta > 1e-8
    idx = (r == max_c) & mask
    h[idx] = ((g - b) / delta)[idx] % 6
    idx = (g == max_c) & mask
    h[idx] = ((b - r) / delta + 2)[idx]
    idx = (b == max_c) & mask
    h[idx] = ((r - g) / delta + 4)[idx]
    h = h / 6.0
    s[mask] = delta[mask] / max_c[mask]

    h = h * 360
    s = s * 100
    v = v * 100
    return np.stack([h, s, v], axis=-1)

def apply_color_correction(image, method='hsv'):
    if method == 'grayscale':
        gray = np.dot(image[..., :3], [0.299, 0.587, 0.114])
        return np.stack([gray, gray, gray], axis=-1)
    elif method == 'sepia':
        sepia_filter = np.array([[0.393, 0.769, 0.189],
                                 [0.349, 0.686, 0.168],
                                 [0.272, 0.534, 0.131]])
        sepia = image @ sepia_filter.T
        return np.clip(sepia, 0, 1)
    elif method == 'negative':
        return 1.0 - image if image.max() <= 1 else 255 - image
    else:
        return image

def create_tomato_mask(image, hsv_params='auto'):
    hsv = rgb_to_hsv(image)
    if hsv_params == 'strict':
        lower_red1 = np.array([0, 40, 40])
        upper_red1 = np.array([15, 100, 100])
        lower_red2 = np.array([345, 40, 40])
        upper_red2 = np.array([360, 100, 100])
    elif hsv_params == 'relaxed':
        lower_red1 = np.array([0, 20, 20])
        upper_red1 = np.array([25, 100, 100])
        lower_red2 = np.array([335, 20, 20])
        upper_red2 = np.array([360, 100, 100])
    else:
        avg_brightness = np.mean(image)
        if avg_brightness > 0.7:
            lower_red1 = np.array([0, 35, 35])
            upper_red1 = np.array([18, 100, 100])
            lower_red2 = np.array([342, 35, 35])
            upper_red2 = np.array([360, 100, 100])
        else:
            lower_red1 = np.array([0, 30, 30])
            upper_red1 = np.array([20, 100, 100])
            lower_red2 = np.array([340, 30, 30])
            upper_red2 = np.array([360, 100, 100])
    mask1 = (hsv[..., 0] >= lower_red1[0]) & (hsv[..., 0] <= upper_red1[0]) & \
            (hsv[..., 1] >= lower_red1[1]) & (hsv[..., 1] <= upper_red1[1]) & \
            (hsv[..., 2] >= lower_red1[2]) & (hsv[..., 2] <= upper_red1[2])
    mask2 = (hsv[..., 0] >= lower_red2[0]) & (hsv[..., 0] <= upper_red2[0]) & \
            (hsv[..., 1] >= lower_red2[1]) & (hsv[..., 1] <= upper_red2[1]) & \
            (hsv[..., 2] >= lower_red2[2]) & (hsv[..., 2] <= upper_red2[2])
    mask = mask1 | mask2
    return mask.astype(np.uint8)

def apply_vectorization(mask, method='watershed', min_distance=30):
    if method == 'watershed':
        distance = distance_transform_edt(mask)
        distance_smooth = gaussian_filter(distance, sigma=2)
        threshold_abs = distance_smooth.max() * 0.4
        local_max = peak_local_max(
            distance_smooth,
            min_distance=min_distance,
            threshold_abs=threshold_abs,
            labels=mask,
            exclude_border=False
        )
        markers = np.zeros_like(mask, dtype=int)
        for idx, (y, x) in enumerate(local_max, start=1):
            markers[y, x] = idx
        for idx in range(1, len(local_max) + 1):
            marker_mask = (markers == idx)
            dilated = binary_dilation(marker_mask, iterations=2)
            markers[dilated & (markers == 0)] = idx
        labels = watershed(-distance, markers, mask=mask)
        return labels, len(local_max)
    elif method == 'contours':
        labeled, num = label(mask)
        return labeled, num
    else:
        from scipy.ndimage import sobel
        sx = sobel(mask.astype(float), axis=0)
        sy = sobel(mask.astype(float), axis=1)
        edges = np.hypot(sx, sy)
        return (edges > edges.mean()).astype(int), 1

def count_tomatoes(image_path, hsv_params='auto', min_size=200,
                   max_size=50000, show_steps=True, vectorization_method='watershed',
                   min_distance=25, erosion_iterations=1):
    image = plt.imread(image_path)
    if image.ndim == 3 and image.shape[2] == 4:
        image = image[..., :3]
    if image.max() > 1:
        image = image / 255.0
    corrected = apply_color_correction(image, method='hsv')
    mask = create_tomato_mask(corrected, hsv_params=hsv_params)
    blurred = gaussian_filter(mask.astype(float), sigma=1.5)
    mask_smooth = (blurred > 0.5).astype(np.uint8)
    eroded = binary_erosion(mask_smooth, iterations=erosion_iterations)
    dilated = binary_dilation(eroded, iterations=erosion_iterations + 1)
    filled = binary_fill_holes(dilated)
    if vectorization_method == 'watershed':
        labeled, num_initial = apply_vectorization(filled, method='watershed',
                                                   min_distance=min_distance)
    else:
        labeled, num_initial = apply_vectorization(filled, method=vectorization_method)
    sizes = np.bincount(labeled.ravel())
    valid_labels = np.where((sizes > min_size) & (sizes < max_size))[0]
    valid_labels = valid_labels[valid_labels > 0]
    filtered_mask = np.isin(labeled, valid_labels)
    final_labeled, num_tomatoes = label(filtered_mask)
    if num_tomatoes > 0:
        final_sizes = np.bincount(final_labeled.ravel())[1:]
        mean_size = np.mean(final_sizes)
        std_size = np.std(final_sizes)
    else:
        mean_size = 0
        std_size = 0
    if show_steps:
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes[0, 0].imshow(image)
        axes[0, 0].axis('off')
        axes[0, 1].imshow(mask, cmap='gray')
        axes[0, 1].axis('off')
        axes[0, 2].imshow(filled, cmap='gray')
        axes[0, 2].axis('off')
        if vectorization_method == 'watershed':
            distance = distance_transform_edt(filled)
            axes[1, 0].imshow(distance, cmap='jet')
        else:
            axes[1, 0].imshow(labeled, cmap='nipy_spectral')
        axes[1, 0].axis('off')
        axes[1, 1].imshow(labeled, cmap='nipy_spectral')
        axes[1, 1].axis('off')
        result = image.copy()
        colors = plt.cm.rainbow(np.linspace(0, 1, num_tomatoes))
        for i in range(1, num_tomatoes + 1):
            mask_i = (final_labeled == i)
            y_coords, x_coords = np.where(mask_i)
            if len(y_coords) > 0:
                cy, cx = int(np.mean(y_coords)), int(np.mean(x_coords))
                result[mask_i] = result[mask_i] * 0.5 + colors[i - 1][:3] * 0.5
                axes[1, 2].text(cx, cy, str(i), color='white',
                                fontsize=20, weight='bold',
                                ha='center', va='center',
                                bbox=dict(boxstyle='circle', facecolor=colors[i - 1], alpha=0.8))
        axes[1, 2].imshow(result)
        axes[1, 2].axis('off')
        plt.tight_layout()
        plt.show()
    return num_tomatoes, mean_size, std_size, final_labeled, image

def compare_images(image_path1, image_path2):
    num1, mean1, std1, _, _ = count_tomatoes(image_path1, show_steps=False)
    num2, mean2, std2, _, _ = count_tomatoes(image_path2, show_steps=False)
    count_similarity = 1 - abs(num1 - num2) / max(num1, num2, 1)
    size_similarity = 1 - abs(mean1 - mean2) / max(mean1, mean2, 1)
    overall_similarity = (count_similarity * 0.6 + size_similarity * 0.4)
    return overall_similarity

if __name__ == "__main__":
    image_path = "tomato.jpg"
    num1, mean_size, std_size, labeled, img = count_tomatoes(
        image_path,
        hsv_params='auto',
        min_size=300,
        max_size=50000,
        show_steps=True,
        vectorization_method='watershed',
        min_distance=25,
        erosion_iterations=3
    )
    if num1 == 1:
        num2, mean_size2, std_size2, labeled2, img2 = count_tomatoes(
            image_path,
            hsv_params='auto',
            min_size=200,
            max_size=50000,
            show_steps=True,
            vectorization_method='watershed',
            min_distance=20,
            erosion_iterations=4
        )