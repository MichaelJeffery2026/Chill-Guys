import pygame
import json
import time

pygame.init()

with open("story.json", "r") as f:
    story = json.load(f)
current_scene = "intro"
GAME_STATE = "menu"

STATUS_EFFECTS = ["Health", "Stamina", "Money"]
STATUS_VALUES =  [100, 90, 0] 
STATUS_ICONS = ["error.png", "error.png", "error.png"]
STATUS_COUNT = len(STATUS_EFFECTS)

# Get screen size
WIDTH = pygame.display.Info().current_w
HEIGHT = pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Title")

# Colors
NARRATIVE_COLOR = (82, 82, 82)  # Gray
CHOICE_COLOR = (78, 72, 76)  # Fossil
STATUS_COLOR = (36, 36, 36)  # Shadow
BORDER_COLOR = (255, 255, 255)  # White
TEXT_COLOR = (0, 0, 0) # Black
BUTTON_COLOR = (180, 180, 180)
BUTTON_HOVER = (220, 220, 220)

# Font setup
pygame.font.init()
font = pygame.font.SysFont("Consolas", 28)
title_font = pygame.font.SysFont("Consolas", 48, bold=True)

# BASE ASPECTS
BORDER_THICKNESS = 10
STATUS_PADDING = 10
NARRATIVE_PADDING = 10
CHOICE_PADDING = 10

#Menu Aspects
MENU_BUTTON_WIDTH = 200
MENU_BUTTON_HEIGHT = 60
MENU_BUTTON_X = (WIDTH - MENU_BUTTON_WIDTH) // 2
MENU_BUTTON_Y = HEIGHT // 2
MENU_BUTTON_RECT = pygame.Rect(MENU_BUTTON_X, MENU_BUTTON_Y, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)

# Base Panel Attributes (DO NOT EDIT)
STATUS_X = BORDER_THICKNESS
STATUS_Y = BORDER_THICKNESS
STATUS_WIDTH = (WIDTH - 3 * BORDER_THICKNESS) // 4
STATUS_HEIGHT = HEIGHT - 2 * BORDER_THICKNESS

NARRATIVE_X = BORDER_THICKNESS + STATUS_WIDTH + BORDER_THICKNESS
NARRATIVE_Y = BORDER_THICKNESS
NARRATIVE_WIDTH = WIDTH - NARRATIVE_X - BORDER_THICKNESS
NARRATIVE_HEIGHT = 3 * (HEIGHT - 3 * BORDER_THICKNESS) // 4

NARRATIVE_RECT_X = NARRATIVE_X + NARRATIVE_PADDING
NARRATIVE_RECT_Y = NARRATIVE_Y + NARRATIVE_PADDING
NARRATIVE_RECT_WIDTH = NARRATIVE_WIDTH - 2 * NARRATIVE_PADDING
NARRATIVE_RECT_HEIGHT = NARRATIVE_HEIGHT - 2 * NARRATIVE_PADDING

CHOICE_X = STATUS_X + STATUS_WIDTH + BORDER_THICKNESS
CHOICE_Y = NARRATIVE_Y + NARRATIVE_HEIGHT + BORDER_THICKNESS
CHOICE_WIDTH = WIDTH - CHOICE_X - BORDER_THICKNESS
CHOICE_HEIGHT = HEIGHT - CHOICE_Y - BORDER_THICKNESS

CHOICE_BUTTONS = []

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
    global TYPING_DONE
    
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
        screen.fill(NARRATIVE_COLOR, (x, y, max_width, len(lines) * (font.get_height() + 5)))  # Clear previous text

        y_offset = y
        for line in visible_text.split("\n"):
            line_surface = font.render(line, True, color)
            screen.blit(line_surface, (x, y_offset))
            y_offset += font.get_height() + 5  # Adjust spacing
        
        pygame.display.flip()
        time.sleep(delay)  # Typing delay
    TYPING_DONE = True

def render_main_menu():
    # Render Title
    title_text = title_font.render("Title", True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    # Render Start Button
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button_color = BUTTON_HOVER if MENU_BUTTON_RECT.collidepoint(mouse_x, mouse_y) else BUTTON_COLOR

    pygame.draw.rect(screen, button_color, MENU_BUTTON_RECT)
    pygame.draw.rect(screen, TEXT_COLOR, MENU_BUTTON_RECT, 2)  # Border

    start_text = font.render("Start Game", True, TEXT_COLOR)
    start_rect = start_text.get_rect(center=MENU_BUTTON_RECT.center)
    screen.blit(start_text, start_rect)

def render_status_panel(STATUS_COUNT):
    pygame.draw.rect(screen, STATUS_COLOR, (STATUS_X, STATUS_Y, STATUS_WIDTH, STATUS_HEIGHT))

    STATUS_RECT_X = STATUS_X + STATUS_PADDING
    STATUS_RECT_Y = STATUS_Y + STATUS_PADDING
    STATUS_RECT_WIDTH = STATUS_WIDTH - 2 * STATUS_PADDING
    STATUS_RECT_HEIGHT = min(STATUS_RECT_WIDTH // 3, (STATUS_HEIGHT - (STATUS_COUNT + 1) * STATUS_PADDING) / STATUS_COUNT)

    for i in range(STATUS_COUNT):
        STATUS_LOGO_RECT = pygame.Rect(STATUS_RECT_X, STATUS_RECT_Y, STATUS_RECT_HEIGHT, STATUS_RECT_HEIGHT)
        STATUS_TEXT_RECT = pygame.Rect(STATUS_RECT_X + STATUS_RECT_HEIGHT, STATUS_RECT_Y, STATUS_RECT_WIDTH - STATUS_RECT_HEIGHT, STATUS_RECT_HEIGHT)

        if (i < len(STATUS_EFFECTS)):
            image = pygame.image.load(STATUS_ICONS[i]).convert_alpha()
            image = pygame.transform.scale(image, (STATUS_LOGO_RECT.width, STATUS_LOGO_RECT.height))  
            screen.blit(image, (STATUS_LOGO_RECT.x, STATUS_LOGO_RECT.y))

            text = font.render(STATUS_EFFECTS[i] + ": " + str(STATUS_VALUES[i]), True, (0, 255, 0))
            text_rect = text.get_rect(center = (STATUS_TEXT_RECT.x + STATUS_TEXT_RECT.width // 2, STATUS_TEXT_RECT.y + STATUS_TEXT_RECT.height // 2))
            screen.blit(text, text_rect)
        else:
            pygame.draw.rect(screen, (0, 255, 0), STATUS_LOGO_RECT, 1)
            pygame.draw.rect(screen, (0, 0, 255), STATUS_TEXT_RECT, 1)

        STATUS_RECT_Y += STATUS_RECT_HEIGHT + STATUS_PADDING

def render_narrative_window():
    pygame.draw.rect(screen, NARRATIVE_COLOR, (NARRATIVE_X, NARRATIVE_Y, NARRATIVE_WIDTH, NARRATIVE_HEIGHT))

    # NARRATIVE_RECT = pygame.Rect(NARRATIVE_RECT_X, NARRATIVE_RECT_Y, NARRATIVE_RECT_WIDTH, NARRATIVE_RECT_HEIGHT)
    # pygame.draw.rect(screen, (255, 0, 0), NARRATIVE_RECT, 1)

    if not TYPING_DONE:
        render_typing_text(scene["text"], NARRATIVE_RECT_X, NARRATIVE_RECT_Y, font, TEXT_COLOR, NARRATIVE_RECT_WIDTH)
    else:
        render_wrapped_text(scene["text"], NARRATIVE_RECT_X, NARRATIVE_RECT_Y, font, TEXT_COLOR, NARRATIVE_RECT_WIDTH)

def render_choice_panel(CHOICE_COUNT):
    global CHOICE_BUTTONS

    pygame.draw.rect(screen, CHOICE_COLOR, (CHOICE_X, CHOICE_Y, CHOICE_WIDTH, CHOICE_HEIGHT))

    CHOICE_RECT_X = CHOICE_X + CHOICE_PADDING
    CHOICE_RECT_Y = CHOICE_Y + CHOICE_PADDING
    CHOICE_RECT_WIDTH = (CHOICE_WIDTH - (CHOICE_COUNT + 1) * CHOICE_PADDING) / CHOICE_COUNT
    CHOICE_RECT_HEIGHT = CHOICE_HEIGHT - 2 * CHOICE_PADDING

    CHOICE_BUTTON_X = CHOICE_RECT_X
    CHOICE_BUTTON_Y = CHOICE_RECT_Y + CHOICE_RECT_HEIGHT / 3
    CHOICE_BUTTON_WIDTH = CHOICE_RECT_WIDTH
    CHOICE_BUTTON_HEIGHT = CHOICE_RECT_HEIGHT / 3

    CHOICE_BUTTONS = []
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for i in range(CHOICE_COUNT):
        # CHOICE_RECT = pygame.Rect(CHOICE_RECT_X, CHOICE_RECT_Y, CHOICE_RECT_WIDTH, CHOICE_RECT_HEIGHT)
        # pygame.draw.rect(screen, (0, 255, 0), CHOICE_RECT, 1)
        BUTTON_RECT = pygame.Rect(CHOICE_BUTTON_X, CHOICE_BUTTON_Y, CHOICE_BUTTON_WIDTH, CHOICE_BUTTON_HEIGHT)

        if BUTTON_RECT.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, BUTTON_HOVER, BUTTON_RECT)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, BUTTON_RECT)

        choice = font.render(choices[i], True, TEXT_COLOR)
        choice_rect = choice.get_rect(center=(CHOICE_BUTTON_X + CHOICE_BUTTON_WIDTH // 2, CHOICE_BUTTON_Y + CHOICE_BUTTON_HEIGHT // 2))
        screen.blit(choice, choice_rect)

        CHOICE_BUTTONS.append(BUTTON_RECT)
        CHOICE_RECT_X += CHOICE_RECT_WIDTH + CHOICE_PADDING
        CHOICE_BUTTON_X = CHOICE_RECT_X

# FLAGS (DO NOT EDIT)
TYPING_DONE = False
EFFECTS_APPLIED = False
running = True

# Main Loop
while running:
    scene = story[current_scene]
    choices = list(scene.get("choices", {}).keys())
    CHOICE_COUNT = len(choices)

    if (CHOICE_COUNT == 0):
        GAME_STATE = "menu"
        current_scene = "intro"

    if not EFFECTS_APPLIED:
        STATUS_VALUES[0] += scene.get("healthchange", 0)
        STATUS_VALUES[1] += scene.get("staminachange", 0)
        STATUS_VALUES[2] += scene.get("moneychange", 0)
        EFFECTS_APPLIED = True

    screen.fill(BORDER_COLOR)
    if (GAME_STATE == "menu"):
        render_main_menu()
    else:
        render_status_panel(STATUS_COUNT)
        render_choice_panel(CHOICE_COUNT)
        render_narrative_window()

    pygame.display.flip()

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if GAME_STATE == "menu":
                if MENU_BUTTON_RECT.collidepoint(mx, my):
                    GAME_STATE = "game"
            else:
                for i, rect in enumerate(CHOICE_BUTTONS):
                    if rect.collidepoint(mx, my) and i < len(choices):
                        current_scene = scene["choices"][choices[i]]
                        TYPING_DONE = False
                        EFFECTS_APPLIED = False

pygame.quit()