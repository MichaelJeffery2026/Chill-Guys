# run pip3 install pygame_aseprite_animation to install animation package
from pygame_aseprite_animation import *
import os, pygame
import json
import time  # time is no longer used for sleeping here

pygame.init()
clock = pygame.time.Clock()  # Create a Clock object

# Load story and save data with UTF-8 encoding
with open("story.json", "r", encoding="utf-8") as f:
    story = json.load(f)
with open("save.json", "r", encoding="utf-8") as f:
    save_data = json.load(f)
    current_scene = save_data["current_scene"]
    STATUS_VALUES = save_data["status_values"]
    is_save_present = save_data["save_present"]

GAME_STATE = "title"

# Screen Size
WIDTH = pygame.display.Info().current_w
HEIGHT = pygame.display.Info().current_h
pygame.display.set_caption("Space Odyssey")
icon = pygame.image.load("Assets/General/logo.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Font Initialization
pygame.font.init()
font = pygame.font.SysFont("Consolas", 28)
DEBUG_FONT = pygame.font.SysFont("Consolas", 15)

# Global Flags
is_typing_done = False
are_effects_applied = False
is_menu_open = False

debug_level_one = False
debug_level_two = False
debug_level_three = False

# Colors (space-themed)
BORDER_COLOR = (20, 20, 30)
STATUS_PANEL_COLOR = (10, 10, 20)
NARRATIVE_PANEL_COLOR = (30, 30, 50)
CHOICE_PANEL_COLOR = (25, 25, 40)
MENU_COLOR = (50, 50, 60)
TEXT_COLOR = (220, 220, 240)
BUTTON_COLOR = (80, 80, 100)
BUTTON_HOVER = (120, 120, 140)
STATUS_TEXT_COLOR = (0, 255, 255)

# Status (managed separately; currently empty)
STATUS_NAMES = []
STATUS_ICONS = []
STATUS_COUNT = 7

# Layout percentages and padding
PADDING = 10
STATUS_PANEL_WIDTH_PCT = 0.20  # 20% of screen width
CHOICE_PANEL_HEIGHT_PCT = 0.25  # 25% of screen height

STATUS_PANEL_WIDTH = int(WIDTH * STATUS_PANEL_WIDTH_PCT)
CHOICE_PANEL_HEIGHT = int(HEIGHT * CHOICE_PANEL_HEIGHT_PCT)
NARRATIVE_PANEL_WIDTH = WIDTH - STATUS_PANEL_WIDTH - 3 * PADDING
NARRATIVE_PANEL_HEIGHT = HEIGHT - CHOICE_PANEL_HEIGHT - 3 * PADDING

# Global variable to track terminal (game-over) state
terminal_scene = False

# Global variables for non-blocking typewriter effect
typing_full_text = ""
typing_visible_text = ""
typing_index = 0
last_typing_time = 0
typing_delay_ms = 30  # delay per character (milliseconds)

def start_typing(new_text):
    global typing_full_text, typing_visible_text, typing_index, last_typing_time, is_typing_done
    typing_full_text = new_text
    typing_visible_text = ""
    typing_index = 0
    last_typing_time = pygame.time.get_ticks()
    is_typing_done = False

def update_typing_text():
    global typing_index, typing_visible_text, last_typing_time, is_typing_done
    now = pygame.time.get_ticks()
    if now - last_typing_time >= typing_delay_ms and not is_typing_done:
        # Increase typing index based on elapsed time; here we add one character per delay interval.
        typing_index += 1
        last_typing_time = now
        if typing_index >= len(typing_full_text):
            typing_index = len(typing_full_text)
            is_typing_done = True
        typing_visible_text = typing_full_text[:typing_index]

# --- Helper: Dynamic Text Scaling ---
def get_scaled_text_surface(text, max_width, color, initial_size=28, min_size=12):
    font_size = initial_size
    scaled_font = pygame.font.SysFont("Consolas", font_size)
    text_surface = scaled_font.render(text, True, color)
    while text_surface.get_width() > max_width - 10 and font_size > min_size:
        font_size -= 1
        scaled_font = pygame.font.SysFont("Consolas", font_size)
        text_surface = scaled_font.render(text, True, color)
    return text_surface

# --- Helper: Save Game ---
def save_game():
    global current_scene, STATUS_VALUES, is_save_present
    is_save_present = True  # Mark that a save exists
    save_data = {
        "current_scene": current_scene,
        "status_values": STATUS_VALUES,
        "save_present": is_save_present
    }
    with open("save.json", "w", encoding="utf-8") as f:
        json.dump(save_data, f)

# --- Helper: Clear Save ---
def clear_save():
    global current_scene, STATUS_VALUES, is_save_present
    current_scene = "The Lonely Veil"
    STATUS_VALUES = []
    is_save_present = False
    with open("save.json", "w", encoding="utf-8") as f:
        json.dump({
            "current_scene": current_scene,
            "status_values": STATUS_VALUES,
            "save_present": is_save_present
        }, f)

# --- Helper: Render Title Screen ---
def render_title_screen():
    global TITLE_AREA, OPTIONS_AREA, LOGO_AREA
    global TITLE_PLAY_BUTTON, TITLE_CONTINUE_BUTTON, TITLE_RESTART_BUTTON, TITLE_OPTIONS_BUTTON, TITLE_QUIT_BUTTON, current_scene

    screen.fill((0, 0, 0))
    # Define the general areas for title screen.
    TITLE_AREA = pygame.Rect(WIDTH // 5, HEIGHT // 10, 3 * WIDTH // 5, 2 * HEIGHT // 5)
    # OPTIONS_AREA will now be used to hold the three vertically arranged buttons.
    OPTIONS_AREA = pygame.Rect(5 * WIDTH // 12, 3 * HEIGHT // 5, WIDTH // 6, 2 * HEIGHT // 5)
    LOGO_AREA = pygame.Rect(19 * WIDTH // 20, HEIGHT - (WIDTH - (19 * WIDTH // 20)),
                            WIDTH - (19 * WIDTH // 20), WIDTH - (19 * WIDTH // 20))
    # Define a vertical gap between buttons.
    gap = PADDING
    # Divide OPTIONS_AREA vertically into 3 buttons.
    button_height = (OPTIONS_AREA.height - 2 * gap) / 3
    
    if is_save_present:
        # Top row: two buttons side-by-side (Continue and Restart)
        play_area = pygame.Rect(OPTIONS_AREA.x, OPTIONS_AREA.y, OPTIONS_AREA.width, button_height)
        # Split horizontally with a gap.
        TITLE_CONTINUE_BUTTON = pygame.Rect(play_area.x, play_area.y, (play_area.width - gap) / 2, play_area.height)
        TITLE_RESTART_BUTTON = pygame.Rect(play_area.x + (play_area.width + gap) / 2, play_area.y,
                                           (play_area.width - gap) / 2, play_area.height)
    else:
        # If no save exists, use a single button for "Start Game"
        TITLE_PLAY_BUTTON = pygame.Rect(OPTIONS_AREA.x, OPTIONS_AREA.y, OPTIONS_AREA.width, button_height)

    # Options button (middle row)
    TITLE_OPTIONS_BUTTON = pygame.Rect(OPTIONS_AREA.x, OPTIONS_AREA.y + button_height + gap, 
                                       OPTIONS_AREA.width, button_height)
    # Quit button (bottom row)
    TITLE_QUIT_BUTTON = pygame.Rect(OPTIONS_AREA.x, OPTIONS_AREA.y + 2 * (button_height + gap),
                                    OPTIONS_AREA.width, button_height)

    # Draw the buttons with hover effects
    if is_save_present:
        if TITLE_CONTINUE_BUTTON.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, BUTTON_HOVER, TITLE_CONTINUE_BUTTON)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, TITLE_CONTINUE_BUTTON)
        if TITLE_RESTART_BUTTON.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, BUTTON_HOVER, TITLE_RESTART_BUTTON)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, TITLE_RESTART_BUTTON)
    else:
        if TITLE_PLAY_BUTTON.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, BUTTON_HOVER, TITLE_PLAY_BUTTON)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, TITLE_PLAY_BUTTON)

    if TITLE_OPTIONS_BUTTON.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, BUTTON_HOVER, TITLE_OPTIONS_BUTTON)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, TITLE_OPTIONS_BUTTON)
    if TITLE_QUIT_BUTTON.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, BUTTON_HOVER, TITLE_QUIT_BUTTON)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, TITLE_QUIT_BUTTON)

    # Render text onto the buttons
    if is_save_present:
        continue_text = get_scaled_text_surface("Continue Game", TITLE_CONTINUE_BUTTON.width, TEXT_COLOR)
        restart_text = get_scaled_text_surface("Restart Game", TITLE_RESTART_BUTTON.width, TEXT_COLOR)
        screen.blit(continue_text, continue_text.get_rect(center=TITLE_CONTINUE_BUTTON.center))
        screen.blit(restart_text, restart_text.get_rect(center=TITLE_RESTART_BUTTON.center))
    else:
        start_text = get_scaled_text_surface("Start Game", TITLE_PLAY_BUTTON.width, TEXT_COLOR)
        # Force the starting scene
        current_scene = "The Lonely Veil"
        screen.blit(start_text, start_text.get_rect(center=TITLE_PLAY_BUTTON.center))
        
    TITLE_OPTIONS_TEXT = font.render("Options", True, TEXT_COLOR)
    screen.blit(TITLE_OPTIONS_TEXT, TITLE_OPTIONS_TEXT.get_rect(center=TITLE_OPTIONS_BUTTON.center))
    TITLE_QUIT_TEXT = font.render("Quit Game", True, TEXT_COLOR)
    screen.blit(TITLE_QUIT_TEXT, TITLE_QUIT_TEXT.get_rect(center=TITLE_QUIT_BUTTON.center))


# --- Helper: Render Wrapped Text ---
def render_wrapped_text(text, x, y, font_obj, color, max_width, line_spacing=5):
    lines = []
    for raw_line in text.split("\n"):
        words = raw_line.split(' ')
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            test_width, _ = font_obj.size(test_line)
            if test_width > max_width and current_line:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line.strip())
        lines.append("")
    y_offset = y
    for line in lines:
        line_surface = font_obj.render(line, True, color)
        screen.blit(line_surface, (x, y_offset))
        y_offset += font_obj.get_height() + line_spacing

# --- Helper: Render Typing Text (non-blocking) ---
def render_typing_text_view(x, y, font_obj, color, max_width):
    # Update the typing effect incrementally (non-blocking)
    update_typing_text()
    render_wrapped_text(typing_visible_text, x, y, font_obj, color, max_width)

# --- Helper: Render Status ---
def render_status():
    global STATUS_PANEL, STATUS_WINDOW, STATUSES, STATUS_LOGOS, STATUS_TEXTS
    STATUSES = []
    STATUS_LOGOS = []
    STATUS_TEXTS = []
    STATUS_PANEL = pygame.Rect(PADDING, PADDING, STATUS_PANEL_WIDTH, HEIGHT - 2 * PADDING)
    pygame.draw.rect(screen, STATUS_PANEL_COLOR, STATUS_PANEL)
    STATUS_WINDOW = pygame.Rect(STATUS_PANEL.x + PADDING, STATUS_PANEL.y + PADDING,
                                STATUS_PANEL.width - 2 * PADDING, STATUS_PANEL.height - 2 * PADDING)
    STATUS_RECT_HEIGHT = min(STATUS_WINDOW.width // 3, (STATUS_WINDOW.height - (STATUS_COUNT - 1) * PADDING) / STATUS_COUNT)
    for i in range(STATUS_COUNT):
        rect = pygame.Rect(STATUS_WINDOW.x, STATUS_WINDOW.y + i * (PADDING + STATUS_RECT_HEIGHT),
                           STATUS_WINDOW.width, STATUS_RECT_HEIGHT)
        status_logo = pygame.Rect(rect.x, rect.y, rect.height, rect.height)
        status_text = pygame.Rect(rect.x + rect.height, rect.y, rect.width - rect.height, rect.height)
        STATUSES.append(rect)
        STATUS_LOGOS.append(status_logo)
        STATUS_TEXTS.append(status_text)
        
        #Code to include potential Statuses
        #try:
        #    if i < len(STATUS_ICONS):
        #        logo = pygame.image.load(STATUS_ICONS[i])
        #    else:
        #        logo = pygame.image.load("Assets/General/error.png")
        #except:
        #    logo = pygame.Surface((status_logo.width, status_logo.height))
        #    logo.fill((255, 0, 0))
        #logo = pygame.transform.scale(logo, (status_logo.width, status_logo.height))
        #screen.blit(logo, status_logo)
        
        #if (i < len(STATUS_NAMES) and i < len(STATUS_VALUES)):
        #    text_surface = font.render(STATUS_NAMES[i] + ": " + str(STATUS_VALUES[i]), True, STATUS_TEXT_COLOR)
        #else:
        #    text_surface = font.render("Error", True, STATUS_TEXT_COLOR)
        #screen.blit(text_surface, text_surface.get_rect(center=status_text.center))

# --- Helper: Render Narrative ---
def render_narrative():
    global NARRATIVE_PANEL, NARRATIVE_WINDOW
    NARRATIVE_PANEL = pygame.Rect(STATUS_PANEL_WIDTH + 2 * PADDING, PADDING,
                                  NARRATIVE_PANEL_WIDTH, NARRATIVE_PANEL_HEIGHT)
    pygame.draw.rect(screen, NARRATIVE_PANEL_COLOR, NARRATIVE_PANEL)
    NARRATIVE_WINDOW = pygame.Rect(NARRATIVE_PANEL.x + PADDING, NARRATIVE_PANEL.y + PADDING,
                                   NARRATIVE_PANEL.width - 2 * PADDING, NARRATIVE_PANEL.height - 2 * PADDING)
    # If typing is not done, update and render typing effect. Otherwise, render full text.
    if not is_typing_done:
        render_typing_text_view(NARRATIVE_WINDOW.x, NARRATIVE_WINDOW.y, font, TEXT_COLOR, NARRATIVE_WINDOW.width)
    else:
        render_wrapped_text(scene["text"], NARRATIVE_WINDOW.x, NARRATIVE_WINDOW.y, font, TEXT_COLOR, NARRATIVE_WINDOW.width)

# --- Helper: Render Choice Button Text ---
def render_choice_button_text(text, rect):
    font_size = 28
    button_font = pygame.font.SysFont("Consolas", font_size)
    text_surface = button_font.render(text, True, TEXT_COLOR)
    while text_surface.get_width() > rect.width - 10 and font_size > 12:
        font_size -= 1
        button_font = pygame.font.SysFont("Consolas", font_size)
        text_surface = button_font.render(text, True, TEXT_COLOR)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))

# --- Helper: Render Choices ---
def render_choice():
    global CHOICE_PANEL, CHOICE_WINDOW, CHOICE_BUTTONS, CHOICES, terminal_scene
    CHOICES = []
    CHOICE_BUTTONS = []
    CHOICE_PANEL = pygame.Rect(STATUS_PANEL_WIDTH + 2 * PADDING, HEIGHT - CHOICE_PANEL_HEIGHT - PADDING,
                               WIDTH - STATUS_PANEL_WIDTH - 3 * PADDING, CHOICE_PANEL_HEIGHT)
    pygame.draw.rect(screen, CHOICE_PANEL_COLOR, CHOICE_PANEL)
    CHOICE_WINDOW = pygame.Rect(CHOICE_PANEL.x + PADDING, CHOICE_PANEL.y + PADDING,
                                CHOICE_PANEL.width - 2 * PADDING, CHOICE_PANEL.height - 2 * PADDING)
    raw_choices = list(scene.get("choices", {}).keys())
    if len(raw_choices) == 0:
        terminal_scene = True
        rendered_choices = ["Game Over"]
    else:
        terminal_scene = False
        rendered_choices = raw_choices
    CHOICE_COUNT = len(rendered_choices)
    if CHOICE_COUNT > 0:
        button_width = (CHOICE_PANEL.width - (CHOICE_COUNT + 1) * PADDING) / CHOICE_COUNT
    else:
        button_width = 0
    for i in range(CHOICE_COUNT):
        choice_rect = pygame.Rect(CHOICE_WINDOW.x + i * (button_width + PADDING),
                                    CHOICE_WINDOW.y, button_width, CHOICE_WINDOW.height)
        choice_button = pygame.Rect(choice_rect.x, choice_rect.y + choice_rect.height // 3,
                                    choice_rect.width, choice_rect.height // 3)
        CHOICE_BUTTONS.append(choice_button)
        CHOICES.append(choice_rect)
        if choice_button.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, BUTTON_HOVER, choice_button)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, choice_button)
        render_choice_button_text(rendered_choices[i], choice_button)

# --- Helper: Render Menu ---
def render_menu():
    global MENU, MENU_PLAY, MENU_OPTIONS, MENU_QUIT, MENU_PLAY_BUTTON, MENU_OPTIONS_BUTTON, MENU_QUIT_BUTTON
    MENU = pygame.Rect(3 * WIDTH // 8, HEIGHT // 4, WIDTH // 4, HEIGHT // 2)
    MENU_PLAY = pygame.Rect(MENU.x, MENU.y, MENU.width, MENU.height // 3)
    MENU_OPTIONS = pygame.Rect(MENU.x, MENU.y + MENU.height // 3, MENU.width, MENU.height // 3)
    MENU_QUIT = pygame.Rect(MENU.x, MENU.y + 2 * MENU.height // 3, MENU.width, MENU.height // 3)
    MENU_PLAY_BUTTON = pygame.Rect(MENU_PLAY.x + MENU_PLAY.width // 6, MENU_PLAY.y + MENU_PLAY.height // 4,
                                     2 * MENU_PLAY.width // 3, MENU_PLAY.height // 2)
    MENU_OPTIONS_BUTTON = pygame.Rect(MENU_OPTIONS.x + MENU_OPTIONS.width // 6, MENU_OPTIONS.y + MENU_OPTIONS.height // 4,
                                        2 * MENU_OPTIONS.width // 3, MENU_OPTIONS.height // 2)
    MENU_QUIT_BUTTON = pygame.Rect(MENU_QUIT.x + MENU_QUIT.width // 6, MENU_QUIT.y + MENU_QUIT.height // 4,
                                     2 * MENU_QUIT.width // 3, MENU_QUIT.height // 2)
    pygame.draw.rect(screen, MENU_COLOR, MENU)
    if MENU_PLAY_BUTTON.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, BUTTON_HOVER, MENU_PLAY_BUTTON)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, MENU_PLAY_BUTTON)
    if MENU_OPTIONS_BUTTON.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, BUTTON_HOVER, MENU_OPTIONS_BUTTON)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, MENU_OPTIONS_BUTTON)
    if MENU_QUIT_BUTTON.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, BUTTON_HOVER, MENU_QUIT_BUTTON)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, MENU_QUIT_BUTTON)
    MENU_PLAY_TEXT = font.render("Resume", True, TEXT_COLOR)
    screen.blit(MENU_PLAY_TEXT, MENU_PLAY_TEXT.get_rect(center=MENU_PLAY_BUTTON.center))
    MENU_OPTIONS_TEXT = font.render("Options", True, TEXT_COLOR)
    screen.blit(MENU_OPTIONS_TEXT, MENU_OPTIONS_TEXT.get_rect(center=MENU_OPTIONS_BUTTON.center))
    MENU_QUIT_TEXT = font.render("Save and Quit", True, TEXT_COLOR)
    screen.blit(MENU_QUIT_TEXT, MENU_QUIT_TEXT.get_rect(center=MENU_QUIT_BUTTON.center))

# --- Debug Functions ---
def debug_title_screen():
    if debug_level_one:
        pygame.draw.rect(screen, (255, 0, 0), TITLE_AREA, 1)
        screen.blit(DEBUG_FONT.render("Title Area", True, (255, 0, 0)), TITLE_AREA)
        pygame.draw.rect(screen, (255, 0, 0), OPTIONS_AREA, 1)
        screen.blit(DEBUG_FONT.render("Options Area", True, (255, 0, 0)), OPTIONS_AREA)
        pygame.draw.rect(screen, (255, 0, 0), LOGO_AREA, 1)
        screen.blit(DEBUG_FONT.render("Logo Area", True, (255, 0, 0)), LOGO_AREA)
    if debug_level_two:
        pygame.draw.rect(screen, (0, 255, 0), TITLE_PLAY_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Title Play Button", True, (0, 255, 0)), TITLE_PLAY_BUTTON)
        pygame.draw.rect(screen, (0, 255, 0), TITLE_OPTIONS_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Title Options Button", True, (0, 255, 0)), TITLE_OPTIONS_BUTTON)
        pygame.draw.rect(screen, (0, 255, 0), TITLE_QUIT_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Title Quit Button", True, (0, 255, 0)), TITLE_QUIT_BUTTON)
    if debug_level_three:
        pass

def debug_game():
    if debug_level_one:
        pygame.draw.rect(screen, (255, 0, 0), STATUS_WINDOW, 1)
        screen.blit(DEBUG_FONT.render("Status Window", True, (255, 0, 0)), STATUS_WINDOW)
        pygame.draw.rect(screen, (255, 0, 0), NARRATIVE_WINDOW, 1)
        screen.blit(DEBUG_FONT.render("Narrative Window", True, (255, 0, 0)), NARRATIVE_WINDOW)
        pygame.draw.rect(screen, (255, 0, 0), CHOICE_WINDOW, 1)
        screen.blit(DEBUG_FONT.render("Choice Window", True, (255, 0, 0)), CHOICE_WINDOW)
    if debug_level_two:
        for i in range(STATUS_COUNT):
            pygame.draw.rect(screen, (0, 255, 0), STATUSES[i], 1)
            screen.blit(DEBUG_FONT.render("Status " + str(i + 1), True, (0, 255, 0)), STATUSES[i])
        for i in range(len(choices)):
            pygame.draw.rect(screen, (0, 255, 0), CHOICE_BUTTONS[i], 1)
            screen.blit(DEBUG_FONT.render("Choice " + str(i + 1), True, (0, 255, 0)), CHOICE_BUTTONS[i])
    if debug_level_three:
        pass

def debug_menu():
    if debug_level_one:
        pygame.draw.rect(screen, (255, 0, 0), MENU, 1)
        screen.blit(DEBUG_FONT.render("Menu", True, (255, 0, 0)), MENU)
    if debug_level_two:
        pygame.draw.rect(screen, (0, 255, 0), MENU_PLAY_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Menu Play Button", True, (0, 255, 0)), MENU_PLAY_BUTTON)
        pygame.draw.rect(screen, (0, 255, 0), MENU_OPTIONS_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Menu Options Button", True, (0, 255, 0)), MENU_OPTIONS_BUTTON)
        pygame.draw.rect(screen, (0, 255, 0), MENU_QUIT_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Menu Quit Button", True, (0, 255, 0)), MENU_QUIT_BUTTON)
    if debug_level_three:
        pass

def draw_fps():
    fps = str(int(clock.get_fps()))
    fps_text = DEBUG_FONT.render(f"FPS: {fps}", True, (255, 0, 0))
    screen.blit(fps_text, (0, 0))

# --- Main Game Loop ---
# defining animations
spaceman = Animation('Assets/animations/spaceman.aseprite')
animationmanager0 = AnimationManager([spaceman], screen)

heartAnimation = Animation('Assets/animations/heart.aseprite')
animationmanager1 = AnimationManager([heartAnimation], screen)

brainAnimation = Animation('Assets/animations/brain.aseprite')
animationmanager2 = AnimationManager([brainAnimation], screen)

oxygenAnimation = Animation('Assets/animations/oxygen.aseprite')
animationmanager3 = AnimationManager([oxygenAnimation], screen)


desertAnimation = Animation('Assets/animations/DesertPlanet.aseprite')
animationmanager4 = AnimationManager([desertAnimation], screen)

iceAnimation = Animation('Assets/animations/icePlanet.aseprite')
animationmanager5 = AnimationManager([iceAnimation], screen)

ringedAnimation = Animation('Assets/animations/ringedPlanet.aseprite')
animationmanager6 = AnimationManager([ringedAnimation], screen)

star1 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager7 = AnimationManager([star1], screen)

star2 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager8 = AnimationManager([star2], screen)

star3 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager9 = AnimationManager([star3], screen)

star4 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager10 = AnimationManager([star4], screen)

star5 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager11 = AnimationManager([star5], screen)

star6 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager12 = AnimationManager([star6], screen)

star7 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager13 = AnimationManager([star7], screen)

star8 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager14 = AnimationManager([star8], screen)

star9 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager15 = AnimationManager([star9], screen)

star10 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager16 = AnimationManager([star10], screen)

star11 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager17 = AnimationManager([star11], screen)

star12 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager18 = AnimationManager([star12], screen)

star13 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager19 = AnimationManager([star13], screen)

star14 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager20 = AnimationManager([star14], screen)

star15 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager21 = AnimationManager([star15], screen)

star16 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager22 = AnimationManager([star16], screen)

star17 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager23 = AnimationManager([star17], screen)

star18 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager24 = AnimationManager([star18], screen)

star19 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager25 = AnimationManager([star19], screen)

star20 = Animation('Assets/animations/starTWINKLE.aseprite')
animationmanager26 = AnimationManager([star20], screen)

spiralPlanet = Animation('Assets/animations/spiralPlanet.aseprite')
animationmanager27 = AnimationManager([spiralPlanet], screen)


#initializing playlist
pygame.mixer.init()

playlist = [
    'Assets/music/nerves.wav',
    'Assets/music/rane.wav',
    'Assets/music/Exploration.wav'
]
currentSongIndex = 1 #Start at second song, arbitrary (loops through playlist in event handler)

SONG_END = pygame.USEREVENT +1
pygame.mixer.music.set_endevent(SONG_END)

pygame.mixer.music.load(playlist[currentSongIndex])
pygame.mixer.music.play()


# Main Loop
running = True
while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    scene = story[current_scene]
    choices = list(scene.get("choices", {}).keys())
    
    screen.fill(BORDER_COLOR)
    
    if GAME_STATE == "title":
        render_title_screen()
        # animation updating
        animationmanager4.update_self(-50, -90)
        animationmanager5.update_self(1350, 150)
        animationmanager6.update_self(350, 450)
        animationmanager27.update_self(1500, 650)
        animationmanager7.update_self(450, 300)
        animationmanager8.update_self(950, 320)
        animationmanager9.update_self(150, 350)
        animationmanager10.update_self(1150, 200)
        animationmanager11.update_self(200, 600)
        animationmanager12.update_self(650, 550)
        animationmanager13.update_self(450, 500)
        animationmanager14.update_self(820, 420)
        animationmanager15.update_self(1250, 650)
        animationmanager16.update_self(315, 400)
        animationmanager17.update_self(400, 720)
        animationmanager18.update_self(550, 950)
        animationmanager19.update_self(1500, 640)
        animationmanager20.update_self(1800, 250)
        animationmanager21.update_self(1650, 500)
        animationmanager22.update_self(2020, 480)
        animationmanager23.update_self(1950, 620)
        animationmanager24.update_self(1315, 400)
        animationmanager25.update_self(2100, 700)
        animationmanager26.update_self(1650, 450)
        debug_title_screen()
    else:
        render_status()
        render_choice()
        # animation updating
        animationmanager1.update_self(-50, -90)
        animationmanager2.update_self(-60, 10)
        animationmanager3.update_self(-60, -120)
        animationmanager0.update_self(-60, 500)
        render_narrative()
        debug_game()
        
    
    if is_menu_open:
        render_menu()
        debug_menu()
        
    draw_fps()
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if GAME_STATE == "game" and event.key == pygame.K_ESCAPE:
                is_menu_open = not is_menu_open
            if event.key == pygame.K_1:
                debug_level_one = not debug_level_one
            if event.key == pygame.K_2:
                debug_level_two = not debug_level_two
            if event.key == pygame.K_3:
                debug_level_three = not debug_level_three
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if GAME_STATE == "title":
                if is_save_present:
                    # Check if the user clicked on the continue or restart button.
                    # Title screen now has two buttons in the play area.
                    # They were created in render_title_screen.
                    # We need to test those buttons, so we require them to be global.
                    try:
                        if TITLE_CONTINUE_BUTTON.collidepoint(mx, my):
                            GAME_STATE = "game"
                        elif TITLE_RESTART_BUTTON.collidepoint(mx, my):
                            clear_save()
                            GAME_STATE = "game"
                    except NameError:
                        # Fall back for when no save exists
                        if TITLE_PLAY_BUTTON.collidepoint(mx, my):
                            current_scene = "The Lonely Veil"
                            GAME_STATE = "game"
                else:
                    if TITLE_PLAY_BUTTON.collidepoint(mx, my):
                        current_scene = "The Lonely Veil"
                        GAME_STATE = "game"
                if TITLE_QUIT_BUTTON.collidepoint(mx, my):
                    running = False
            else:
                if is_menu_open:
                    if MENU_PLAY_BUTTON.collidepoint(mx, my):
                        is_menu_open = False
                    if MENU_QUIT_BUTTON.collidepoint(mx, my):
                        save_game()
                        is_menu_open = False
                        GAME_STATE = "title"
                else:
                    if terminal_scene:
                        if CHOICE_BUTTONS and CHOICE_BUTTONS[0].collidepoint(mx, my):
                            clear_save()
                            GAME_STATE = "title"
                    else:
                        for i, rect in enumerate(CHOICE_BUTTONS):
                            if rect.collidepoint(mx, my) and i < len(choices):
                                current_scene = scene["choices"][choices[i]]
                                is_typing_done = False
                                are_effects_applied = False
                                # Set up the typewriter effect for the new scene text.
                                start_typing(story[current_scene]["text"])
    
        elif event.type == SONG_END:
            currentSongIndex += 1
            if currentSongIndex >= len(playlist):
                currentSongIndex = 0
            pygame.mixer.music.load(playlist[currentSongIndex])
            pygame.mixer.music.play()
        clock.tick(60)

pygame.quit()
