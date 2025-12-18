import pygame
from color import *
from enum import Enum

# Baru: Enum untuk tipe dekorasi
class DecorationType(Enum):
    TREE = "tree"
    BENCH = "bench"
    FOUNTAIN = "fountain"

# Baru: Template untuk harga dan nama
DECORATION_TEMPLATES = {
    DecorationType.TREE: {
        "name": "Pohon Hias",
        "cost": 100
    },
    DecorationType.BENCH: {
        "name": "Bangku Taman",
        "cost": 150
    },
    DecorationType.FOUNTAIN: {
        "name": "Air Mancur",
        "cost": 300
    }
}

class Decoration:
    def __init__(self, dec_type, x, y):
        self.type = dec_type # Sekarang Enum, bukan string
        self.template = DECORATION_TEMPLATES[dec_type]
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        
    def draw(self, screen, offset_x, offset_y):
        # Panggil fungsi draw_preview statis dengan posisi yang benar
        Decoration.draw_preview(screen, self.x + offset_x, self.y + offset_y, self.type)

    @staticmethod
    def draw_preview(screen, draw_x, draw_y, dec_type):
        """
        Fungsi statis untuk menggambar pratinjau dekorasi di mana saja.
        Digunakan oleh menu dan oleh ghost penempatan.
        """
        if dec_type == DecorationType.TREE:
            # Tree trunk
            pygame.draw.rect(screen, BROWN, (draw_x + 15, draw_y + 20, 10, 20))
            # Tree foliage (3 circles)
            pygame.draw.circle(screen, GREEN, (draw_x + 20, draw_y + 15), 15)
            pygame.draw.circle(screen, (34, 139, 34), (draw_x + 15, draw_y + 10), 12)
            pygame.draw.circle(screen, (50, 205, 50), (draw_x + 25, draw_y + 10), 12)
        elif dec_type == DecorationType.BENCH:
            # Bench
            pygame.draw.rect(screen, BROWN, (draw_x + 5, draw_y + 25, 30, 5))
            pygame.draw.rect(screen, BROWN, (draw_x + 5, draw_y + 15, 5, 15))
            pygame.draw.rect(screen, BROWN, (draw_x + 30, draw_y + 15, 5, 15))
            pygame.draw.rect(screen, BROWN, (draw_x + 5, draw_y + 10, 30, 5))
        elif dec_type == DecorationType.FOUNTAIN:
            # Fountain base
            pygame.draw.ellipse(screen, BLUE, (draw_x + 5, draw_y + 25, 30, 15))
            pygame.draw.ellipse(screen, LIGHT_BLUE, (draw_x + 10, draw_y + 20, 20, 10))
            # Water drops
            for i in range(3):
                drop_x = draw_x + 15 + i * 5
                pygame.draw.circle(screen, LIGHT_BLUE, (drop_x, draw_y + 15), 2)