import pygame
import sys
import random
from pygame.locals import *

pygame.init()

BACKGROUND = (28, 40, 56)
PLAYER1_COLOR = (66, 135, 245)
PLAYER2_COLOR = (245, 66, 66)
DICE_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (52, 152, 219)
BUTTON_HOVER = (41, 128, 185)
PANEL_COLOR = (40, 55, 75)
HIDDEN_COLOR = (60, 60, 80)
HIDDEN_DOT_COLOR = (100, 100, 100)

class Die:
    def __init__(self):
        self.value = random.randint(1, 6)
        self.held = False
    
    def roll(self):
        if not self.held:
            self.value = random.randint(1, 6)

class DiceSet:
    def __init__(self, num_dice=5):
        self.dice = [Die() for _ in range(num_dice)]
    
    def roll_all(self):
        for die in self.dice:
            die.roll()
    
    def get_values(self):
        return [die.value for die in self.dice]
    
    def count_value(self, value):
        return sum(1 for die in self.dice if die.value == value)
    
    def remove_die(self):
        if self.dice:
            return self.dice.pop()
        return None
    
    def size(self):
        return len(self.dice)

class LiarsDiceGame:
    def __init__(self):
        self.players = [DiceSet(), DiceSet()]
        self.current_player = 0
        self.current_bid = None
        self.round_active = True
        self.message = ""
        self.game_over = False
        self.winner = None
        self.all_dice_revealed = False
        self.challenge_result = ""
    
    def roll_all_dice(self):
        for player in self.players:
            player.roll_all()
        self.all_dice_revealed = False
        self.challenge_result = ""
    
    def make_bid(self, player, quantity, face_value):
        if player != self.current_player or not self.round_active:
            return False
        
        if self.current_bid:
            q, v = self.current_bid
            if quantity < q or (quantity == q and face_value <= v):
                return False
        
        self.current_bid = (quantity, face_value)
        self.current_player = 1 - self.current_player
        self.message = f"Player {self.current_player + 1}'s turn"
        self.challenge_result = ""
        return True
    
    def challenge(self, player):
        if player != self.current_player or not self.round_active or not self.current_bid:
            return False
        
        self.all_dice_revealed = True
        
        total_count = 0
        for p in self.players:
            total_count += p.count_value(self.current_bid[1])
            if self.current_bid[1] != 1:
                total_count += p.count_value(1)
        
        bid_quantity, bid_value = self.current_bid
        
        if total_count >= bid_quantity:
            loser = player
            self.challenge_result = f"Challenge failed! Total {total_count} {bid_value}s"
            self.message = f"Player {loser + 1} loses a die"
        else:
            loser = 1 - player
            self.challenge_result = f"Challenge succeeded! Only {total_count} {bid_value}s"
            self.message = f"Player {loser + 1} loses a die"
        
        self.players[loser].remove_die()
        
        self.current_bid = None
        self.round_active = False
        
        if self.players[loser].size() == 0:
            winner = 1 - loser
            self.winner = winner
            self.game_over = True
            self.message = f"Player {winner + 1} wins!"
            self.challenge_result = ""
        
        return True
    
    def start_new_round(self):
        if self.game_over:
            self.__init__()
        else:
            self.roll_all_dice()
            self.current_player = random.randint(0, 1)
            self.current_bid = None
            self.round_active = True
            self.all_dice_revealed = False
            self.message = f"Player {self.current_player + 1}'s turn"
            self.challenge_result = ""
    
    def get_player_view(self, player_perspective):
        state = {
            'current_player': self.current_player,
            'current_bid': self.current_bid,
            'player_counts': [p.size() for p in self.players],
            'message': self.message,
            'round_active': self.round_active,
            'game_over': self.game_over,
            'winner': self.winner,
            'all_dice_revealed': self.all_dice_revealed,
            'challenge_result': self.challenge_result
        }
        
        state['player1_dice'] = self.players[0].get_values()
        state['player2_dice'] = self.players[1].get_values()
        state['player1_count'] = self.players[0].size()
        state['player2_count'] = self.players[1].size()
        
        if self.all_dice_revealed or self.game_over:
            state['visible_player1_dice'] = state['player1_dice']
            state['visible_player2_dice'] = state['player2_dice']
        else:
            if player_perspective == 0:
                state['visible_player1_dice'] = state['player1_dice']
                state['visible_player2_dice'] = ['?' for _ in range(state['player2_count'])]
            else:
                state['visible_player1_dice'] = ['?' for _ in range(state['player1_count'])]
                state['visible_player2_dice'] = state['player2_dice']
        
        state['perspective'] = player_perspective
        
        return state

class DiceGUI:
    def __init__(self):
        screen_info = pygame.display.Info()
        resolution = (screen_info.current_w, screen_info.current_h)
        if resolution[0] < 1920 or resolution[1] < 1080:
            resolution = (1920, 1080)
        
        self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
        pygame.display.set_caption("Liar's Dice")
        self.clock = pygame.time.Clock()
        
        self.resolution = resolution
        self.screen_width = resolution[0]
        self.screen_height = resolution[1]
        
        self.dice_size = 60
        self.font_size_title = 40
        self.font_size_large = 28
        self.font_size_medium = 20
        self.font_size_small = 16
        
        self.title_font = pygame.font.SysFont('Arial', self.font_size_title, bold=True)
        self.font = pygame.font.SysFont('Arial', self.font_size_large)
        self.small_font = pygame.font.SysFont('Arial', self.font_size_medium)
        self.tiny_font = pygame.font.SysFont('Arial', self.font_size_small)
        
        self.game = LiarsDiceGame()
        
        self.dice_faces = {}
        self.hidden_dice_face = None
        self.create_dice_faces()
        
        self.selected_quantity = 1
        self.selected_face = 2
        self.max_quantity = 10
        
        self.current_perspective = 0
        self.perspective_locked = False
        
        center_x = self.screen_width // 2
        
        self.button_width = 180
        self.button_height = 45
        
        self.bid_button = pygame.Rect(center_x - 200, self.screen_height - 120, self.button_width, self.button_height)
        self.challenge_button = pygame.Rect(center_x + 20, self.screen_height - 120, self.button_width, self.button_height)
        self.new_round_button = pygame.Rect(center_x - self.button_width // 2, self.screen_height - 120, self.button_width, self.button_height)
        self.restart_button = pygame.Rect(center_x - self.button_width // 2, self.screen_height - 60, self.button_width, self.button_height)
        
        self.switch_view_button = pygame.Rect(self.screen_width - 200, 20, 180, self.button_height)
        
        self.face_buttons = []
        for i in range(1, 7):
            btn_x = center_x - 140 + (i-1) * 50
            btn = pygame.Rect(btn_x, self.screen_height - 220, 45, 45)
            self.face_buttons.append(btn)
        
        self.quantity_up = pygame.Rect(center_x + 100, self.screen_height - 290, 45, 40)
        self.quantity_down = pygame.Rect(center_x - 145, self.screen_height - 290, 45, 40)
        
        self.turn_reminder = pygame.Rect(50, self.screen_height - 90, 300, self.button_height)
        
        self.setup_panels()
    
    def setup_panels(self):
        center_x = self.screen_width // 2
        
        self.player_panel_width = 600
        self.player_panel_height = 180
        
        self.player1_panel = pygame.Rect(50, 100, self.player_panel_width, self.player_panel_height)
        self.player2_panel = pygame.Rect(50, 300, self.player_panel_width, self.player_panel_height)
        
        self.bid_panel = pygame.Rect(center_x - 300, 250, 600, 70)
        
        self.message_panel = pygame.Rect(center_x - 300, 330, 600, 40)
        
        self.challenge_panel = pygame.Rect(center_x - 300, 380, 600, 40)
        
        self.bid_control_panel = pygame.Rect(center_x - 250, self.screen_height - 350, 500, 180)
        
        self.instructions_panel = pygame.Rect(self.screen_width - 380, 100, 350, 250)
        
        self.winner_panel = pygame.Rect(center_x - 300, 430, 600, 80)
    
    def create_dice_faces(self):
        for value in range(1, 7):
            surf = pygame.Surface((self.dice_size, self.dice_size), pygame.SRCALPHA)
            pygame.draw.rect(surf, DICE_COLOR, (0, 0, self.dice_size, self.dice_size), border_radius=8)
            pygame.draw.rect(surf, (0, 0, 0), (0, 0, self.dice_size, self.dice_size), 2, border_radius=8)
            
            dot_radius = self.dice_size // 12
            
            positions = {
                1: [(self.dice_size // 2, self.dice_size // 2)],
                2: [(self.dice_size // 4, self.dice_size // 4), (3*self.dice_size // 4, 3*self.dice_size // 4)],
                3: [(self.dice_size // 4, self.dice_size // 4), (self.dice_size // 2, self.dice_size // 2), (3*self.dice_size // 4, 3*self.dice_size // 4)],
                4: [(self.dice_size // 4, self.dice_size // 4), (3*self.dice_size // 4, self.dice_size // 4), 
                    (self.dice_size // 4, 3*self.dice_size // 4), (3*self.dice_size // 4, 3*self.dice_size // 4)],
                5: [(self.dice_size // 4, self.dice_size // 4), (3*self.dice_size // 4, self.dice_size // 4), 
                    (self.dice_size // 2, self.dice_size // 2), 
                    (self.dice_size // 4, 3*self.dice_size // 4), (3*self.dice_size // 4, 3*self.dice_size // 4)],
                6: [(self.dice_size // 4, self.dice_size // 4), (3*self.dice_size // 4, self.dice_size // 4), 
                    (self.dice_size // 4, self.dice_size // 2), (3*self.dice_size // 4, self.dice_size // 2),
                    (self.dice_size // 4, 3*self.dice_size // 4), (3*self.dice_size // 4, 3*self.dice_size // 4)]
            }
            
            for pos in positions[value]:
                pygame.draw.circle(surf, (0, 0, 0), pos, dot_radius)
            
            self.dice_faces[value] = surf
        
        self.hidden_dice_face = pygame.Surface((self.dice_size, self.dice_size), pygame.SRCALPHA)
        pygame.draw.rect(self.hidden_dice_face, HIDDEN_COLOR, (0, 0, self.dice_size, self.dice_size), border_radius=8)
        pygame.draw.rect(self.hidden_dice_face, (100, 100, 100), (0, 0, self.dice_size, self.dice_size), 2, border_radius=8)
        
        dot_radius = self.dice_size // 12
        for i in range(3):
            for j in range(3):
                if not (i == 1 and j == 1):
                    x = self.dice_size // 4 + i * (self.dice_size // 4)
                    y = self.dice_size // 4 + j * (self.dice_size // 4)
                    pygame.draw.circle(self.hidden_dice_face, HIDDEN_DOT_COLOR, (x, y), dot_radius)
    
    def draw_button(self, rect, text, hover=False, color=None, font=None, border=True):
        if font is None:
            font = self.font
            
        if color is None:
            color = BUTTON_HOVER if hover else BUTTON_COLOR
            
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        if border:
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=5)
        
        text_surf = font.render(text, True, TEXT_COLOR)
        
        if text_surf.get_width() > rect.width - 20:
            smaller_font = pygame.font.SysFont('Arial', font.get_height() - 4)
            text_surf = smaller_font.render(text, True, TEXT_COLOR)
        
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def draw_dice(self, dice_values, x, y, player_num, is_hidden=False):
        color = PLAYER1_COLOR if player_num == 0 else PLAYER2_COLOR
        
        dice_count = len(dice_values)
        group_width = dice_count * (self.dice_size + 15) + 20
        group_height = self.dice_size + 40
        
        if is_hidden:
            pygame.draw.rect(self.screen, (40, 40, 60), (x-10, y-10, group_width, group_height), border_radius=8)
            pygame.draw.rect(self.screen, (80, 80, 100), (x-10, y-10, group_width, group_height), 2, border_radius=8)
        else:
            pygame.draw.rect(self.screen, color, (x-10, y-10, group_width, group_height), border_radius=8)
        
        for i, value in enumerate(dice_values):
            dice_x = x + i * (self.dice_size + 15)
            
            if value == '?':
                self.screen.blit(self.hidden_dice_face, (dice_x, y))
            else:
                self.screen.blit(self.dice_faces[value], (dice_x, y))
            
            if value != '?':
                num_text = self.tiny_font.render(str(i+1), True, (0, 0, 0))
                num_rect = num_text.get_rect(center=(dice_x + self.dice_size//2, y + self.dice_size + 15))
                self.screen.blit(num_text, num_rect)
    
    def draw_panel(self, rect, title=None, title_color=TEXT_COLOR):
        pygame.draw.rect(self.screen, PANEL_COLOR, rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 120), rect, 2, border_radius=10)
        
        if title:
            title_surf = self.small_font.render(title, True, title_color)
            title_x = rect.x + 15
            title_y = rect.y + 8
            self.screen.blit(title_surf, (title_x, title_y))
    
    def draw_player_panel(self, panel_rect, player_num, dice_values, dice_count, is_hidden=False, is_current_turn=False):
        player_title = f"Player {player_num + 1} - {dice_count} dice"
        self.draw_panel(panel_rect, player_title, PLAYER1_COLOR if player_num == 0 else PLAYER2_COLOR)
        
        if is_current_turn:
            turn_text = self.small_font.render("TURN", True, (255, 215, 0))
            self.screen.blit(turn_text, (panel_rect.x + panel_rect.width - 60, panel_rect.y + 10))
        
        dice_x = panel_rect.x + 20
        dice_y = panel_rect.y + 50
        
        self.draw_dice(dice_values, dice_x, dice_y, player_num, is_hidden)
    
    def draw_bid_controls(self, center_x):
        self.draw_panel(self.bid_control_panel, f"Player {self.current_perspective + 1}'s Bid")
        
        q_text = self.font.render(f"Quantity: {self.selected_quantity}", True, TEXT_COLOR)
        q_x = center_x - q_text.get_width() // 2
        q_y = self.bid_control_panel.y + 45
        self.screen.blit(q_text, (q_x, q_y))
        
        f_text = self.font.render("Face Value:", True, TEXT_COLOR)
        f_x = center_x - f_text.get_width() // 2
        f_y = self.bid_control_panel.y + 95
        self.screen.blit(f_text, (f_x, f_y))
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        state = self.game.get_player_view(self.current_perspective)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                if self.switch_view_button.collidepoint(mouse_pos) and not self.perspective_locked:
                    self.current_perspective = 1 - self.current_perspective
                
                if self.quantity_up.collidepoint(mouse_pos) and state['round_active'] and self.current_perspective == state['current_player']:
                    self.selected_quantity = min(self.max_quantity, self.selected_quantity + 1)
                
                if self.quantity_down.collidepoint(mouse_pos) and state['round_active'] and self.current_perspective == state['current_player']:
                    self.selected_quantity = max(1, self.selected_quantity - 1)
                
                if state['round_active'] and self.current_perspective == state['current_player']:
                    for i, btn in enumerate(self.face_buttons):
                        if btn.collidepoint(mouse_pos):
                            self.selected_face = i + 1
                
                if self.bid_button.collidepoint(mouse_pos) and state['round_active'] and self.current_perspective == state['current_player']:
                    if self.game.make_bid(state['current_player'], self.selected_quantity, self.selected_face):
                        self.selected_quantity = max(1, self.selected_quantity)
                        self.current_perspective = 1 - self.current_perspective
                
                if self.challenge_button.collidepoint(mouse_pos) and state['round_active'] and self.current_perspective == state['current_player']:
                    self.game.challenge(state['current_player'])
                    self.perspective_locked = True
                
                if self.new_round_button.collidepoint(mouse_pos) and not state['round_active'] and not state['game_over']:
                    self.game.start_new_round()
                    self.perspective_locked = False
                    self.current_perspective = self.game.current_player
                
                if self.restart_button.collidepoint(mouse_pos) and state['game_over']:
                    self.game = LiarsDiceGame()
                    self.game.start_new_round()
                    self.perspective_locked = False
                    self.current_perspective = 0
    
    def draw(self):
        self.screen.fill(BACKGROUND)
        state = self.game.get_player_view(self.current_perspective)
        center_x = self.screen_width // 2
        
        title = self.title_font.render("LIAR'S DICE", True, (255, 215, 0))
        self.screen.blit(title, (center_x - title.get_width() // 2, 20))
        
        perspective_text = f"Viewing: Player {self.current_perspective + 1}"
        perspective_surf = self.small_font.render(perspective_text, True, PLAYER1_COLOR if self.current_perspective == 0 else PLAYER2_COLOR)
        self.screen.blit(perspective_surf, (50, 70))
        
        player1_is_hidden = (state['visible_player1_dice'][0] == '?') if state['visible_player1_dice'] else False
        player2_is_hidden = (state['visible_player2_dice'][0] == '?') if state['visible_player2_dice'] else False
        
        self.draw_player_panel(self.player1_panel, 0, state['visible_player1_dice'], state['player1_count'], player1_is_hidden, state['current_player'] == 0)
        self.draw_player_panel(self.player2_panel, 1, state['visible_player2_dice'], state['player2_count'], player2_is_hidden, state['current_player'] == 1)
        
        self.draw_panel(self.bid_panel, "Current Bid")
        if state['current_bid']:
            bid_text = f"{state['current_bid'][0]} x {state['current_bid'][1]}s"
        else:
            bid_text = "No bid yet"
        
        bid_surf = self.font.render(bid_text, True, TEXT_COLOR)
        if bid_surf.get_width() > self.bid_panel.width - 40:
            smaller_font = pygame.font.SysFont('Arial', self.font_size_medium)
            bid_surf = smaller_font.render(bid_text, True, TEXT_COLOR)
        
        bid_x = self.bid_panel.x + (self.bid_panel.width - bid_surf.get_width()) // 2
        bid_y = self.bid_panel.y + 40
        self.screen.blit(bid_surf, (bid_x, bid_y))
        
        self.draw_panel(self.message_panel, "Game Status")
        message = state['message']
        msg_surf = self.small_font.render(message, True, TEXT_COLOR)
        
        if msg_surf.get_width() > self.message_panel.width - 40:
            smaller_font = pygame.font.SysFont('Arial', self.font_size_small)
            msg_surf = smaller_font.render(message, True, TEXT_COLOR)
            
            if msg_surf.get_width() > self.message_panel.width - 40:
                for i in range(len(message), 0, -1):
                    truncated = message[:i] + "..."
                    test_surf = smaller_font.render(truncated, True, TEXT_COLOR)
                    if test_surf.get_width() <= self.message_panel.width - 40:
                        msg_surf = test_surf
                        break
        
        msg_x = self.message_panel.x + (self.message_panel.width - msg_surf.get_width()) // 2
        msg_y = self.message_panel.y + 22
        self.screen.blit(msg_surf, (msg_x, msg_y))
        
        if state['challenge_result']:
            self.draw_panel(self.challenge_panel, "Challenge Result")
            challenge_text = state['challenge_result']
            challenge_surf = self.small_font.render(challenge_text, True, (255, 215, 0))
            
            if challenge_surf.get_width() > self.challenge_panel.width - 40:
                smaller_font = pygame.font.SysFont('Arial', self.font_size_small)
                challenge_surf = smaller_font.render(challenge_text, True, (255, 215, 0))
                
                if challenge_surf.get_width() > self.challenge_panel.width - 40:
                    for i in range(len(challenge_text), 0, -1):
                        truncated = challenge_text[:i] + "..."
                        test_surf = smaller_font.render(truncated, True, (255, 215, 0))
                        if test_surf.get_width() <= self.challenge_panel.width - 40:
                            challenge_surf = test_surf
                            break
            
            challenge_x = self.challenge_panel.x + (self.challenge_panel.width - challenge_surf.get_width()) // 2
            challenge_y = self.challenge_panel.y + 22
            self.screen.blit(challenge_surf, (challenge_x, challenge_y))
        
        self.draw_panel(self.instructions_panel, "Instructions")
        instructions = [
            "View shows dice of Player 1",
            "or Player 2 depending on view",
            "Other player's dice are hidden",
            "During challenge: all revealed",
            "Switch view to see from other",
            "player's perspective",
            "",
            "ESC: Exit game",
            "Mouse: Click buttons"
        ]
        
        y_offset = 40
        for line in instructions:
            text = self.tiny_font.render(line, True, TEXT_COLOR)
            if text.get_width() > self.instructions_panel.width - 40:
                words = line.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    test_surf = self.tiny_font.render(test_line, True, TEXT_COLOR)
                    if test_surf.get_width() > self.instructions_panel.width - 40:
                        line_surf = self.tiny_font.render(current_line, True, TEXT_COLOR)
                        self.screen.blit(line_surf, (self.instructions_panel.x + 20, self.instructions_panel.y + y_offset))
                        y_offset += 22
                        current_line = word
                    else:
                        current_line = test_line
                if current_line:
                    line_surf = self.tiny_font.render(current_line, True, TEXT_COLOR)
                    self.screen.blit(line_surf, (self.instructions_panel.x + 20, self.instructions_panel.y + y_offset))
                    y_offset += 22
            else:
                self.screen.blit(text, (self.instructions_panel.x + 20, self.instructions_panel.y + y_offset))
                y_offset += 22
        
        mouse_pos = pygame.mouse.get_pos()
        
        if state['game_over']:
            self.draw_panel(self.winner_panel, "Game Over!", (255, 215, 0))
            
            win_text = f"Player {state['winner'] + 1} Wins!"
            win_surf = self.font.render(win_text, True, (255, 215, 0))
            win_x = self.winner_panel.x + (self.winner_panel.width - win_surf.get_width()) // 2
            win_y = self.winner_panel.y + 45
            self.screen.blit(win_surf, (win_x, win_y))
            
            self.draw_button(self.restart_button, "Play Again", self.restart_button.collidepoint(mouse_pos))
        
        elif state['round_active']:
            turn_player = state['current_player'] + 1
            if self.current_perspective == state['current_player']:
                turn_text = f"Player {turn_player}'s Turn"
                self.draw_button(self.turn_reminder, turn_text, False, (255, 215, 0), self.small_font)
            else:
                turn_text = f"Player {turn_player}'s Turn"
                self.draw_button(self.turn_reminder, turn_text, False, (100, 100, 100), self.small_font)
            
            if self.current_perspective == state['current_player']:
                self.draw_bid_controls(center_x)
                
                self.draw_button(self.quantity_down, "-", self.quantity_down.collidepoint(mouse_pos), border=False)
                self.draw_button(self.quantity_up, "+", self.quantity_up.collidepoint(mouse_pos), border=False)
                
                for i, btn in enumerate(self.face_buttons):
                    face_value = i + 1
                    is_selected = (face_value == self.selected_face)
                    color = BUTTON_HOVER if is_selected else BUTTON_COLOR
                    hover = btn.collidepoint(mouse_pos)
                    
                    if hover and not is_selected:
                        color = (100, 100, 255)
                    
                    self.draw_button(btn, str(face_value), False, color, border=False)
                
                self.draw_button(self.bid_button, "Make Bid", self.bid_button.collidepoint(mouse_pos))
                self.draw_button(self.challenge_button, "Challenge!", self.challenge_button.collidepoint(mouse_pos))
            else:
                wait_text = f"Waiting for Player {state['current_player'] + 1}"
                wait_surf = self.font.render(wait_text, True, (200, 200, 200))
                wait_x = center_x - wait_surf.get_width() // 2
                wait_y = 500
                self.screen.blit(wait_surf, (wait_x, wait_y))
        
        else:
            self.draw_button(self.new_round_button, "Start New Round", self.new_round_button.collidepoint(mouse_pos))
            
            if state['all_dice_revealed']:
                reveal_text = "All dice revealed from challenge"
                reveal_surf = self.small_font.render(reveal_text, True, (255, 215, 0))
                reveal_x = center_x - reveal_surf.get_width() // 2
                reveal_y = 500
                self.screen.blit(reveal_surf, (reveal_x, reveal_y))
        
        other_player = 2 - self.current_perspective
        switch_text = f"View Player {other_player}"
        self.draw_button(self.switch_view_button, switch_text, self.switch_view_button.collidepoint(mouse_pos) and not self.perspective_locked)
        
        if self.perspective_locked:
            lock_text = "Perspective locked during challenge"
            lock_surf = self.small_font.render(lock_text, True, (255, 100, 100))
            lock_x = center_x - lock_surf.get_width() // 2
            lock_y = 450
            self.screen.blit(lock_surf, (lock_x, lock_y))
        
        pygame.display.flip()
    
    def run(self):
        self.game.start_new_round()
        self.current_perspective = self.game.current_player
        
        running = True
        while running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    gui = DiceGUI()
    gui.run()

if __name__ == "__main__":
    main()