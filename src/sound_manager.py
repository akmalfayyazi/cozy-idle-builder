import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sounds_dir = os.path.join(self.base_dir, "sounds")

        self.bgm_volume = 0.5
        self.sfx_volume = 0.7

        self.sfx = {}

        # preload sfx (kalau belum ada file, aman)
        self._load_sfx_safe("click", "click.wav")
        self._load_sfx_safe("error", "error.wav")

    def _load_sfx_safe(self, name, filename):
        path = os.path.join(self.sounds_dir, filename)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.sfx_volume)
            self.sfx[name] = sound

    # ================= BGM =================
    def play_bgm(self, filename, volume=None):
        path = os.path.join(self.sounds_dir, filename)
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume if volume is not None else self.bgm_volume)
            pygame.mixer.music.play(-1)

    def stop_bgm(self):
        pygame.mixer.music.stop()

    def set_bgm_volume(self, volume):
        self.bgm_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.bgm_volume)

    def get_bgm_volume(self):
        return self.bgm_volume

    # ================= SFX =================
    def play_sfx(self, name):
        if name in self.sfx:
            self.sfx[name].play()

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for s in self.sfx.values():
            s.set_volume(self.sfx_volume)

    def get_sfx_volume(self):
        return self.sfx_volume
