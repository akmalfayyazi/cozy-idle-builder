import pygame
import random
import time

from mall import Mall
from quest import Quest
from customer import Customer, CustomerState
from shop import Shop, ShopType, SHOP_TEMPLATES
from decoration import Decoration, DecorationType, DECORATION_TEMPLATES
from save_manager import SaveManager
from sound_manager import SoundManager
from main_menu import MainMenu
from color import *

pygame.init() 

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60    

TILE_SIZE = 50
SHOP_GRID_SIZE = 100 
BORDER_THICKNESS = 15

class Game:
    def __init__(self, save_slot=1, load_from_save=False):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cozy Idle Builder")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.save_manager = SaveManager()
        self.save_slot = save_slot
        self.last_autosave = time.time()
        self.autosave_interval = 30
        
        self.sound_manager = SoundManager()
        
        if load_from_save:
            self.load_game_data()
        else:
            self.init_new_game()
        
        self.sound_manager.play_bgm('bgm_gameplay.mp3')
        
        self.selected_shop_type = None
        self.selected_decoration_type = None
        self.placing_shop = False
        self.placing_decoration = False
        
        self.show_shop_menu = False
        self.show_decorate_menu = False
        self.show_quest_menu = False
        self.show_mall_info = False
        self.show_expand_menu = False
        self.show_save_menu = False
        
        self.shop_scroll_y = 0
        self.decorate_scroll_y = 0
        self.quest_scroll_y = 0
        
        self.close_button_rect = pygame.Rect(0, 0, 24, 24)

        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 36)
        
        self.last_customer_spawn = time.time()
        self.customer_spawn_interval = 3
    
    def init_new_game(self):
        self.coins = 2000
        self.gems = 50
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.mall = Mall(800, 500)
        self.camera_x = 0
        self.camera_y = 0
        self.shops = []
        self.customers = []
        self.decorations = []
        self.init_quests()
    
    def init_quests(self):
        self.quests = [
            Quest("Build 3 shops", 3, 500, 50),
            Quest("Serve 10 customers", 10, 300, 30),
            Quest("Earn 1000 coins", 1000, 200, 40),
            Quest("Expand your mall", 1, 1000, 100),
            Quest("Build a Cafe", 1, 100, 10),
            Quest("Place 5 decorations", 5, 200, 20)
        ]
    
    def save_game_data(self):
        game_data = {
            'coins': self.coins,
            'gems': self.gems,
            'level': self.level,
            'xp': self.xp,
            'xp_to_next_level': self.xp_to_next_level,
            'mall': {
                'width': self.mall.width,
                'height': self.mall.height,
                'level': self.mall.level
            },
            'shops': [
                {
                    'type': shop.type.value,
                    'x': shop.x,
                    'y': shop.y,
                    'level': shop.level,
                    'customers_served': shop.customers_served
                }
                for shop in self.shops
            ],
            'decorations': [
                {
                    'type': dec.type.value,
                    'x': dec.x,
                    'y': dec.y
                }
                for dec in self.decorations
            ],
            'quests': [
                {
                    'description': quest.description,
                    'target': quest.target,
                    'progress': quest.progress,
                    'reward_coins': quest.reward_coins,
                    'reward_xp': quest.reward_xp,
                    'completed': quest.completed
                }
                for quest in self.quests
            ]
        }
        
        success = self.save_manager.save_game(game_data, self.save_slot)
        if success:
            self.sound_manager.play_sfx('click')
            print(f"✓ Game saved to slot {self.save_slot}!")
        return success
    
    def load_game_data(self):
        game_data = self.save_manager.load_game(self.save_slot)
        
        if game_data is None:
            print("⚠ No save found, starting new game")
            self.init_new_game()
            return
        
        self.coins = game_data.get('coins', 2000)
        self.gems = game_data.get('gems', 50)
        self.level = game_data.get('level', 1)
        self.xp = game_data.get('xp', 0)
        self.xp_to_next_level = game_data.get('xp_to_next_level', 100)
        
        mall_data = game_data.get('mall', {})
        self.mall = Mall(mall_data.get('width', 800), mall_data.get('height', 500))
        self.mall.level = mall_data.get('level', 1)
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.shops = []
        for shop_data in game_data.get('shops', []):
            try:
                shop_type = ShopType(shop_data['type'])
                shop = Shop(shop_type, shop_data['x'], shop_data['y'])
                shop.level = shop_data.get('level', 1)
                shop.customers_served = shop_data.get('customers_served', 0)
                self.shops.append(shop)
            except:
                print(f"⚠ Failed to load shop: {shop_data}")
        
        self.decorations = []
        for dec_data in game_data.get('decorations', []):
            try:
                dec_type = DecorationType(dec_data['type'])
                decoration = Decoration(dec_type, dec_data['x'], dec_data['y'])
                self.decorations.append(decoration)
            except:
                print(f"⚠ Failed to load decoration: {dec_data}")
        
        self.quests = []
        for quest_data in game_data.get('quests', []):
            quest = Quest(
                quest_data['description'],
                quest_data['target'],
                quest_data['reward_coins'],
                quest_data['reward_xp']
            )
            quest.progress = quest_data.get('progress', 0)
            quest.completed = quest_data.get('completed', False)
            self.quests.append(quest)
        
        if not self.quests:
            self.init_quests()
        
        self.customers = []
        print(f"✓ Game loaded from slot {self.save_slot}!")
    
    def add_xp(self, amount):
        old_level = self.level
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        
        if self.level > old_level:
            self.sound_manager.play_sfx('levelup')
    
    def spawn_customer(self):
        if len(self.shops) > 0:
            target_shop = random.choice(self.shops)
            mall_entrance_x = self.mall.entrance_x + BORDER_THICKNESS
            mall_entrance_y = 170 + BORDER_THICKNESS 
            customer = Customer(target_shop, mall_entrance_x, mall_entrance_y)
            self.customers.append(customer)
    
    def update(self):
        if time.time() - self.last_autosave > self.autosave_interval:
            self.save_game_data()
            self.last_autosave = time.time()
        
        if time.time() - self.last_customer_spawn > self.customer_spawn_interval:
            self.spawn_customer()
            self.last_customer_spawn = time.time()
        
        for customer in self.customers[:]:
            customer.update()
            if customer.should_remove():
                self.customers.remove(customer)
                if customer.has_purchased:
                    self.sound_manager.play_sfx('happy')
                    for quest in self.quests:
                        if "customers" in quest.description.lower() and not quest.completed:
                            quest.update_progress(1)
                            if quest.completed:
                                self.sound_manager.play_sfx('quest_complete')
        
        for shop in self.shops:
            income = shop.collect_income()
            if income > 0:
                self.coins += income
                self.sound_manager.play_sfx('coin')
                shop.start_production()
                shop.customers_served += 1
                for quest in self.quests:
                    if "earn" in quest.description.lower() and not quest.completed:
                        quest.update_progress(income)
                        if quest.completed:
                            self.sound_manager.play_sfx('quest_complete')
    
    def draw_road_and_environment(self):
        pygame.draw.rect(self.screen, ROAD_GRAY, (0, 60, SCREEN_WIDTH, 80))
        for i in range(0, SCREEN_WIDTH, 60): 
            pygame.draw.rect(self.screen, YELLOW, (i, 95, 40, 5))
        pygame.draw.rect(self.screen, SIDEWALK, (0, 140, SCREEN_WIDTH, 30))
        for i in range(0, SCREEN_WIDTH, 150):
            pygame.draw.rect(self.screen, BROWN, (i + 20, 45, 8, 15))
            pygame.draw.circle(self.screen, DARK_GREEN, (i + 24, 42), 12)
    
    def draw_mall_building(self):
        mall_y_start = 170
        view_x = self.camera_x
        view_y = self.camera_y + mall_y_start
        pygame.draw.rect(self.screen, BROWN, (view_x, view_y, self.mall.width + (BORDER_THICKNESS*2), BORDER_THICKNESS))
        pygame.draw.rect(self.screen, BROWN, (view_x, view_y, BORDER_THICKNESS, self.mall.height + (BORDER_THICKNESS*2)))
        pygame.draw.rect(self.screen, BROWN, (view_x + self.mall.width + BORDER_THICKNESS, view_y, BORDER_THICKNESS, self.mall.height + (BORDER_THICKNESS*2)))
        pygame.draw.rect(self.screen, BROWN, (view_x, view_y + self.mall.height + BORDER_THICKNESS, self.mall.width + (BORDER_THICKNESS*2), BORDER_THICKNESS))
        internal_view_x = view_x + BORDER_THICKNESS
        internal_view_y = view_y + BORDER_THICKNESS
        start_tile_x = max(0, -internal_view_x // TILE_SIZE)
        start_tile_y = max(0, -internal_view_y // TILE_SIZE)
        for i in range(start_tile_x, start_tile_x + self.mall.width // TILE_SIZE + 2):
            for j in range(start_tile_y, start_tile_y + self.mall.height // TILE_SIZE + 2):
                if i*TILE_SIZE < self.mall.width and j*TILE_SIZE < self.mall.height:
                    tile_x = i * TILE_SIZE + internal_view_x
                    tile_y = j * TILE_SIZE + internal_view_y
                    color = (240, 230, 220) if (i + j) % 2 == 0 else (230, 220, 210)
                    pygame.draw.rect(self.screen, color, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
        entrance_width = 80
        entrance_x = view_x + BORDER_THICKNESS + self.mall.entrance_x - entrance_width // 2
        entrance_y = view_y 
        pygame.draw.rect(self.screen, (139, 90, 43), (entrance_x - 10, entrance_y, entrance_width + 20, BORDER_THICKNESS + 10))
        pygame.draw.rect(self.screen, (101, 67, 33), (entrance_x, entrance_y, entrance_width, BORDER_THICKNESS + 5), border_radius=5)
        glass_width = entrance_width - 20
        pygame.draw.rect(self.screen, LIGHT_BLUE, (entrance_x + 10, entrance_y + 2, glass_width, 8), border_radius=3)
        sign_text = self.font_small.render("MALL ENTRANCE", True, WHITE)
        sign_rect = pygame.Rect(entrance_x + entrance_width // 2 - 60, entrance_y - 22, 120, 20)
        pygame.draw.rect(self.screen, RED, sign_rect, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, sign_rect, 2, border_radius=5)
        self.screen.blit(sign_text, (entrance_x + entrance_width // 2 - 55, entrance_y - 20))
    
    def draw_ui(self):
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 60), 2)
        
        coin_text = self.font_medium.render(f"Coins: {self.coins}", True, BLACK)
        pygame.draw.circle(self.screen, YELLOW, (20, 20), 12)
        pygame.draw.circle(self.screen, ORANGE, (20, 20), 8)
        pygame.draw.circle(self.screen, BLACK, (20, 20), 12, 2)
        self.screen.blit(coin_text, (40, 10))
        
        gem_text = self.font_medium.render(f"Gems: {self.gems}", True, BLACK)
        points = [(220, 15), (230, 25), (220, 35), (210, 25)]
        pygame.draw.polygon(self.screen, BLUE, points)
        pygame.draw.polygon(self.screen, LIGHT_BLUE, [(215, 20), (220, 25), (215, 30), (210, 25)])
        pygame.draw.polygon(self.screen, BLACK, points, 2)
        self.screen.blit(gem_text, (240, 10))
        
        level_text = self.font_medium.render(f"Level {self.level}", True, BLACK)
        self.screen.blit(level_text, (420, 10))
        xp_bar_width = 200
        xp_progress = (self.xp / self.xp_to_next_level) * xp_bar_width
        pygame.draw.rect(self.screen, DARK_GRAY, (420, 40, xp_bar_width, 15), border_radius=7)
        pygame.draw.rect(self.screen, GREEN, (420, 40, xp_progress, 15), border_radius=7)
        pygame.draw.rect(self.screen, BLACK, (420, 40, xp_bar_width, 15), 2, border_radius=7)
        xp_text = self.font_small.render(f"{self.xp}/{self.xp_to_next_level} XP", True, WHITE)
        self.screen.blit(xp_text, (450, 42))
        
        self.draw_button("Build", 650, 10, 80, 40, BLUE)
        self.draw_button("Quest", 740, 10, 80, 40, PURPLE)
        self.draw_button("Deco", 830, 10, 70, 40, GREEN)
        self.draw_button("Info", 910, 10, 70, 40, ORANGE)
        self.draw_button("Expand", 990, 10, 90, 40, RED)
        self.draw_button("Save", 1090, 10, 100, 40, (50, 150, 200))

        self.screen.set_clip(None)
        if self.show_shop_menu:
            self.draw_shop_menu()
        if self.show_decorate_menu:
            self.draw_decorate_menu()
        if self.show_quest_menu:
            self.draw_quest_menu()
        if self.show_mall_info:
            self.draw_mall_info()
        if self.show_expand_menu:
            self.draw_expand_menu()
        if self.show_save_menu:
            self.draw_save_menu()
    
    def draw_button(self, text, x, y, width, height, color):
        pygame.draw.rect(self.screen, DARK_GRAY, (x + 2, y + 2, width, height), border_radius=10)
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=10)
        pygame.draw.rect(self.screen, BLACK, (x, y, width, height), 2, border_radius=10)
        text_surface = self.font_small.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def draw_close_button(self, menu_rect):
        x = menu_rect.right - 30
        y = menu_rect.top + 6
        self.close_button_rect.topleft = (x, y)
        pygame.draw.rect(self.screen, RED, self.close_button_rect, border_radius=5)
        pygame.draw.line(self.screen, WHITE, (x + 6, y + 6), (x + 18, y + 18), 3)
        pygame.draw.line(self.screen, WHITE, (x + 18, y + 6), (x + 6, y + 18), 3)

    def draw_save_menu(self):
        menu_width = 350
        menu_height = 200
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 200
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        
        pygame.draw.rect(self.screen, DARK_GRAY, (menu_x + 5, menu_y + 5, menu_width, menu_height), border_radius=15)
        pygame.draw.rect(self.screen, WHITE, menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3, border_radius=15)
        
        title = self.font_large.render("Save Game", True, BLACK)
        self.screen.blit(title, (menu_x + 20, menu_y + 20))
        
        self.draw_close_button(menu_rect)
        
        slot_text = self.font_medium.render(f"Slot: {self.save_slot}", True, BLACK)
        self.screen.blit(slot_text, (menu_x + 20, menu_y + 70))
        
        self.draw_button("Save Now", menu_rect.centerx - 100, menu_y + 120, 200, 50, GREEN)
    
    def draw_shop_menu(self):
        menu_width = 400
        menu_height = 450
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 80
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)

        pygame.draw.rect(self.screen, DARK_GRAY, (menu_x + 5, menu_y + 5, menu_width, menu_height), border_radius=15)
        pygame.draw.rect(self.screen, WHITE, menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3, border_radius=15)
        
        title = self.font_large.render("Build Shop", True, BLACK)
        self.screen.blit(title, (menu_x + 20, menu_y + 20))
        
        self.draw_close_button(menu_rect)
        
        content_height = menu_height - 90
        content_rect = pygame.Rect(menu_x + 10, menu_y + 70, menu_width - 20, content_height)
        
        shop_list = SHOP_TEMPLATES.items()
        sorted_shops = sorted(shop_list, key=lambda item: item[1]['level_required'])
        
        total_content_height = len(sorted_shops) * 90
        
        self.shop_scroll_y = min(0, self.shop_scroll_y)
        max_scroll = content_height - total_content_height
        if max_scroll > 0: 
            max_scroll = 0
        self.shop_scroll_y = max(self.shop_scroll_y, max_scroll)

        self.screen.set_clip(content_rect)

        y_offset = menu_y + 70 + self.shop_scroll_y
        
        for shop_type, template in sorted_shops:
            locked = self.level < template["level_required"]
            
            card_rect = pygame.Rect(menu_x + 20, y_offset, menu_width - 40, 80)
            color = GRAY if locked else (220, 220, 220)
            pygame.draw.rect(self.screen, color, card_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, card_rect, 2, border_radius=10)
            
            Shop.draw_preview(self.screen, menu_x + 30, y_offset + 15, shop_type) 
            
            text_x = menu_x + 95 
            
            name_text = self.font_medium.render(template["name"], True, BLACK)
            self.screen.blit(name_text, (text_x, y_offset + 10))
            
            cost_text = self.font_small.render(f"Cost: {template['cost']} coins", True, BLACK)
            self.screen.blit(cost_text, (text_x, y_offset + 40))
            
            income_text = self.font_small.render(f"Income: {template['income']}/cycle", True, BLACK)
            self.screen.blit(income_text, (text_x, y_offset + 60))
            
            if locked:
                lock_text = self.font_small.render(f"Unlock at Lv.{template['level_required']}", True, RED)
                self.screen.blit(lock_text, (menu_x + menu_width - 120, y_offset + 30))
            
            y_offset += 90
        
        self.screen.set_clip(None)

    def draw_decorate_menu(self):
        menu_width = 400
        menu_height = 450
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 80
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, DARK_GRAY, (menu_x + 5, menu_y + 5, menu_width, menu_height), border_radius=15)
        pygame.draw.rect(self.screen, WHITE, menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3, border_radius=15)
        title = self.font_large.render("Decorate", True, BLACK)
        self.screen.blit(title, (menu_x + 20, menu_y + 20))
        self.draw_close_button(menu_rect)
        content_height = menu_height - 90
        content_rect = pygame.Rect(menu_x + 10, menu_y + 70, menu_width - 20, content_height)
        total_content_height = len(DecorationType) * 90
        self.decorate_scroll_y = min(0, self.decorate_scroll_y)
        max_scroll = content_height - total_content_height
        if max_scroll > 0: 
            max_scroll = 0
        self.decorate_scroll_y = max(self.decorate_scroll_y, max_scroll)
        self.screen.set_clip(content_rect)
        y_offset = menu_y + 70 + self.decorate_scroll_y
        for dec_type in DecorationType:
            template = DECORATION_TEMPLATES[dec_type]
            card_rect = pygame.Rect(menu_x + 20, y_offset, menu_width - 40, 80)
            pygame.draw.rect(self.screen, LIGHT_GRAY, card_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, card_rect, 2, border_radius=10)
            Decoration.draw_preview(self.screen, menu_x + 30, y_offset + 20, dec_type)
            text_x = menu_x + 95
            name_text = self.font_medium.render(template["name"], True, BLACK)
            self.screen.blit(name_text, (text_x, y_offset + 15))
            cost_text = self.font_small.render(f"Cost: {template['cost']} coins", True, BLACK)
            self.screen.blit(cost_text, (text_x, y_offset + 45))
            y_offset += 90
        self.screen.set_clip(None)

    def draw_quest_menu(self):
        menu_width = 450
        menu_height = 400
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 100
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        
        pygame.draw.rect(self.screen, DARK_GRAY, (menu_x + 5, menu_y + 5, menu_width, menu_height), border_radius=15)
        pygame.draw.rect(self.screen, WHITE, menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3, border_radius=15)
        
        title = self.font_large.render("Quests", True, BLACK)
        self.screen.blit(title, (menu_x + 20, menu_y + 20))
        
        self.draw_close_button(menu_rect)
        
        content_height = menu_height - 90
        content_rect = pygame.Rect(menu_x + 10, menu_y + 70, menu_width - 20, content_height)
        
        total_content_height = len(self.quests) * 90
        
        self.quest_scroll_y = min(0, self.quest_scroll_y)
        max_scroll = content_height - total_content_height
        if max_scroll > 0: 
            max_scroll = 0
        self.quest_scroll_y = max(self.quest_scroll_y, max_scroll)
        
        self.screen.set_clip(content_rect)

        y_offset = menu_y + 70 + self.quest_scroll_y
        
        for quest in self.quests:
            card_color = GREEN if quest.completed else LIGHT_GRAY
            card_rect = pygame.Rect(menu_x + 20, y_offset, menu_width - 40, 80)
            pygame.draw.rect(self.screen, card_color, card_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, card_rect, 2, border_radius=10)
            
            desc_text = self.font_medium.render(quest.description, True, BLACK)
            self.screen.blit(desc_text, (menu_x + 30, y_offset + 10))
            progress_percent = min((quest.progress / quest.target) * 100, 100)
            progress_width = int((menu_width - 80) * progress_percent / 100)
            pygame.draw.rect(self.screen, DARK_GRAY, (menu_x + 30, y_offset + 40, menu_width - 80, 15), border_radius=7)
            pygame.draw.rect(self.screen, BLUE, (menu_x + 30, y_offset + 40, progress_width, 15), border_radius=7)
            progress_text = self.font_small.render(f"{quest.progress}/{quest.target}", True, BLACK)
            self.screen.blit(progress_text, (menu_x + 30, y_offset + 57))
            reward_text = self.font_small.render(f"Reward: {quest.reward_coins} coins, {quest.reward_xp} XP", True, BLACK)
            self.screen.blit(reward_text, (menu_x + 200, y_offset + 57))
            
            y_offset += 90
        
        self.screen.set_clip(None)

    def draw_mall_info(self):
        menu_width = 400
        menu_height = 300
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 150
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, DARK_GRAY, (menu_x + 5, menu_y + 5, menu_width, menu_height), border_radius=15)
        pygame.draw.rect(self.screen, WHITE, menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3, border_radius=15)
        title = self.font_large.render("Mall Information", True, BLACK)
        self.screen.blit(title, (menu_x + 20, menu_y + 20))
        self.draw_close_button(menu_rect)
        y_offset = menu_y + 70
        slots_x, slots_y = self.mall.get_shop_slots()
        size_text = self.font_medium.render(f"Mall Size: {self.mall.width} x {self.mall.height} px", True, BLACK)
        self.screen.blit(size_text, (menu_x + 30, y_offset))
        y_offset += 35
        tiles_text = self.font_medium.render(f"Total Tiles: {self.mall.width // TILE_SIZE} x {self.mall.height // TILE_SIZE}", True, BLACK)
        self.screen.blit(tiles_text, (menu_x + 30, y_offset))
        y_offset += 35
        slots_text = self.font_medium.render(f"Shop Slots: {slots_x} x {slots_y} ({slots_x * slots_y} total)", True, BLACK)
        self.screen.blit(slots_text, (menu_x + 30, y_offset))
        y_offset += 35
        shops_text = self.font_medium.render(f"Shops Built: {len(self.shops)}", True, BLACK)
        self.screen.blit(shops_text, (menu_x + 30, y_offset))
        y_offset += 35
        if self.mall.can_expand():
            cost = self.mall.get_expand_cost()
            expand_text = self.font_medium.render(f"Next Expansion Cost: {cost}", True, BLUE)
            self.screen.blit(expand_text, (menu_x + 30, y_offset))
        else:
            max_text = self.font_medium.render("Mall at Maximum Size!", True, GREEN)
            self.screen.blit(max_text, (menu_x + 30, y_offset))
        
    def draw_expand_menu(self):
        menu_width = 400
        menu_height = 300
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 150
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        
        pygame.draw.rect(self.screen, DARK_GRAY, (menu_x + 5, menu_y + 5, menu_width, menu_height), border_radius=15)
        pygame.draw.rect(self.screen, WHITE, menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3, border_radius=15)
        
        title = self.font_large.render("Expand Mall", True, BLACK)
        self.screen.blit(title, (menu_x + 20, menu_y + 20))
        self.draw_close_button(menu_rect)
        
        y_offset = menu_y + 80
        
        if self.mall.can_expand():
            slots_x, slots_y = self.mall.get_shop_slots()
            next_slots_str = self.mall.get_next_expansion_slots()
            cost = self.mall.get_expand_cost()
            
            current_text = self.font_medium.render(f"Current Size: {slots_x}x{slots_y} Slots", True, BLACK)
            self.screen.blit(current_text, (menu_x + 30, y_offset))
            y_offset += 40
            
            next_text = self.font_medium.render(f"Upgrade to: {next_slots_str} Slots", True, GREEN)
            self.screen.blit(next_text, (menu_x + 30, y_offset))
            y_offset += 60
            
            cost_text = self.font_large.render(f"Cost: {cost} Coins", True, BLACK)
            cost_rect = cost_text.get_rect(center=(menu_rect.centerx, y_offset))
            self.screen.blit(cost_text, cost_rect)
            y_offset += 50
            
            color = BLUE if self.coins >= cost else DARK_GRAY
            self.draw_button("Upgrade", menu_rect.centerx - 100, y_offset, 200, 40, color)
            
        else:
            max_text = self.font_medium.render("Mall is at Maximum Size!", True, RED)
            max_rect = max_text.get_rect(center=(menu_rect.centerx, menu_rect.centery))
            self.screen.blit(max_text, max_rect)


    def handle_click(self, pos):
        x, y = pos
        
        any_menu_open = self.show_shop_menu or self.show_decorate_menu or self.show_quest_menu or self.show_mall_info or self.show_expand_menu or self.show_save_menu
        if any_menu_open and self.close_button_rect.collidepoint(pos):
            self.sound_manager.play_sfx('click')
            self.show_shop_menu = False
            self.show_decorate_menu = False
            self.show_quest_menu = False
            self.show_mall_info = False
            self.show_expand_menu = False
            self.show_save_menu = False
            return 

        if 650 <= x <= 730 and 10 <= y <= 50:
            self.sound_manager.play_sfx('click')
            self.show_shop_menu = not self.show_shop_menu
            self.show_decorate_menu = False; self.show_quest_menu = False; self.show_mall_info = False; self.show_expand_menu = False; self.show_save_menu = False
            self.shop_scroll_y = 0 
        elif 740 <= x <= 820 and 10 <= y <= 50:
            self.sound_manager.play_sfx('click')
            self.show_quest_menu = not self.show_quest_menu
            self.show_shop_menu = False; self.show_decorate_menu = False; self.show_mall_info = False; self.show_expand_menu = False; self.show_save_menu = False
            self.quest_scroll_y = 0
        elif 830 <= x <= 900 and 10 <= y <= 50:
            self.sound_manager.play_sfx('click')
            self.show_decorate_menu = not self.show_decorate_menu
            self.show_shop_menu = False; self.show_quest_menu = False; self.show_mall_info = False; self.show_expand_menu = False; self.show_save_menu = False
            self.decorate_scroll_y = 0 
        elif 910 <= x <= 980 and 10 <= y <= 50:
            self.sound_manager.play_sfx('click')
            self.show_mall_info = not self.show_mall_info
            self.show_shop_menu = False; self.show_decorate_menu = False; self.show_quest_menu = False; self.show_expand_menu = False; self.show_save_menu = False
        elif 990 <= x <= 1080 and 10 <= y <= 50:
            self.sound_manager.play_sfx('click')
            self.show_expand_menu = not self.show_expand_menu
            self.show_shop_menu = False; self.show_decorate_menu = False; self.show_quest_menu = False; self.show_mall_info = False; self.show_save_menu = False
        elif 1090 <= x <= 1190 and 10 <= y <= 50:
            self.sound_manager.play_sfx('click')
            self.show_save_menu = not self.show_save_menu
            self.show_shop_menu = False; self.show_decorate_menu = False; self.show_quest_menu = False; self.show_mall_info = False; self.show_expand_menu = False
        
        if self.show_save_menu:
            menu_width = 350
            menu_x = (SCREEN_WIDTH - menu_width) // 2
            menu_y = 200
            save_btn_rect = pygame.Rect(menu_x + menu_width // 2 - 100, menu_y + 120, 200, 50)
            if save_btn_rect.collidepoint(pos):
                self.save_game_data()
                self.show_save_menu = False
                return
        
        if self.show_shop_menu:
            menu_x = (SCREEN_WIDTH - 400) // 2
            menu_y = 80
            y_offset = menu_y + 70 + self.shop_scroll_y 
            shop_list = SHOP_TEMPLATES.items()
            sorted_shops = sorted(shop_list, key=lambda item: item[1]['level_required'])
            
            for shop_type, template in sorted_shops:
                card_rect = pygame.Rect(menu_x + 20, y_offset, 360, 80)
                content_rect = pygame.Rect(menu_x + 10, menu_y + 70, 380, 450 - 90)
                if card_rect.collidepoint(pos) and content_rect.collidepoint(pos):
                    if self.level >= template["level_required"] and self.coins >= template["cost"]:
                        self.sound_manager.play_sfx('click')
                        self.selected_shop_type = shop_type
                        self.placing_shop = True
                        self.placing_decoration = False
                        self.show_shop_menu = False
                    else:
                        self.sound_manager.play_sfx('error')
                    return
                y_offset += 90

        if self.show_decorate_menu:
            menu_x = (SCREEN_WIDTH - 400) // 2
            menu_y = 80
            y_offset = menu_y + 70 + self.decorate_scroll_y 
            for dec_type in DecorationType:
                template = DECORATION_TEMPLATES[dec_type]
                card_rect = pygame.Rect(menu_x + 20, y_offset, 360, 80)
                content_rect = pygame.Rect(menu_x + 10, menu_y + 70, 380, 450 - 90)
                if card_rect.collidepoint(pos) and content_rect.collidepoint(pos):
                    if self.coins >= template["cost"]:
                        self.sound_manager.play_sfx('click')
                        self.selected_decoration_type = dec_type
                        self.placing_decoration = True
                        self.placing_shop = False
                        self.show_decorate_menu = False
                    else:
                        self.sound_manager.play_sfx('error')
                    return
                y_offset += 90

        if self.show_expand_menu:
            menu_width = 400
            menu_x = (SCREEN_WIDTH - menu_width) // 2
            menu_y = 150
            menu_center_x = menu_x + (menu_width // 2)
            button_y = menu_y + 80 + 40 + 60 + 50
            
            upgrade_btn_rect = pygame.Rect(menu_center_x - 100, button_y, 200, 40)
            
            if upgrade_btn_rect.collidepoint(pos):
                if self.mall.can_expand():
                    cost = self.mall.get_expand_cost()
                    if self.coins >= cost:
                        self.sound_manager.play_sfx('build')
                        self.coins -= cost
                        self.mall.expand()
                        self.add_xp(100)
                        for quest in self.quests:
                            if "expand" in quest.description.lower() and not quest.completed:
                                quest.update_progress(1)
                                if quest.completed:
                                    self.sound_manager.play_sfx('quest_complete')
                        self.show_expand_menu = False
                    else:
                        self.sound_manager.play_sfx('error')
                return

        mall_y_start = 170
        if y > mall_y_start + BORDER_THICKNESS:
            internal_x = x - self.camera_x - BORDER_THICKNESS
            internal_y = y - self.camera_y - mall_y_start - BORDER_THICKNESS
            
            if self.placing_shop and self.selected_shop_type:
                self.place_item_on_grid(internal_x, internal_y)
            elif self.placing_decoration and self.selected_decoration_type:
                self.place_item_on_grid(internal_x, internal_y)


    def is_grid_occupied(self, grid_x, grid_y):
        item_rect = pygame.Rect(grid_x, grid_y, SHOP_GRID_SIZE, SHOP_GRID_SIZE)
        for shop in self.shops:
            if item_rect.colliderect(pygame.Rect(shop.x, shop.y, shop.width, shop.height)):
                return True
        return False

    def place_item_on_grid(self, internal_x, internal_y):
        grid_x = (internal_x // SHOP_GRID_SIZE) * SHOP_GRID_SIZE
        grid_y = (internal_y // SHOP_GRID_SIZE) * SHOP_GRID_SIZE
        if 0 <= grid_x <= self.mall.width - SHOP_GRID_SIZE and \
           0 <= grid_y <= self.mall.height - SHOP_GRID_SIZE:
            if not self.is_grid_occupied(grid_x, grid_y):
                if self.placing_shop:
                    template = SHOP_TEMPLATES[self.selected_shop_type]
                    if self.coins >= template["cost"]:
                        self.sound_manager.play_sfx('build')
                        new_shop = Shop(self.selected_shop_type, grid_x, grid_y)
                        self.shops.append(new_shop)
                        new_shop.start_production()
                        self.coins -= template["cost"]
                        self.add_xp(20)
                        for quest in self.quests:
                            if "build" in quest.description.lower() and not quest.completed:
                                quest.update_progress(1)
                                if quest.completed:
                                    self.sound_manager.play_sfx('quest_complete')
                
                elif self.placing_decoration:
                    template = DECORATION_TEMPLATES[self.selected_decoration_type]
                    if self.coins >= template["cost"]:
                        self.sound_manager.play_sfx('build')
                        dec_x = grid_x + (SHOP_GRID_SIZE // 2) - 20 
                        dec_y = grid_y + (SHOP_GRID_SIZE // 2) - 20
                        new_dec = Decoration(self.selected_decoration_type, dec_x, dec_y)
                        self.decorations.append(new_dec)
                        self.coins -= template["cost"]
                        self.add_xp(5)
                        for quest in self.quests:
                            if "decorations" in quest.description.lower() and not quest.completed:
                                quest.update_progress(1)
                                if quest.completed:
                                    self.sound_manager.play_sfx('quest_complete')

        self.placing_shop = False
        self.placing_decoration = False
        self.selected_shop_type = None
        self.selected_decoration_type = None


    def draw(self):
        self.screen.fill(LIGHT_GRAY)
        self.draw_road_and_environment()
        self.draw_mall_building()
        
        mall_y_start = 170
        internal_offset_x = self.camera_x + BORDER_THICKNESS
        internal_offset_y = self.camera_y + mall_y_start + BORDER_THICKNESS
        
        for decoration in self.decorations:
            decoration.draw(self.screen, internal_offset_x, internal_offset_y)
        for shop in self.shops:
            shop.draw(self.screen, internal_offset_x, internal_offset_y)
        
        for customer in self.customers:
            in_mall_states = [ CustomerState.SHOPPING, CustomerState.EXITING_MALL ]
            if customer.state in in_mall_states:
                customer.draw(self.screen, internal_offset_x, internal_offset_y)
            else:
                customer.draw(self.screen, self.camera_x, self.camera_y)
        
        mouse_pos = pygame.mouse.get_pos()
        if self.placing_shop or self.placing_decoration:
            mall_y_start = 170
            if mouse_pos[1] > mall_y_start + BORDER_THICKNESS:
                internal_x = mouse_pos[0] - self.camera_x - BORDER_THICKNESS
                internal_y = mouse_pos[1] - self.camera_y - mall_y_start - BORDER_THICKNESS
                grid_x = (internal_x // SHOP_GRID_SIZE) * SHOP_GRID_SIZE
                grid_y = (internal_y // SHOP_GRID_SIZE) * SHOP_GRID_SIZE
                draw_x = grid_x + internal_offset_x
                draw_y = grid_y + internal_offset_y
                is_valid = True
                if not (0 <= grid_x <= self.mall.width - SHOP_GRID_SIZE and \
                        0 <= grid_y <= self.mall.height - SHOP_GRID_SIZE):
                    is_valid = False
                if self.is_grid_occupied(grid_x, grid_y):
                    is_valid = False
                if self.placing_shop:
                    ghost_color = (0, 255, 0, 100) if is_valid else (255, 0, 0, 100)
                    ghost_surf = pygame.Surface((SHOP_GRID_SIZE, SHOP_GRID_SIZE), pygame.SRCALPHA)
                    ghost_surf.fill(ghost_color)
                    self.screen.blit(ghost_surf, (draw_x, draw_y))
                    pygame.draw.rect(self.screen, WHITE, (draw_x, draw_y, SHOP_GRID_SIZE, SHOP_GRID_SIZE), 2)
                elif self.placing_decoration:
                    dec_draw_x = draw_x + (SHOP_GRID_SIZE // 2) - 20
                    dec_draw_y = draw_y + (SHOP_GRID_SIZE // 2) - 20
                    ghost_color = (0, 255, 0, 100) if is_valid else (255, 0, 0, 100)
                    ghost_surf = pygame.Surface((SHOP_GRID_SIZE, SHOP_GRID_SIZE), pygame.SRCALPHA)
                    ghost_surf.fill(ghost_color)
                    self.screen.blit(ghost_surf, (draw_x, draw_y))
                    Decoration.draw_preview(self.screen, dec_draw_x, dec_draw_y, self.selected_decoration_type)

        self.screen.set_clip(None) 
        self.draw_ui()
        
        customer_count_text = self.font_small.render(f"Customers: {len(self.customers)}", True, BLACK)
        self.screen.blit(customer_count_text, (10, SCREEN_HEIGHT - 25))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game_data()
                    self.running = False
                
                elif event.type == pygame.MOUSEWHEEL:
                    if self.show_shop_menu:
                        self.shop_scroll_y += event.y * 20 
                    elif self.show_decorate_menu:
                        self.decorate_scroll_y += event.y * 20
                    elif self.show_quest_menu:
                        self.quest_scroll_y += event.y * 20
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        self.handle_click(event.pos)
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.camera_x = min(self.camera_x + 50, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.camera_x = max(self.camera_x - 50, -(self.mall.width + BORDER_THICKNESS*2 - SCREEN_WIDTH))
                    elif event.key == pygame.K_UP:
                        self.camera_y = min(self.camera_y + 50, 0)
                    elif event.key == pygame.K_DOWN:
                        self.camera_y = max(self.camera_y - 50, -(self.mall.height + BORDER_THICKNESS*2 - (SCREEN_HEIGHT - 170)))
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    sound_manager = SoundManager()
    sound_manager.play_bgm("bgm_menu.mp3")

    main_menu = MainMenu(screen, sound_manager)
    menu_result, slot = main_menu.run()

    if menu_result == 'NEW_GAME':
        game = Game(save_slot=slot, load_from_save=False)
        game.run()
    elif menu_result == 'LOAD_GAME':
        game = Game(save_slot=slot, load_from_save=True)
        game.run()