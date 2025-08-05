import cv2
import numpy as np


class Render:
    def __init__(self, image_path: str, particle_image_path: str):
        self._ori_image = cv2.imread(image_path)
        h, w = self._ori_image.shape[:2]

        # 调整分辨率，输出 200 万像素（高清）
        cur_pixels = h * w
        target_pixels = 2000000
        scale_exp = 1.0
        if cur_pixels > target_pixels:
            scale_exp = (target_pixels / cur_pixels) ** 0.5
            out_h = int(h * scale_exp)
            out_w = int(w * scale_exp)
        else:
            out_h = h
            out_w = w
        scale_exp2 = 1080 / out_h
        self._out_h = 1080
        self._out_w = int(out_w * scale_exp2) // 2 * 2
        scale_exp *= scale_exp2

        # 矫正过的图片
        self._resized_image = cv2.resize(self._ori_image, (self._out_w, self._out_h), interpolation=cv2.INTER_AREA)

        # 粒子图片(带 alpha)
        self._particle_image = cv2.imread(particle_image_path, cv2.IMREAD_UNCHANGED)

        # 计算粒子
        self._all_coords = self._find_local_maxima( min_distance=5, threshold=20)
        np.random.shuffle(self._all_coords)

    # 加载参数
    def load_params(self, 
                    z_init=3,         # 初始远近
                    z_dir=-1,           # 远近移动方向
                    speed=1,            # 照片移动速度
                    rotate=-5,          # 照片旋转角度
                    particle_dir=-1,    # 粒子移动方向
                    particle_size=16,   # 粒子尺寸
                    particle_num=1000,  # 粒子数量
                    particle_rotate=-4, # 粒子旋转角度
                    particle_speed=3,   # 粒子移动速度
                    duration=15,        # 持续时间
                    fade=1.0,           # 淡入淡出时间
                    fps=30,             # 帧数
                    ):
        self._z_init = z_init
        self._z_dir = z_dir
        self._speed = speed
        self._rotate = rotate
        self._particle_dir = particle_dir
        self._particle_size = particle_size
        self._particle_num = particle_num
        self._particle_rotate = particle_rotate
        self._particle_speed = particle_speed
        self._duration = duration
        self._fade = fade
        self._fps = fps
        self._total_frames = int(self._duration * self._fps)

        self._cal_particles()

    # 计算粒子
    def _cal_particles(self):
        self._coords = self._all_coords[:self._particle_num]
        # 粒子 [(x, y, z, size)...]
        self._particles = np.array([[x, y, np.random.uniform(0.1, 1.0), np.random.randint(1, self._particle_size)] for y, x in self._coords])

    @property
    def z_init(self):
        return self._z_init

    @z_init.setter
    def z_init(self, v):
        self._z_init = v

    @property
    def z_dir(self):
        return self._z_dir
    
    @z_dir.setter
    def z_dir(self, v):
        self._z_dir = v

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, v):
        self._speed = v

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, v):
        self._rotate = v

    @property
    def particle_size(self):
        return self._particle_size

    @particle_size.setter
    def particle_size(self, v):
        self._particle_size = v
        self._cal_particles()
    @property
    def particle_num(self):
        return self._particle_num

    @particle_num.setter
    def particle_num(self, v):
        self._particle_num = v
        self._cal_particles()
    
    @property
    def particle_dir(self):
        return self._particle_dir
    
    @particle_dir.setter
    def particle_dir(self, v):
        self._particle_dir = v

    @property
    def particle_speed(self):
        return self._particle_speed

    @particle_speed.setter
    def particle_speed(self, v):
        self._particle_speed = v

    @property
    def particle_rotate(self):
        return self._particle_rotate

    @particle_rotate.setter
    def particle_rotate(self, v):
        self._particle_rotate = v

    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, v):
        self._duration = v
        self._total_frames = int(self._duration * self._fps)

    @property
    def fps(self):
        return self._fps
    
    @fps.setter
    def fps(self, v):
        self._fps = v
        self._total_frames = int(self._duration * self._fps)

    @property
    def fade(self):
        return self._fade
    
    @fade.setter
    def fade(self, v):
        self._fade = v

    def render_video(self, output_path: str, callback=None):
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, self._fps, (self._out_w, self._out_h))

        for i in range(self._total_frames):
            index, frame = self.render_one_frame(i, True)
            writer.write(frame)
            if callback:
                callback(index, self._total_frames)

        writer.release()

    def render_one_frame(self, frame_idx: int, fade_enable=False):
        t = frame_idx * 1.0 / self._fps
        
        # 背景变换
        angle = self._rotate * t * 1.0 / self._duration
        scale = 1 + self._z_init * 0.1 + self._speed * t * 0.002 * self._z_dir
        M = self._get_affine_matrix(
            scale=scale, angle_deg=angle
        )
        frame = cv2.warpAffine(self._resized_image, M, (self._out_w, self._out_h),
                             flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT,
                             borderValue=(0, 0, 0))
        
        # 粒子变换
        speed = self._particle_speed * 0.01
        p_angle = np.deg2rad(self._particle_rotate * t / self._duration)
        cos_theta, sin_theta = np.cos(p_angle), np.sin(p_angle)
        
        for x, y, z, size in self._particles:
            size = int(size)
            z3 = z + t * speed * self._particle_dir * -1
            if not 0.05 < z3 < 2:
                continue
                
            scale_p = 1 / z3
            x0, y0 = x - self._out_w / 2, y - self._out_h / 2
            x_rot = x0 * cos_theta - y0 * sin_theta
            y_rot = x0 * sin_theta + y0 * cos_theta
            x2d = int(self._out_w / 2 + x_rot * scale_p)
            y2d = int(self._out_h / 2 + y_rot * scale_p)
            
            if 0 <= x2d < self._out_w and 0 <= y2d < self._out_h:
                half = size // 2
                roi = frame[
                    max(0, y2d - half):min(self._out_h, y2d + half + size % 2),
                    max(0, x2d - half):min(self._out_w, x2d + half + size % 2)
                ]
                if roi.size > 0:
                    resized_particle = cv2.resize(
                        self._particle_image, (roi.shape[1], roi.shape[0]),
                        interpolation=cv2.INTER_AREA
                    )
                    alpha = resized_particle[:, :, 3:] / 255.0
                    frame[
                        max(0, y2d - half):min(self._out_h, y2d + half + size % 2),
                        max(0, x2d - half):min(self._out_w, x2d + half + size % 2)
                    ] = alpha * resized_particle[:, :, :3] + (1 - alpha) * roi
        
        # 淡入淡出效果
        if fade_enable:
            fade_frames = int(self._fade * self._fps)
            if frame_idx < fade_frames:
                alpha = frame_idx / fade_frames
            elif frame_idx > self._total_frames - fade_frames:
                alpha = (self._total_frames - frame_idx) / fade_frames
            else:
                alpha = 1.0
            frame = (frame * alpha).astype(np.uint8)

        return frame_idx, frame

    def _find_local_maxima(self, min_distance, threshold):
        gray_image = cv2.cvtColor(self._resized_image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((min_distance * 2 + 1, min_distance * 2 + 1), dtype=np.uint8)
        dilated = cv2.dilate(gray_image, kernel)
        maxima = (gray_image == dilated) & (gray_image >= threshold)
        coords = np.column_stack(np.where(maxima))
        return coords

    def _get_affine_matrix(self, scale, angle_deg):
        # 图像中心
        cx, cy = self._out_w / 2, self._out_h / 2
        
        # 缩放和旋转
        theta = np.deg2rad(angle_deg)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        # 直接计算仿射矩阵的前两行
        # 这里利用了没有平移的情况下的简化公式
        a = scale * cos_theta
        b = scale * -sin_theta
        c = (1 - a) * cx - b * cy
        d = scale * sin_theta
        e = scale * cos_theta
        f = (1 - e) * cy - d * cx
            
        return np.array([[a, b, c], [d, e, f]])    
    

if __name__ == '__main__':
    r = Render(image_path='002.jpg', particle_image_path='star2.png')
    r.load_params()

    def record(frame_num, total_frames):
        print(frame_num, total_frames)
    r.render_video(output_path="output.mp4", callback=record)
    print("视频生成完成")