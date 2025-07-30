import numpy as np
import cv2

def get_affine_matrix(W_src, H_src, W_out, H_out, scale, angle_deg, dx, dy):
    cx, cy = (W_src / 2, H_src / 2)
    T1 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]])
    S = np.array([[scale, 0, 0], [0, scale, 0], [0, 0, 1]])
    theta = np.deg2rad(angle_deg)
    R = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])
    T2 = np.array([[1, 0, W_out / 2 + dx], [0, 1, H_out / 2 + dy], [0, 0, 1]])
    M = T2 @ R @ S @ T1
    return M[:2]

def direction_vector():
    dx = 0
    dy = 0
    dz = -1

    norm = np.linalg.norm([dx, dy, dz])
    if norm == 0:
        return 0, 0, 0
    return dx / norm, dy / norm, dz / norm

def find_local_maxima(gray_img, min_distance=5, threshold_abs=20):
    # 使用膨胀法检测局部最大值
    kernel = np.ones((min_distance * 2 + 1, min_distance * 2 + 1), dtype=np.uint8)
    dilated = cv2.dilate(gray_img, kernel)
    maxima = (gray_img == dilated) & (gray_img >= threshold_abs)
    coords = np.column_stack(np.where(maxima))
    return coords

def main():
    bgr = cv2.imread('002.jpg', cv2.IMREAD_COLOR)
    a_image = bgr.copy()

    H0, W0 = a_image.shape[:2]
    out_H, out_W = (H0, H0)

    cur_pixels = H0 * W0
    target_pixels = 2000000
    if cur_pixels > target_pixels:
        scale_exp = (target_pixels / cur_pixels) ** 0.5
        out_H = int(H0 * scale_exp)
        out_W = int(W0 * scale_exp)
    else:
        out_H = H0
        out_W = W0
        scale_exp = 1.0
    scale_exp2 = 1080 / out_H
    out_H = 1080
    out_W = int(out_W * scale_exp2) // 2 * 2
    scale_exp *= scale_exp2
    img_for_export = cv2.resize(a_image, (out_W, out_H), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img_for_export, cv2.COLOR_BGR2GRAY)
    coords = find_local_maxima(gray, min_distance=5, threshold_abs=20)
    np.random.shuffle(coords)
    coords = coords[:1000]
    particles = np.array([[x, y, np.random.uniform(0.1, 1.0)] for y, x in coords])
    bg = img_for_export.copy()
    export_fps = 30
    duration = 10

    bg_offset_x = 0.0
    bg_offset_y = 0.0
    bg_offset_z = 0.3
    bg_speed = 1
    bg_dir_x = 0
    bg_dir_y = 0
    bg_dir_z = -2
    bg_rotate = -4

    dir_speed = 4
    p_min = 1
    p_max = 2
    praticles_rotate = -3

    fade = 1000

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter('output.mp4', fourcc, export_fps, (out_W, out_H))

    for frame_num in range(int(duration * export_fps)):
        t = frame_num / export_fps

        angle = bg_rotate * (t / duration)
        drift_z = bg_dir_z * bg_speed * t * 0.02
        init_z = bg_offset_z
        scale_bg = 1 + init_z + drift_z
        init_x = bg_offset_x + bg_dir_x * bg_speed * t * 15
        init_y = bg_offset_y + bg_dir_y * bg_speed * t * 15
        M = get_affine_matrix(W_src=bg.shape[1], H_src=bg.shape[0], W_out=out_W, H_out=out_H,
                             scale=scale_bg, angle_deg=angle, dx=init_x, dy=init_y)
        frame = cv2.warpAffine(bg, M, (out_W, out_H), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

        dx, dy, dz = direction_vector()
        speed = dir_speed * 0.01
        p_angle = praticles_rotate * (t / duration)
        theta = np.deg2rad(p_angle)
        cos_theta, sin_theta = (np.cos(theta), np.sin(theta))

        particle_layer = np.zeros((out_H, out_W, 3), dtype=np.float32)

        for x, y, z in particles:
            z3 = z + t * speed * dz
            if not 0.05 < z3 < 2:
                continue
            scale_p = 1 / (z3 + 1e-05)
            x0, y0 = (x - out_W / 2, y - out_H / 2)
            x_rot = x0 * cos_theta - y0 * sin_theta
            y_rot = x0 * sin_theta + y0 * cos_theta
            x2d = int(out_W / 2 + x_rot * scale_p + t * speed * dx * 150 * scale_exp)
            y2d = int(out_H / 2 + y_rot * scale_p + t * speed * dy * 150 * scale_exp)

            base_size = int(np.interp(scale_p, [0.1, 1.0], [p_min, p_max]) * scale_exp)
            glow_size = base_size * 3

            if 0 <= x2d < out_W and 0 <= y2d < out_H:
                glow_intensity = 0.2
                cv2.circle(particle_layer, (x2d, y2d), glow_size,
                          (glow_intensity, glow_intensity, glow_intensity), -1)

                core_intensity = 3.0
                core_size = max(1, base_size // 2)
                cv2.circle(particle_layer, (x2d, y2d), core_size,
                          (core_intensity, core_intensity, core_intensity), -1)

        blur_ksize = int(base_size) | 1
        blur_ksize = max(3, blur_ksize)
        particle_layer = cv2.GaussianBlur(particle_layer, (blur_ksize, blur_ksize), sigmaX=0)

        frame_float = frame.astype(np.float32) / 255.0
        combined = cv2.add(frame_float, particle_layer)
        combined = np.clip(combined * 1.2, 0, 1.5)

        frame = (np.clip(combined, 0, 1) * 255).astype(np.uint8)

        alpha = 1.0
        fade_s = fade / 1000.0
        if t < fade_s:
            alpha = t / fade_s
        elif t > duration - fade_s:
            alpha = (duration - t) / fade_s
        frame = (frame * alpha).astype(np.uint8)

        # Write frame to video (OpenCV uses BGR format)
        video_writer.write(frame)

    video_writer.release()

if __name__ == "__main__":
    main()
