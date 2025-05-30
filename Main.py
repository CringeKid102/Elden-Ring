"""
Elden Ring
ICS3U
William Ding

Version History
April 17, 2025: Version 1
April 23, 2025: Version 2
April 25, 2025: Version 3
April 25, 2025: Version 3.1
April 29, 2025: Version 4
May 01, 2025: Version 5
May 05, 2025: Version 6
May 07, 2025: Version 7
May 09, 2025: Version 8
May 13, 2025: Version 8.1
May 14, 2025: Version 9
May 15, 2025: Version 10
May 20, 2025: Version 11
May 22, 2025: Version 12
May 28, 2025: Version 13 (animation)
"""

# ================== LIBRARIES =============
import pygame
import time
import random
from pygame.locals import *

# Initialize pygame and music
pygame.init()
pygame.mixer.init()

# ================== FUNCTIONS =============
def createSprite(image, x, y, center_pos=True, colorkey=None):
    """
    Create a sprite
    Args:
        image(str): the name of the image
        x(int): x position of the image
        y(int): y position of the image
        center_pos(bool): if True uses center position, if False uses bottomleft
        colorkey(tuple or None): color to make transparent
    Returns:
        sprite(sprite): the sprite of the image
    """
    sprite = pygame.sprite.Sprite()
    sprite.image = pygame.image.load(image+'.png').convert_alpha()
    sprite.rect = sprite.image.get_rect()
    if colorkey is not None:
        sprite.image.set_colorkey(colorkey, RLEACCEL)
    if center_pos:
        sprite.rect.center = (x, y)
    else:
        sprite.rect.bottomleft = (x, y)
    return sprite

def createAnimation(filename, frame_count x, y, center_pos=True, colorkey=None):
    animation = []
    for i in range(frame_count):
        animation.append(createSprite(f'{filename}/{i+1}', x, y, center_pos, colorkey))
    return animation

def updateButton(screen, buttonNormal, buttonHover, buttonPress):
    """
    When hovering a button, it will shine. When pressing a button, it will either exit, or start the game.
    Args:
        screen: the window of the game
        buttonNormal(sprite): the image for the normal button
        buttonHover(sprite): the image for the hovering button
        buttonPress(sprite): the image for the pressing button
    Returns:
        False(bool): if the burron was clicked or not
    """
    mouse_pos = pygame.mouse.get_pos()
    
    if buttonNormal.rect.collidepoint(mouse_pos):
        if pygame.mouse.get_pressed()[0]:  # Left Click
            screen.blit(buttonPress.image, buttonPress.rect)
            pygame.display.update(buttonNormal.rect)
            return True
        else:
            screen.blit(buttonHover.image, buttonHover.rect)
    else:
        screen.blit(buttonNormal.image, buttonNormal.rect)

    pygame.display.update(buttonNormal.rect)
    return False

def start(game_params, screen):
    """
    The title screen, includes the play and exit buttons.
    Args:
        game_params(dict): contains constants and variables such as SCREEN_WIDTH
        screen: the window of the game
    Returns:
        (str): used to update game_params['status']
    """
    title = createSprite('other/title', game_params['SCREEN_WIDTH'] // 2, 100, True)
    bg = pygame.image.load('other/title background.png') # Background for the title screen

    playNormal = createSprite('button/play normal', game_params['SCREEN_WIDTH']/2, 400, True)
    playHover = createSprite('button/play hover', game_params['SCREEN_WIDTH']/2, 400, True)
    playPress = createSprite('button/play press', game_params['SCREEN_WIDTH']/2, 400, True)

    exitNormal = createSprite('button/exit normal', game_params['SCREEN_WIDTH']/2, 550, True)
    exitHover = createSprite('button/exit hover', game_params['SCREEN_WIDTH']/2, 550, True)
    exitPress = createSprite('button/exit press', game_params['SCREEN_WIDTH']/2, 550, True)

    # Draw background sprites
    screen.blit(bg, (0, 0))
    screen.blit(title.image, title.rect)
    
    # Return which button was clicked
    if updateButton(screen, playNormal, playHover, playPress):
        fade_to_black(screen)
        return 'cutscene'
    elif updateButton(screen, exitNormal, exitHover, exitPress):
        return 'exit'
    return 'start'

def introCutscene(screen, i=1):
    if i > 20:
        return 'game'

    image = pygame.image.load(f'{i}.png')

    # Fade in the image
    result = fade_to_image(screen, image)
    if result == 'quit':
        return 'exit'
    elif result == 'skip':
        return introCutscene(screen, i + 1)
    
    # Display the image for 1 second (but check for events)
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 1000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            if event.type == pygame.KEYDOWN:
                return introCutscene(screen, i + 1)
        pygame.time.delay(10)

    # Fade out the image
    result = fade_to_black(screen, image)
    if result == 'quit':
        return 'exit'
    elif result == 'skip':
        return introCutscene(screen, i + 1)

    return introCutscene(screen, i + 1)

def fade_to_black(screen, image=None, alpha=0, fade_speed=5):
    if alpha > 255:
        return None
    
    # Check for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return 'quit'
        if event.type == KEYDOWN:
            return 'skip'
    
    black_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    black_surface.fill((0, 0, 0))
    black_surface.set_alpha(alpha)

    if image is not None:
        screen.blit(image, (0, 0))

    screen.blit(black_surface, (0, 0))
    pygame.display.flip()
    pygame.time.delay(10)

    return fade_to_black(screen, image, alpha + fade_speed, fade_speed)

def fade_to_image(screen, image=None, alpha=255, fade_speed=5):
    if alpha < 0:
        return None
    
    # Check for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return 'quit'
        if event.type == KEYDOWN:
            return 'skip'
    
    black_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    black_surface.fill((0, 0, 0))
    black_surface.set_alpha(alpha)

    if image is not None:
        screen.blit(image, (0, 0))

    screen.blit(black_surface, (0, 0))
    pygame.display.flip()
    pygame.time.delay(10)

    return fade_to_image(screen, image, alpha - fade_speed, fade_speed)

def updatePlayer(playerAnim, demon, pressed_keys, bg, collide_walls, game_params):


def updateBoss(demonAnim, player, bg, collide_walls, game_params):
    

# ================== GAME PARAMETERS =============
game_params = {
    # Screen Constants
    'SCREEN_WIDTH': 1280,
    'SCREEN_HEIGHT': 720,
    
    # Game State
    'status': 'game',
    
    # Colors
    'black': (0, 0, 0),
    
    # Player

    # Demon
}

# ================== INITIALIZATION =============
screen = pygame.display.set_mode([game_params['SCREEN_WIDTH'], game_params['SCREEN_HEIGHT']])
bg = pygame.image.load('chapel/background.png')

player

demon

# v means vertical and h means horizontal
# The number represents how many 64pixels (e.g, 1 = 64pixels and 3 = 192pixels)        
collide_walls = (
    # Chapel
    createSprite('wall/v2', 640, 1568),
)

# List instead of sprite group in order to find the rect.bottom and sort it with the player
image_walls = [
    # Seats
    createSprite('chapel/bench1', 640, 1800),
]

# Main game loop
# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_params['status'] == 'exit':
            running = False
        # Add escape key to exit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    pressed_keys = pygame.key.get_pressed()
    
    # State machine
    if game_params['status'] == 'start':
        game_params['status'] = start(game_params, screen)
    elif game_params['status'] == 'cutscene':
        game_params['status'] = introCutscene(screen)
    elif game_params['status'] == 'game':
        # Update game state
        player_hearts, boss_hearts = updatePlayer(player, boss, bg, collide_walls, game_params)
        game_params['hitting'] = updateBoss(boss, player, bg, collide_walls, game_params)
        
        # Calculate camera offset
        camera_offset = (
            player.rect.centerx - screen.get_width() // 2,
            player.rect.centery - screen.get_height() // 2
        )
        
        # Draw background
        screen.blit(bg, (-camera_offset[0], -camera_offset[1]))
        
        # Prepare sprites for rendering (sorted by y-position)
        render_sprites = image_walls + [player, boss]
        render_sprites.sort(key=lambda sprite: sprite.rect.bottom)
        
        # Draw all sprites
        for sprite in render_sprites:
            screen.blit(sprite.image, 
                       (sprite.rect.x - camera_offset[0], 
                        sprite.rect.y - camera_offset[1]))
        
        # Draw collision walls (for debugging)
        for wall in collide_walls:
            screen.blit(wall.image, 
                       (wall.rect.x - camera_offset[0], 
                        wall.rect.y - camera_offset[1]))
    
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
exit()