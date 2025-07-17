from PIL import Image
import numpy as np
from skimage.color import rgb2gray
from skimage.feature import peak_local_max
from moviepy.video.VideoClip import VideoClip
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


def main():
    pil = Image.open('002.jpg').convert('RGB')
    rgb = np.array(pil)
    a_image = rgb[:, :, ::-1] # 转换为BGR, opencv 使用

    H0, W0 = a_image.shape[:2]
    out_H, out_W = (H0, W0)

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
    target_bitrate = '8M'

    gray = rgb2gray(img_for_export)
    coords = peak_local_max(gray, min_distance=2, threshold_abs=20 / 255.0)
    np.random.shuffle(coords)
    coords = coords[:250]
    particles = np.array([[x, y, np.random.uniform(0.1, 1.0)] for y, x in coords])
    bg = img_for_export[:, :, ::-1].copy()
    export_fps = 30


    bg_offset_x = 0.0 # 初始横向位置
    bg_offset_y = 0.0 # 初始纵向位置
    bg_offset_z = 0.3# 初始远近位置
    bg_speed = 1 # 背景移动速度
    bg_dir_x = 0 # 横向移动方向
    bg_dir_y = 0 # 纵向移动方向
    bg_dir_z = -2 # 远近移动方向
    bg_rotate = -4 # 背景旋转角度

    dir_speed = 4 # 粒子移动速度
    p_min = 1 # 粒子最小半径
    p_max = 4 # 粒子最大半径
    praticles_rotate = -3 # 粒子旋转角度

    fade = 1000 # 淡入淡出时间 ms

    def make_frame(t):
        duration = 15
        angle = bg_rotate * (t / duration)
        drift_z = bg_dir_z * bg_speed * t * 0.02
        init_z = bg_offset_z
        scale_bg = 1 + init_z + drift_z
        init_x = bg_offset_x + bg_dir_x * bg_speed * t * 15
        init_y = bg_offset_y + bg_dir_y * bg_speed * t * 15
        M = get_affine_matrix(W_src=bg.shape[1], H_src=bg.shape[0], W_out=out_W, H_out=out_H, scale=scale_bg, angle_deg=angle, dx=init_x, dy=init_y)
        frame = cv2.warpAffine(bg, M, (out_W, out_H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

        dx, dy, dz = direction_vector()
        speed = dir_speed * 0.01
        p_angle = praticles_rotate * (t / duration)
        theta = np.deg2rad(p_angle)
        cos_theta, sin_theta = (np.cos(theta), np.sin(theta))

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
            size = int(np.interp(scale_p, [0.1, 1.0], [p_min, p_max]) * scale_exp)  
            if 0 <= x2d < out_W and 0 <= y2d < out_H:
                cv2.circle(frame, (x2d, y2d), size, (255, 255, 255), -1)

        alpha = 1.0
        fade_s = fade / 1000.0
        if t < fade_s:
            alpha = t / fade_s
        elif t > duration - fade_s:
            alpha = (duration - t) / fade_s
        frame = (frame * alpha).astype(np.uint8)
        return frame

    clip = VideoClip(make_frame, duration=15, )
    clip.write_videofile('output.mp4', fps=export_fps, bitrate=target_bitrate, threads=7)


if __name__ == "__main__":
    main()
