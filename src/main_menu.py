import pygame
import sys
from color import *
from save_manager import SaveManager

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700

class MainMenu:
    def __init__(self, screen, sound_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.save_manager = SaveManager()

        self.font_title = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.state = "MAIN"
        self.selected_slot = None

        # ✅ BGM MENU (BENAR)
        self.sound_manager.play_bgm("bgm_menu.mp3")

    def draw_button(self, text, x, y, w, h, color, hover=False):
        if hover:
            color = tuple(min(c + 30, 255) for c in color)

        pygame.draw.rect(self.screen, DARK_GRAY, (x+4, y+4, w, h), border_radius=15)
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=15)
        pygame.draw.rect(self.screen, BLACK, (x, y, w, h), 3, border_radius=15)

        text_surf = self.font_medium.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(x+w//2, y+h//2))
        self.screen.blit(text_surf, text_rect)

        return pygame.Rect(x, y, w, h)

    def draw_main_screen(self, mouse_pos):
        self.screen.fill((135, 206, 250))

        title = self.font_title.render("Happy Mall Story", True, WHITE)
        rect = title.get_rect(center=(SCREEN_WIDTH//2, 120))
        self.screen.blit(title, rect)

        cx = SCREEN_WIDTH // 2
        bw, bh = 300, 70

        buttons = {
            "new": self.draw_button("New Game", cx-bw//2, 280, bw, bh, GREEN,
                                    pygame.Rect(cx-bw//2,280,bw,bh).collidepoint(mouse_pos)),
            "load": self.draw_button("Load Game", cx-bw//2, 370, bw, bh, BLUE,
                                     pygame.Rect(cx-bw//2,370,bw,bh).collidepoint(mouse_pos)),
            "exit": self.draw_button("exit", cx-bw//2, 460, bw, bh, ORANGE,
                                         pygame.Rect(cx-bw//2,460,bw,bh).collidepoint(mouse_pos)),
        }
        return buttons

    def run(self):
        clock = pygame.time.Clock()

        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "MAIN":
                        btn = self.draw_main_screen(mouse_pos)

                        if btn["new"].collidepoint(mouse_pos):
                            self.sound_manager.play_sfx("click")
                            return "NEW_GAME", 1

                        if btn["load"].collidepoint(mouse_pos):
                            self.sound_manager.play_sfx("click")
                            return "LOAD_GAME", 1

                        if btn["exit"].collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()

            self.draw_main_screen(mouse_pos)
            pygame.display.flip()
            clock.tick(60)
