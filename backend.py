import json
from PySide6.QtCore import QObject, Signal, Slot, QThreadPool, QRunnable
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtGui import QImage, QPixmap
import render
import cv2
from utils import resource_path, handle_file_url


class RenderThread(QRunnable):
    def __init__(self, fn, path, callback, finish):
        super().__init__()
        self.fn = fn
        self._path = path
        self._callback = callback
        self._finish = finish

    def run(self):
        self.fn(self._path, self._callback)
        self._finish.emit()


class RenderImageThread(QRunnable):
    def __init__(self, render, image_processor, finish):
        super().__init__()
        self._render = render
        self._image_processor = image_processor
        self._finish = finish

    def run(self):
        _, begin_frame = self._render.render_one_frame(0)
        _, end_frame = self._render.render_one_frame(self._render.duration * self._render.fps-1)
        self._image_processor.update_begin_image(begin_frame)
        self._image_processor.update_end_image(end_frame)
        self._finish.emit()


class ImageProcessor(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Pixmap)
        self._begin = QPixmap()
        self._end = QPixmap()
        
    def requestPixmap(self, id: str, size, requestedSize):
        if id.startswith('begin'):
            return self._begin
        elif id.startswith('end'):
            return self._end
        else:
            return QPixmap()
    
    def update_begin_image(self, processed: cv2.Mat):
        # 转换为QImage
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        height, width, _ = processed.shape
        bytes_per_line = 3*width
        qimg = QImage(processed.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # 转换为QPixmap并保存
        self._begin = QPixmap.fromImage(qimg)
        return True
    
    def update_end_image(self, processed: cv2.Mat):
        # 转换为QImage
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        height, width, _ = processed.shape
        bytes_per_line = 3*width
        qimg = QImage(processed.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # 转换为QPixmap并保存
        self._end = QPixmap.fromImage(qimg)
        return True
    

class Backend(QObject):
    imageProcessed = Signal()
    paramsLoaded = Signal()
    progressChanged = Signal(int)
    videoFinished = Signal()

    def __init__(self, image_processor: ImageProcessor):
        super().__init__()
        self.image_path = None
        self.image_processor = image_processor
        self._default_params_file = 'nebula-dance-default-params.json'
        self.thread_pool = QThreadPool()
        self.params = {
            "z_init": 3,
            "z_dir": -1,
            "speed": 1,
            "rotate": -5,
            "particle_dir": -1,
            "particle_size": 16,
            "particle_num": 1000,
            "particle_rotate": -4,
            "particle_speed": 3,
            "duration": 15,
        }
        with open(self._default_params_file, 'w') as f:
            json.dump(self.params, f)

    @Slot(str)
    def load_image(self, path):
        self.image_path = handle_file_url(path)
        self.render = render.Render(image_path=self.image_path, particle_image_path=resource_path('star2.png'))
        self.render.load_params(**self.params)
        self.paramsLoaded.emit()
        self.render_first_end_frame()

    @Slot(str)
    def load_params(self, path):
        with open(handle_file_url(path)) as f:
            params = f.read()
        self.params = json.loads(params)
        self.paramsLoaded.emit()
        render = getattr(self, 'render', None)
        if render:
            self.render.load_params(**self.params)

    @Slot(str)
    def save_params(self, path):
        with open(handle_file_url(path), 'w') as f:
            f.write(json.dumps(self.params))

    @Slot()
    def render_first_end_frame(self):
        image_thread = RenderImageThread(self.render, self.image_processor, self.imageProcessed)
        self.thread_pool.start(image_thread)

    @Slot(str)
    def render_video(self, video_path):
        self.progress = 0
        def callback(frame_num, total_frames):
            self.progress = int( frame_num * 1.0 / total_frames * 100 )
            self.progressChanged.emit(self.progress)

        video_thread = RenderThread(self.render.render_video, video_path, callback, self.videoFinished)
        self.thread_pool.start(video_thread)

    @Slot(int)
    def z_init_changed(self, val):
        self.render.z_init = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_z_init(self):
        return self.params['z_init']
    
    @Slot(int)
    def z_dir_changed(self, val):
        self.render.z_dir = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_z_dir(self):
        return self.params['z_dir']
    
    @Slot(int)
    def speed_changed(self, val):
        self.render.speed = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_speed(self):
        return self.params['speed']
    
    @Slot(int)
    def rotate_changed(self, val):
        self.render.rotate = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_rotate(self):
        return self.params['rotate']
    
    @Slot(int)
    def duration_changed(self, val):
        self.render.duration = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_duration(self):
        return self.params['duration']
    
    @Slot(int)
    def particle_num_changed(self, val):
        self.render.particle_num = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_particle_num(self):
        return self.params['particle_num']
    
    @Slot(int)
    def particle_size_changed(self, val):
        self.render.particle_size = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_particle_size(self):
        return self.params['particle_size']
    
    @Slot(int)
    def particle_speed_changed(self, val):
        self.render.particle_speed = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_particle_speed(self):
        return self.params['particle_speed']
    
    @Slot(int)
    def particle_rotate_changed(self, val):
        self.render.particle_rotate = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_particle_rotate(self):
        return self.params['particle_rotate']
    
    @Slot(int)
    def particle_dir_changed(self, val):
        self.render.particle_dir = val
        self.render_first_end_frame()

    @Slot(result=int)
    def get_particle_dir(self):
        return self.params['particle_dir']