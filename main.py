# run pip3 install pygame_aseprite_animation to install animation package
from pygame_aseprite_animation import *
import os, pygame
import json
import time

pygame.init()

clock = pygame.time.Clock()  # Create a Clock object

with open("story.json", "r") as f:
    story = json.load(f)
with open("save.json", "r") as f:
        save_data = json.load(f)
        current_scene = save_data["current_scene"]
        STATUS_VALUES = save_data["status_values"]
        is_save_present = save_data["save_present"]
GAME_STATE = "title"

# Screen Size
WIDTH = pygame.display.Info().current_w
HEIGHT = pygame.display.Info().current_h
pygame.display.set_caption("Title")
icon = pygame.image.load("Assets/General/logo.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Font
pygame.font.init()
font = pygame.font.SysFont("Consolas", 28)
DEBUG_FONT = pygame.font.SysFont("Consolas", 15)

# Flags
is_typing_done = False
are_effects_applied = False
is_menu_open = False
is_save_present = False
debug_level_one = False
debug_level_two = False
debug_level_three = False

# Colors
BORDER_COLOR = (255, 255, 255)  # White
STATUS_PANEL_COLOR = (36, 36, 36)  # Shadow
NARRATIVE_PANEL_COLOR = (82, 82, 82)  # Gray
CHOICE_PANEL_COLOR = (78, 72, 76)  # Fossil
MENU_COLOR = (178, 190, 181) # Ash
TEXT_COLOR = (0, 0, 0) # Black
BUTTON_COLOR = (180, 180, 180)
BUTTON_HOVER = (220, 220, 220)
STATUS_TEXT_COLOR = (0, 255, 255)

# Status
STATUS_NAMES = []
# STATUS_VALUES =  [] 
STATUS_ICONS = []
STATUS_COUNT = 7

# Sizing
PADDING = 10
STATUS_PANEL_WIDTH = WIDTH / 4
CHOICE_PANEL_HEIGHT = HEIGHT / 4

def save_game():
    save_data = {
        "current_scene": current_scene,
        "status_values": STATUS_VALUES,
        "save_present": True
    }
    with open("save.json", "w") as f:
        json.dump(save_data, f)

def render_title_screen():
    global TITLE_AREA, OPTIONS_AREA, LOGO_AREA, TITLE_PLAY, TITLE_OPTIONS, TITLE_QUIT, TITLE_PLAY_BUTTON, TITLE_OPTIONS_BUTTON, TITLE_QUIT_BUTTON

    #Level 0
    screen.fill((0, 0, 0))

    # Level 1
    TITLE_AREA = pygame.Rect(WIDTH // 5, HEIGHT // 10, 3 * WIDTH // 5, 2 * HEIGHT // 5)
    OPTIONS_AREA = pygame.Rect(5 * WIDTH // 12, 3 * HEIGHT // 5, WIDTH // 6, 2 * HEIGHT // 5)
    LOGO_AREA = pygame.Rect(19 * WIDTH // 20, HEIGHT - (WIDTH - (19 * WIDTH // 20)), WIDTH - (19 * WIDTH // 20), WIDTH - (19 * WIDTH // 20))
    # Level 2
    TITLE_PLAY = pygame.Rect(OPTIONS_AREA.x, OPTIONS_AREA.y, OPTIONS_AREA.width, OPTIONS_AREA.height // 3)
    TITLE_OPTIONS = pygame.Rect(OPTIONS_AREA.x, OPTIONS_AREA.y + OPTIONS_AREA.height // 3, OPTIONS_AREA.width, OPTIONS_AREA.height // 3)
    TITLE_QUIT = pygame.Rect(OPTIONS_AREA.x, OPTIONS_AREA.y + 2 * OPTIONS_AREA.height // 3, OPTIONS_AREA.width, OPTIONS_AREA.height // 3)
    # Level 3
    TITLE_PLAY_BUTTON = pygame.Rect(TITLE_PLAY.x + TITLE_PLAY.width // 6, TITLE_PLAY.y + TITLE_PLAY.height // 4, 2 * TITLE_PLAY.width // 3, TITLE_PLAY.height // 2)
    TITLE_OPTIONS_BUTTON = pygame.Rect(TITLE_OPTIONS.x + TITLE_OPTIONS.width // 6, TITLE_OPTIONS.y + TITLE_OPTIONS.height // 4, 2 * TITLE_OPTIONS.width // 3, TITLE_OPTIONS.height // 2)
    TITLE_QUIT_BUTTON = pygame.Rect(TITLE_QUIT.x + TITLE_QUIT.width // 6, TITLE_QUIT.y + TITLE_QUIT.height // 4, 2 * TITLE_QUIT.width // 3, TITLE_QUIT.height // 2)

    # Render
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

    if not is_save_present:
        TITLE_PLAY_TEXT = font.render("Start Game", True, TEXT_COLOR)
    else:
        TITLE_PLAY_TEXT = font.render("Continue Game", True, TEXT_COLOR)
    screen.blit(TITLE_PLAY_TEXT, TITLE_PLAY_TEXT.get_rect(center=TITLE_PLAY_BUTTON.center))

    TITLE_OPTIONS_TEXT = font.render("Options", True, TEXT_COLOR)
    screen.blit(TITLE_OPTIONS_TEXT, TITLE_OPTIONS_TEXT.get_rect(center=TITLE_OPTIONS_BUTTON.center))

    TITLE_QUIT_TEXT = font.render("Quit Game", True, TEXT_COLOR)
    screen.blit(TITLE_QUIT_TEXT, TITLE_QUIT_TEXT.get_rect(center=TITLE_QUIT_BUTTON.center))

def render_wrapped_text(text, x, y, font, color, max_width, line_spacing=5):
    lines = []
    for raw_line in text.split("\n"):  # Handle explicit newlines
        words = raw_line.split(' ')
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_width, _ = font.size(test_line)

            if test_width > max_width and current_line:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line.strip())  # Add remaining words

        lines.append("")  # Ensure explicit newlines are preserved

    y_offset = y
    for line in lines:
        line_surface = font.render(line, True, color)
        screen.blit(line_surface, (x, y_offset))
        y_offset += font.get_height() + line_spacing  # Adjust spacing

def render_typing_text(text, x, y, font, color, max_width, delay=0.03):
    global is_typing_done
    
    words = text.split(" ")
    current_line = ""
    lines = []
    
    for word in words:
        test_line = current_line + word + " "
        test_width, _ = font.size(test_line)

        if test_width > max_width and current_line:
            lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line

    if current_line:
        lines.append(current_line.strip())

    y_offset = y
    total_text = "\n".join(lines)  # Flatten into a single string
    visible_text = ""

    for i in range(len(total_text)):
        visible_text = total_text[:i+1]  # Reveal one character at a time
        screen.fill(NARRATIVE_PANEL_COLOR, (x, y, max_width, len(lines) * (font.get_height() + 5)))  # Clear previous text

        y_offset = y
        for line in visible_text.split("\n"):
            line_surface = font.render(line, True, color)
            screen.blit(line_surface, (x, y_offset))
            y_offset += font.get_height() + 5  # Adjust spacing
        
        pygame.display.flip()
        time.sleep(delay)  # Typing delay
    is_typing_done = True

def render_status():
    global STATUS_PANEL, STATUS_WINDOW, STATUSES, STATUS_LOGOS, STATUS_TEXTS
    STATUSES = []
    STATUS_LOGOS = []
    STATUS_TEXTS = []

    STATUS_PANEL = pygame.Rect(PADDING, PADDING, STATUS_PANEL_WIDTH, HEIGHT - 2 * PADDING)
    pygame.draw.rect(screen, STATUS_PANEL_COLOR, STATUS_PANEL)
    STATUS_WINDOW = pygame.Rect(STATUS_PANEL.x + PADDING, STATUS_PANEL.y + PADDING, STATUS_PANEL.width - 2 * PADDING, STATUS_PANEL.height - 2 * PADDING)

    STATUS_RECT_HEIGHT = min(STATUS_WINDOW.width // 3, (STATUS_WINDOW.height - (STATUS_COUNT - 1) * PADDING) / STATUS_COUNT)
    for i in range(STATUS_COUNT):
        STATUS = pygame.Rect(STATUS_WINDOW.x, STATUS_WINDOW.y + i * (PADDING + STATUS_RECT_HEIGHT), STATUS_WINDOW.width, STATUS_RECT_HEIGHT)
        STATUS_LOGO = pygame.Rect(STATUS.x, STATUS.y, STATUS.height, STATUS.height)
        STATUS_TEXT = pygame.Rect(STATUS.x + STATUS.height, STATUS.y, STATUS.width - STATUS.height, STATUS.height)

        STATUSES.append(STATUS)
        STATUS_LOGOS.append(STATUS_LOGO)
        STATUS_TEXTS.append(STATUS_TEXT)

        #if (i < len(STATUS_ICONS)):
        #    logo = pygame.image.load(STATUS_ICONS[i])
        #else:
        #    logo = pygame.image.load("Assets/General/error.png")
        #logo = pygame.transform.scale(logo, (STATUS_LOGO.width, STATUS_LOGO.height))
        #screen.blit(logo, STATUS_LOGO)

        if (i < len(STATUS_NAMES) and i < len(STATUS_VALUES)):
            TEXT = font.render(STATUS_NAMES[i] + ": " + str(STATUS_VALUES[i]), True, STATUS_TEXT_COLOR)
        else:
            TEXT = font.render("Error", True, STATUS_TEXT_COLOR)
        screen.blit(TEXT, TEXT.get_rect(center = STATUS_TEXT.center))
        

def render_narrative():
    global NARRATIVE_PANEL, NARRATIVE_WINDOW
    
    NARRATIVE_PANEL = pygame.Rect(STATUS_PANEL_WIDTH + 2 * PADDING, PADDING, WIDTH - STATUS_PANEL_WIDTH - 3 * PADDING, HEIGHT - CHOICE_PANEL_HEIGHT - 3 * PADDING)
    pygame.draw.rect(screen, NARRATIVE_PANEL_COLOR, NARRATIVE_PANEL)
    
    NARRATIVE_WINDOW = pygame.Rect(NARRATIVE_PANEL.x + PADDING, NARRATIVE_PANEL.y + PADDING, NARRATIVE_PANEL.width - 2 * PADDING, NARRATIVE_PANEL.height - 2 * PADDING)

    if not is_typing_done:
        render_typing_text(scene["text"], NARRATIVE_WINDOW.x, NARRATIVE_WINDOW.y, font, TEXT_COLOR, NARRATIVE_WINDOW.width)
    else:
        render_wrapped_text(scene["text"], NARRATIVE_WINDOW.x, NARRATIVE_WINDOW.y, font, TEXT_COLOR, NARRATIVE_WINDOW.width)

def render_choice():
    global CHOICE_PANEL, CHOICE_WINDOW, CHOICES, CHOICE_BUTTONS
    CHOICES = []
    CHOICE_BUTTONS = []

    CHOICE_PANEL = pygame.Rect(STATUS_PANEL_WIDTH + 2 * PADDING, HEIGHT - CHOICE_PANEL_HEIGHT - PADDING, WIDTH - STATUS_PANEL_WIDTH - 3 * PADDING, CHOICE_PANEL_HEIGHT)
    pygame.draw.rect(screen, CHOICE_PANEL_COLOR, CHOICE_PANEL)

    CHOICE_WINDOW = pygame.Rect(CHOICE_PANEL.x + PADDING, CHOICE_PANEL.y + PADDING, CHOICE_PANEL.width - 2 * PADDING, CHOICE_PANEL.height - 2 * PADDING)
    
    CHOICE_WIDTH = (CHOICE_PANEL.width - (CHOICE_COUNT + 1) * PADDING) / CHOICE_COUNT
    for i in range(CHOICE_COUNT):
        CHOICE = pygame.Rect(CHOICE_WINDOW.x + i * (CHOICE_WIDTH + PADDING), CHOICE_WINDOW.y, CHOICE_WIDTH, CHOICE_WINDOW.height)
        CHOICE_BUTTON = pygame.Rect(CHOICE.x, CHOICE.y + CHOICE.height // 3, CHOICE.width, CHOICE.height // 3)

        CHOICES.append(CHOICE)
        CHOICE_BUTTONS.append(CHOICE_BUTTON)

        if CHOICE_BUTTON.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, BUTTON_HOVER, CHOICE_BUTTON)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, CHOICE_BUTTON) 

        CHOICE_BUTTON_TEXT = font.render(choices[i], True, TEXT_COLOR)
        screen.blit(CHOICE_BUTTON_TEXT, CHOICE_BUTTON_TEXT.get_rect(center =  CHOICE_BUTTON.center))

def render_menu():
    global MENU, MENU_PLAY, MENU_OPTIONS, MENU_QUIT, MENU_PLAY_BUTTON, MENU_OPTIONS_BUTTON, MENU_QUIT_BUTTON

    # Level 1
    MENU = pygame.Rect(3 * WIDTH // 8, HEIGHT // 4, WIDTH // 4, HEIGHT // 2)
    # Level 2
    MENU_PLAY = pygame.Rect(MENU.x, MENU.y, MENU.width, MENU.height // 3)
    MENU_OPTIONS = pygame.Rect(MENU.x, MENU.y + MENU.height // 3, MENU.width, MENU.height // 3)
    MENU_QUIT = pygame.Rect(MENU.x, MENU.y + 2 * MENU.height // 3, MENU.width, MENU.height // 3)
    # Level 3
    MENU_PLAY_BUTTON = pygame.Rect(MENU_PLAY.x + MENU_PLAY.width // 6, MENU_PLAY.y + MENU_PLAY.height // 4, 2 * MENU_PLAY.width // 3, MENU_PLAY.height // 2)
    MENU_OPTIONS_BUTTON = pygame.Rect(MENU_OPTIONS.x + MENU_OPTIONS.width // 6, MENU_OPTIONS.y + MENU_OPTIONS.height // 4, 2 * MENU_OPTIONS.width // 3, MENU_OPTIONS.height // 2)
    MENU_QUIT_BUTTON = pygame.Rect(MENU_QUIT.x + MENU_QUIT.width // 6, MENU_QUIT.y + MENU_QUIT.height // 4, 2 * MENU_QUIT.width // 3, MENU_QUIT.height // 2)

    # Render
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

def debug_title_screen():
    if debug_level_one:
        # Title Area
        pygame.draw.rect(screen, (255, 0, 0), TITLE_AREA, 1)
        screen.blit(DEBUG_FONT.render("Title Area", True, (255, 0, 0)), TITLE_AREA)
        # Options Area
        pygame.draw.rect(screen, (255, 0, 0), OPTIONS_AREA, 1)
        screen.blit(DEBUG_FONT.render("Options Area", True, (255, 0, 0)), OPTIONS_AREA)
        # Logo Area
        pygame.draw.rect(screen, (255, 0, 0), LOGO_AREA, 1)
        screen.blit(DEBUG_FONT.render("Logo Area", True, (255, 0, 0)), LOGO_AREA)
    if debug_level_two:
        # Title Play
        pygame.draw.rect(screen, (0, 255, 0), TITLE_PLAY, 1)
        screen.blit(DEBUG_FONT.render("Title Play", True, (0, 255, 0)), TITLE_PLAY)
        # Title Options
        pygame.draw.rect(screen, (0, 255, 0), TITLE_OPTIONS, 1)
        screen.blit(DEBUG_FONT.render("Title Options", True, (0, 255, 0)), TITLE_OPTIONS)
        # Title Exit
        pygame.draw.rect(screen, (0, 255, 0), TITLE_QUIT, 1)
        screen.blit(DEBUG_FONT.render("Title Exit", True, (0, 255, 0)), TITLE_QUIT)
    if debug_level_three:
        # Title Play Button
        pygame.draw.rect(screen, (0, 0, 255), TITLE_PLAY_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Title Play Button", True, (0, 0, 255)), TITLE_PLAY_BUTTON)
        # Title Options Button
        pygame.draw.rect(screen, (0, 0, 255), TITLE_OPTIONS_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Title Options Button", True, (0, 0, 255)), TITLE_OPTIONS_BUTTON)
        # Title Play Button
        pygame.draw.rect(screen, (0, 0, 255), TITLE_QUIT_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Title Exit Button", True, (0, 0, 255)), TITLE_QUIT_BUTTON)

def debug_game():
    if debug_level_one:
        # Status Window
        pygame.draw.rect(screen, (255, 0, 0), STATUS_WINDOW, 1)
        screen.blit(DEBUG_FONT.render("Status Window", True, (255, 0, 0)), STATUS_WINDOW)
        # Narrative Window
        pygame.draw.rect(screen, (255, 0, 0), NARRATIVE_WINDOW, 1)
        screen.blit(DEBUG_FONT.render("Narrative Window", True, (255, 0, 0)), NARRATIVE_WINDOW)
        # Choice Window
        pygame.draw.rect(screen, (255, 0, 0), CHOICE_WINDOW, 1)
        screen.blit(DEBUG_FONT.render("Choice Window", True, (255, 0, 0)), CHOICE_WINDOW)
    if debug_level_two:
        # Status
        for i in range(STATUS_COUNT):
            pygame.draw.rect(screen, (0, 255, 0), STATUSES[i], 1)
            screen.blit(DEBUG_FONT.render("Status " + str(i + 1), True, (0, 255, 0)), STATUSES[i])
        # Choice
        for i in range(CHOICE_COUNT):
            pygame.draw.rect(screen, (0, 255, 0), CHOICES[i], 1)
            screen.blit(DEBUG_FONT.render("Choice " + str(i + 1), True, (0, 255, 0)), CHOICES[i])
    if debug_level_three:
        # Status Logos and Text
        for i in range(STATUS_COUNT):
            pygame.draw.rect(screen, (0, 0, 255), STATUS_LOGOS[i], 1)
            screen.blit(DEBUG_FONT.render("Logo " + str(i + 1), True, (0, 0, 255)), STATUS_LOGOS[i])
            pygame.draw.rect(screen, (0, 0, 255), STATUS_TEXTS[i], 1)
            screen.blit(DEBUG_FONT.render("Text " + str(i + 1), True, (0, 0, 255)), STATUS_TEXTS[i])
        # Choice Buttons
        for i in range(CHOICE_COUNT):
            pygame.draw.rect(screen, (0, 0, 255), CHOICE_BUTTONS[i], 1)
            screen.blit(DEBUG_FONT.render("Button " + str(i + 1), True, (0, 0, 255)), CHOICE_BUTTONS[i])

def debug_menu():
    if debug_level_one:
        # Menu
        pygame.draw.rect(screen, (255, 0, 0), MENU, 1)
        screen.blit(DEBUG_FONT.render("Menu", True, (255, 0, 0)), MENU)
    if debug_level_two:
        # Menu Play
        pygame.draw.rect(screen, (0, 255, 0), MENU_PLAY, 1)
        screen.blit(DEBUG_FONT.render("Menu Play", True, (0, 255, 0)), MENU_PLAY)
        # Menu Options
        pygame.draw.rect(screen, (0, 255, 0), MENU_OPTIONS, 1)
        screen.blit(DEBUG_FONT.render("Menu Options", True, (0, 255, 0)), MENU_OPTIONS)
        # Menu Exit
        pygame.draw.rect(screen, (0, 255, 0), MENU_QUIT, 1)
        screen.blit(DEBUG_FONT.render("Menu Exit", True, (0, 255, 0)), MENU_QUIT)
    if debug_level_three:
        # Menu Play Button
        pygame.draw.rect(screen, (0, 0, 255), MENU_PLAY_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Menu Play Button", True, (0, 0, 255)), MENU_PLAY_BUTTON)
        # Menu Options Button
        pygame.draw.rect(screen, (0, 0, 255), MENU_OPTIONS_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Menu Options Button", True, (0, 0, 255)), MENU_OPTIONS_BUTTON)
        # Menu Exit Button
        pygame.draw.rect(screen, (0, 0, 255), MENU_QUIT_BUTTON, 1)
        screen.blit(DEBUG_FONT.render("Menu Exit Button", True, (0, 0, 255)), MENU_QUIT_BUTTON)

def draw_fps():
    fps = str(int(clock.get_fps()))  # Get FPS and convert to string
    fps_text = DEBUG_FONT.render(f"FPS: {fps}", True, (255, 0, 0))  # White text
    screen.blit(fps_text, (0, 0))  # Position at top-left

# defining animations
heartAnimation = Animation('Assets/animations/heart.aseprite')
animationmanager1 = AnimationManager([heartAnimation], screen)

brainAnimation = Animation('Assets/animations/brain.aseprite')
animationmanager2 = AnimationManager([brainAnimation], screen)

oxygenAnimation = Animation('Assets/animations/oxygen.aseprite')
animationmanager3 = AnimationManager([oxygenAnimation], screen)

#initializing playlist
pygame.mixer.init()

playlist = [
    'Assets/music/nerves.wav',
    'Assets/music/rane.wav',
    'Assets/music/Exploration.wav'
]
currentSongIndex = 1

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
    CHOICE_COUNT = len(choices)

    if (CHOICE_COUNT == 0):
        GAME_STATE = "title"
        current_scene = "intro"

    screen.fill(BORDER_COLOR)
    
    if (GAME_STATE == "title"):
        render_title_screen()
        debug_title_screen()
    else:
        render_status()
        render_choice()
        # animation updating
        animationmanager1.update_self(-50, -90)
        animationmanager2.update_self(-60, 10)
        animationmanager3.update_self(-60, -120)
        render_narrative()
        debug_game()
        
    
    if is_menu_open:
        render_menu()
        debug_menu()
    
    pygame.display.flip()

    # Event Handling
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
                if TITLE_PLAY_BUTTON.collidepoint(mx, my):
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
                    for i, rect in enumerate(CHOICE_BUTTONS):
                        if rect.collidepoint(mx, my) and i < len(choices):
                            current_scene = scene["choices"][choices[i]]
                            is_typing_done = False
                            are_effects_applied = False
        elif event.type == SONG_END:
            currentSongIndex += 1
            if currentSongIndex >= len(playlist):
                currentSongIndex = 0
            pygame.mixer.music.load(playlist[currentSongIndex])
            pygame.mixer.music.play()
    
    

pygame.quit()