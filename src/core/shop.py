import time
import pygame
from enum import Enum
from visuals.color import *

# *** BARU: Konstanta ukuran grid ***
SHOP_SIZE = 100 # 100x100

class ShopType(Enum):
    FOOD = "Food"
    CLOTHING = "Clothing"
    ENTERTAINMENT = "Entertainment"
    ELECTRONICS = "Electronics"
    BOOKSTORE = "Bookstore"
    # *** BARU: Tambahkan tipe toko baru jika ada ***
    CAFE = "Cafe"

SHOP_TEMPLATES = {
    ShopType.FOOD: {
        "name": "Food Court", "cost": 500, "production_time": 30, "income": 100,
        "color": ORANGE, "icon_color": YELLOW, "level_required": 1
    },
    ShopType.CLOTHING: {
        "name": "Fashion Store", "cost": 1000, "production_time": 60, "income": 200,
        "color": PINK, "icon_color": RED, "level_required": 2
    },
    ShopType.ENTERTAINMENT: {
        "name": "Game Center", "cost": 1500, "production_time": 90, "income": 300,
        "color": PURPLE, "icon_color": BLUE, "level_required": 3
    },
    ShopType.ELECTRONICS: {
        "name": "Tech Store", "cost": 2000, "production_time": 120, "income": 400,
        "color": BLUE, "icon_color": LIGHT_BLUE, "level_required": 4
    },
    ShopType.BOOKSTORE: {
        "name": "Book Haven", "cost": 800, "production_time": 45, "income": 150,
        "color": BROWN, "icon_color": YELLOW, "level_required": 2
    },
    # *** BARU: Template untuk toko baru ***
    ShopType.CAFE: {
        "name": "Coffee Shop", "cost": 600, "production_time": 35, "income": 120,
        "color": (139, 69, 19), "icon_color": (245, 222, 179), "level_required": 1
    }
}

class Shop:
    def __init__(self, shop_type, x, y):
        self.type = shop_type
        self.template = SHOP_TEMPLATES[shop_type]
        self.x = x
        self.y = y
        # *** DIUBAH: Gunakan konstanta SHOP_SIZE ***
        self.width = SHOP_SIZE
        self.height = SHOP_SIZE
        self.level = 1
        self.is_producing = False
        self.production_start = None
        self.customers_served = 0
        
    def start_production(self):
        self.is_producing = True
        self.production_start = time.time()
        
    def get_production_progress(self):
        if not self.is_producing:
            return 0
        elapsed = time.time() - self.production_start
        progress = (elapsed / self.template["production_time"]) * 100
        return min(progress, 100)
    
    def collect_income(self):
        if self.is_producing and self.get_production_progress() >= 100:
            self.is_producing = False
            return self.template["income"] * self.level
        return 0
    
    @staticmethod
    def draw_preview(screen, x, y, shop_type):
        """ *** BARU: Menggambar pratinjau toko 50x50 untuk menu *** """
        try:
            template = SHOP_TEMPLATES[shop_type]
            color = template["color"]
            icon_color = template["icon_color"]
            width, height = 50, 50 # Ukuran preview
            
            shop_rect = pygame.Rect(x, y, width, height)
            pygame.draw.rect(screen, color, shop_rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, shop_rect, 2, border_radius=8)
            
            # Atap (disederhanakan)
            roof_points = [
                (x, y + 10),
                (x + width // 2, y - 3),
                (x + width, y + 10)
            ]
            pygame.draw.polygon(screen, icon_color, roof_points)
            pygame.draw.polygon(screen, BLACK, roof_points, 1)
            
            # Pintu (disederhanakan)
            door_rect = pygame.Rect(x + width // 2 - 8, y + 25, 16, 25)
            pygame.draw.rect(screen, (101, 67, 33), door_rect, border_radius=3)
        except Exception as e:
            # Fallback jika ada error (misal, template tidak ditemukan)
            pygame.draw.rect(screen, RED, (x, y, 50, 50))
            print(f"Error drawing preview: {e}")

    
    def draw(self, screen, offset_x, offset_y):
        # *** DIUBAH: Ukuran 100x100 dan proporsi disesuaikan ***
        draw_x = self.x + offset_x
        draw_y = self.y + offset_y
        
        shadow_rect = pygame.Rect(draw_x + 4, draw_y + 4, self.width, self.height)
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=12)
        
        shop_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        pygame.draw.rect(screen, self.template["color"], shop_rect, border_radius=12)
        pygame.draw.rect(screen, BLACK, shop_rect, 3, border_radius=12)
        
        # Atap (disesuaikan untuk 100px)
        roof_points = [
            (draw_x, draw_y + 20),
            (draw_x + self.width // 2, draw_y - 10),
            (draw_x + self.width, draw_y + 20)
        ]
        pygame.draw.polygon(screen, self.template["icon_color"], roof_points)
        pygame.draw.polygon(screen, BLACK, roof_points, 2)
        
        # Pintu (disesuaikan untuk 100px)
        door_rect = pygame.Rect(draw_x + self.width // 2 - 15, draw_y + 55, 30, 40)
        pygame.draw.rect(screen, (101, 67, 33), door_rect, border_radius=5)
        pygame.draw.circle(screen, YELLOW, (draw_x + self.width // 2 + 8, draw_y + 75), 3)
        
        # Jendela (disesuaikan untuk 100px)
        window1 = pygame.Rect(draw_x + 15, draw_y + 30, 20, 20)
        window2 = pygame.Rect(draw_x + self.width - 35, draw_y + 30, 20, 20)
        pygame.draw.rect(screen, LIGHT_BLUE, window1, border_radius=3)
        pygame.draw.rect(screen, LIGHT_BLUE, window2, border_radius=3)
        pygame.draw.rect(screen, BLACK, window1, 1, border_radius=3)
        pygame.draw.rect(screen, BLACK, window2, 1, border_radius=3)
        
        # Progress bar
        if self.is_producing:
            progress = self.get_production_progress()
            bar_width = int((self.width - 10) * progress / 100)
            pygame.draw.rect(screen, DARK_GRAY, (draw_x + 5, draw_y - 15, self.width - 10, 8), border_radius=4)
            pygame.draw.rect(screen, GREEN, (draw_x + 5, draw_y - 15, bar_width, 8), border_radius=4)