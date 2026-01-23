import cv2
import numpy as np
import matplotlib.pyplot as plt


def detect_white_airplanes(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    result = img.copy()

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 180])  # Низкая насыщенность, высокая яркость
    upper_white = np.array([180, 60, 255])  # Весь диапазон оттенков

    mask = cv2.inRange(hsv, lower_white, upper_white)

    kernel_small = np.ones((3, 3), np.uint8)
    kernel_medium = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_small, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_medium, iterations=3)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    contour_data = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        cx = x + w // 2
        cy = y + h // 2
        contour_data.append({
            'contour': contour,
            'x': x, 'y': y, 'w': w, 'h': h,
            'cx': cx, 'cy': cy,
            'area': area,
            'merged': False
        })

    airplane_groups = []
    merge_distance = 40

    for i, data in enumerate(contour_data):
        if data['merged']:
            continue

        group = [i]
        data['merged'] = True

        for j, other in enumerate(contour_data):
            if i == j or other['merged']:
                continue

            distance = np.sqrt((data['cx'] - other['cx']) ** 2 +
                               (data['cy'] - other['cy']) ** 2)

            if distance < merge_distance:
                group.append(j)
                other['merged'] = True

        airplane_groups.append(group)

    airplane_count = len(airplane_groups)
    detected_planes = []


    for plane_num, group in enumerate(airplane_groups, 1):
        group_contours = [contour_data[idx]['contour'] for idx in group]

        all_points = np.vstack(group_contours)
        x, y, w, h = cv2.boundingRect(all_points)

        total_area = sum(contour_data[idx]['area'] for idx in group)

        detected_planes.append((x, y, w, h, total_area))


        for idx in group:
            cv2.drawContours(result, [contour_data[idx]['contour']],
                             -1, (0, 255, 0), 3)

        cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 3)

        cv2.putText(result, str(plane_num),
                    (x + 5, y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    (0, 0, 255), 3)

        cv2.putText(result, f'{int(total_area)}px',
                    (x + 5, y + h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 0), 2)

    return airplane_count, result, mask, detected_planes


def visualize_detection(image_path):
    original = cv2.imread(image_path)
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)

    count, result, mask, planes = detect_white_airplanes(image_path)
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    axes[0].imshow(original_rgb)
    axes[0].set_title('Исходное изображение', fontsize=14)
    axes[0].axis('off')

    axes[1].imshow(mask, cmap='gray')
    axes[1].set_title('Маска белых объектов', fontsize=14)
    axes[1].axis('off')

    axes[2].imshow(result_rgb)
    axes[2].set_title(f'Обнаружено самолетов: {count}', fontsize=14, fontweight='bold')
    axes[2].axis('off')

    plt.tight_layout()
    plt.savefig('airplane_detection_result.png', dpi=150, bbox_inches='tight')
    plt.show()


    return count, result


def tune_parameters(image_path):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    cv2.namedWindow('Tuning')

    def nothing(x):
        pass

    cv2.createTrackbar('H_min', 'Tuning', 0, 180, nothing)
    cv2.createTrackbar('H_max', 'Tuning', 180, 180, nothing)
    cv2.createTrackbar('S_min', 'Tuning', 0, 255, nothing)
    cv2.createTrackbar('S_max', 'Tuning', 60, 255, nothing)
    cv2.createTrackbar('V_min', 'Tuning', 180, 255, nothing)
    cv2.createTrackbar('V_max', 'Tuning', 255, 255, nothing)

    cv2.createTrackbar('Min_Area', 'Tuning', 400, 5000, nothing)
    cv2.createTrackbar('Max_Area', 'Tuning', 20000, 50000, nothing)

    while True:
        h_min = cv2.getTrackbarPos('H_min', 'Tuning')
        h_max = cv2.getTrackbarPos('H_max', 'Tuning')
        s_min = cv2.getTrackbarPos('S_min', 'Tuning')
        s_max = cv2.getTrackbarPos('S_max', 'Tuning')
        v_min = cv2.getTrackbarPos('V_min', 'Tuning')
        v_max = cv2.getTrackbarPos('V_max', 'Tuning')

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)

        result = cv2.bitwise_and(img, img, mask=mask)

        cv2.imshow('Tuning', np.hstack([img, result]))

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break


    cv2.destroyAllWindows()


if __name__ == "__main__":
    image_path = "plane2.jpg"

    try:
        count, result = visualize_detection(image_path)

        cv2.imwrite("detected_airplanes.jpg", result)


    except Exception as e:
        print(f": {e}")