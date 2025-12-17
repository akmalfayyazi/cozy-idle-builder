import random
import pygame
import math
import time
from enum import Enum
from visuals.color import *

SCREEN_WIDTH = 1200
# *** BARU: Menambahkan BORDER_THICKNESS di sini untuk konversi ***
BORDER_THICKNESS = 15

class CustomerMood(Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    ANGRY = "angry"

class CustomerState(Enum):
    WALKING_ON_ROAD = "walking_on_road"
    WALKING_TO_MALL = "walking_to_mall"
    # ENTERING_MALL dihapus
    SHOPPING = "shopping"
    EXITING_MALL = "exiting_mall"
    LEAVING = "leaving"
    LEAVING_ON_ROAD = "leaving_on_road"

class Customer:
    customer_images = []
    images_loaded = False

    @classmethod
    def load_images(cls):
        if cls.images_loaded:
            return

        try:
            import os, pygame

            BASE_DIR = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
            )
            ASSETS_DIR = os.path.join(BASE_DIR, "assets")

            for i in range(1, 4):
                image_path = os.path.join(ASSETS_DIR, f"foto-{i}.png")
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.smoothscale(img, (80, 80))
                cls.customer_images.append(img)

            cls.images_loaded = True

        except Exception as e:
            print(f"✗ Error loading customer images: {e}")
            cls.images_loaded = False

    def __init__(self, target_shop=None, mall_entrance_x=None, mall_entrance_y=None):
        # mall_entrance_x dan y sekarang adalah KOORDINAT DUNIA (sudah + border)
        if not Customer.images_loaded:
            Customer.load_images()
        
        self.target_shop = target_shop
        self.mall_entrance_x = mall_entrance_x 
        self.mall_entrance_y = mall_entrance_y
        
        self.spawn_side = random.choice([-1, 1])
        if self.spawn_side == -1:
            self.x = -50 # Koordinat Dunia
        else:
            self.x = SCREEN_WIDTH + 50 # Koordinat Dunia
        
        self.y = 100  # Koordinat Dunia
        self.state = CustomerState.WALKING_ON_ROAD
        
        self.speed = random.uniform(0.8, 1.5)
        self.mood = CustomerMood.NEUTRAL
        self.radius = 40
        self.color = self.get_color_by_mood()
        self.has_purchased = False
        self.direction = 0
        self.waiting_time = 0
        
        if Customer.customer_images:
            self.image = random.choice(Customer.customer_images)
            self.use_image = True
        else:
            self.image = None
            self.use_image = False
        
    def get_color_by_mood(self):
        if self.mood == CustomerMood.HAPPY: return GREEN
        elif self.mood == CustomerMood.ANGRY: return RED
        return BLUE
    
    def update(self):
        self.direction += 0.1
        
        if self.state == CustomerState.WALKING_ON_ROAD:
            # 1. Bergerak di jalan ke Pintu Masuk (Koordinat Dunia)
            dx = self.mall_entrance_x - self.x
            if abs(dx) > self.speed:
                self.x += self.speed if dx > 0 else -self.speed
            else:
                self.x = self.mall_entrance_x
                self.state = CustomerState.WALKING_TO_MALL

        elif self.state == CustomerState.WALKING_TO_MALL:
            # 2. Bergerak di trotoar ke Pintu Masuk (Koordinat Dunia)
            dy = self.mall_entrance_y - self.y
            if abs(dy) > self.speed:
                self.y += self.speed
            else:
                self.y = self.mall_entrance_y
                self.state = CustomerState.SHOPPING
                
                # *** FIX: Konversi ke Koordinat INTERNAL Mal ***
                self.x = self.x - BORDER_THICKNESS
                self.y = 0 
                
        elif self.state == CustomerState.SHOPPING:
            # 3. Bergerak ke toko (Koordinat Internal)
            target_x = self.target_shop.x + self.target_shop.width // 2
            target_y = self.target_shop.y + self.target_shop.height // 2
            
            dx = target_x - self.x
            dy = target_y - self.y
            
            if abs(dx) > self.speed:
                self.x += self.speed if dx > 0 else -self.speed
            elif abs(dy) > self.speed:
                self.y += self.speed if dy > 0 else -self.speed
            else:
                self.x = target_x
                self.y = target_y
                if not self.has_purchased:
                    self.has_purchased = True
                    self.mood = CustomerMood.HAPPY
                    self.color = self.get_color_by_mood()
                    self.waiting_time = time.time()
                elif time.time() - self.waiting_time > 1:
                    self.state = CustomerState.EXITING_MALL
                        
        elif self.state == CustomerState.EXITING_MALL:
            # 4. Kembali ke pintu (Koordinat Internal)
            # Hitung target X internal pintu
            target_x = self.mall_entrance_x - BORDER_THICKNESS 
            target_y = 0 
            
            dx = target_x - self.x
            dy = target_y - self.y

            if abs(dy) > self.speed:
                self.y += self.speed if dy > 0 else -self.speed
            elif abs(dx) > self.speed:
                self.x += self.speed if dx > 0 else -self.speed
            else:
                self.x = target_x
                self.y = target_y
                self.state = CustomerState.LEAVING
                
                # *** FIX: Konversi kembali ke Koordinat DUNIA ***
                self.x = self.x + BORDER_THICKNESS
                self.y = self.mall_entrance_y 

        elif self.state == CustomerState.LEAVING:
            # 5. Bergerak kembali ke jalan (Koordinat Dunia)
            target_y = 100
            dy = target_y - self.y
            if abs(dy) > self.speed:
                self.y -= self.speed
            else:
                self.y = target_y
                self.state = CustomerState.LEAVING_ON_ROAD

        elif self.state == CustomerState.LEAVING_ON_ROAD:
            # 6. Bergerak keluar layar (Koordinat Dunia)
            exit_x = -50 if self.spawn_side == 1 else SCREEN_WIDTH + 50
            dx = exit_x - self.x
            if abs(dx) > self.speed:
                self.x += self.speed if dx > 0 else -self.speed
            else:
                self.y = -100
    
    def should_remove(self):
        return self.y < 0
    
    def draw(self, screen, offset_x, offset_y): 
        draw_x = int(self.x + offset_x)
        draw_y = int(self.y + offset_y)
        
        offset = math.sin(self.direction) * 3
        
        if self.use_image and self.image:
            img_rect = self.image.get_rect(center=(draw_x, draw_y + int(offset)))
            shadow_radius = 15
            shadow_surf = pygame.Surface((shadow_radius * 2, shadow_radius * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 30), (0, 0, shadow_radius * 2, shadow_radius * 2))
            shadow_rect = shadow_surf.get_rect(center=(draw_x, draw_y + 25))
            screen.blit(shadow_surf, shadow_rect)
            screen.blit(self.image, img_rect)
            
            if self.mood == CustomerMood.HAPPY:
                emoji_y = draw_y + int(offset) - 28
                pygame.draw.circle(screen, GREEN, (draw_x + 15, emoji_y), 6)
                pygame.draw.circle(screen, WHITE, (draw_x + 15, emoji_y), 6, 1)
                pygame.draw.arc(screen, WHITE, (draw_x + 12, emoji_y - 1, 6, 4), 3.14, 0, 1)
            
            if self.has_purchased:
                bag_x = draw_x + 20; bag_y = draw_y + int(offset) + 8
                bag_points = [(bag_x, bag_y), (bag_x + 10, bag_y), (bag_x + 9, bag_y + 12), (bag_x + 1, bag_y + 12)]
                pygame.draw.polygon(screen, ORANGE, bag_points)
                pygame.draw.polygon(screen, (139, 69, 19), bag_points, 1)
                pygame.draw.arc(screen, (139, 69, 19), (bag_x + 2, bag_y - 3, 6, 5), 0, 3.14, 1)
        else:
            pygame.draw.circle(screen, self.color, (draw_x, draw_y + int(offset)), self.radius)
            pygame.draw.circle(screen, BLACK, (draw_x, draw_y + int(offset)), self.radius, 2)
            pygame.draw.circle(screen, (255, 220, 177), (draw_x, draw_y - 10 + int(offset)), 6)
            pygame.draw.circle(screen, BLACK, (draw_x, draw_y - 10 + int(offset)), 6, 1)
            pygame.draw.circle(screen, BLACK, (draw_x - 2, draw_y - 11 + int(offset)), 1)
            pygame.draw.circle(screen, BLACK, (draw_x + 2, draw_y - 11 + int(offset)), 1)
            if self.mood == CustomerMood.HAPPY: pygame.draw.arc(screen, BLACK, (draw_x - 3, draw_y - 8 + offset, 6, 4), math.pi, 0, 1)
            elif self.mood == CustomerMood.ANGRY: pygame.draw.line(screen, BLACK, (draw_x - 3, draw_y - 7 + offset), (draw_x + 3, draw_y - 7 + offset), 1)
            if self.has_purchased:
                bag_points = [(draw_x + 8, draw_y + 5), (draw_x + 14, draw_y + 5), (draw_x + 13, draw_y + 12), (draw_x + 9, draw_y + 12)]
                pygame.draw.polygon(screen, ORANGE, bag_points)
                pygame.draw.polygon(screen, BLACK, bag_points, 1)