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
May 30, 2025: Version 14 (animation)
May 31, 2025: Version 15 (player and demon logic)
June 01, 2025: Version 16 (player and demon logic, better UI)
June 02, 2025: Version 17 (better UI and music)
"""

# ================== LIBRARIES =============
from math import e
from turtle import done
import pygame
import time
import os
from pygame import image
from pygame.locals import *
from Animation import Animation

# Initialize pygame, music and font
pygame.init()
pygame.mixer.init()
pygame.font.init()
my_font = pygame.font.SysFont('MinimalPixel2', 20)

# Background music
pygame.mixer.music.load('audio/title screen.mp3')
pygame.mixer.music.play(-1) # loop

# ================== FUNCTIONS =============
def createSprite(image, x, y, center_pos=True, colorkey=None):
    """
    Create a sprite
    Args:
        image(str): the name of the image file to load (without extension)
        x(int): x position of the sprite
        y(int): y position of the sprite
        center_pos(bool): whether to center the sprite at (x, y) or set bottom left (default: True)
        colorkey(tuple): color key for transparency (default: None)
    Returns:
        sprite(pygame.sprite.Sprite): a sprite object with the loaded image and position
    """
    sprite = pygame.sprite.Sprite()
    try:
        sprite.image = pygame.image.load(image+'.png').convert_alpha()
    except pygame.error as e:
        print(f"Error loading image '{image}.png': {e}")
        return None

    sprite.rect = sprite.image.get_rect()
    if colorkey is not None:
        sprite.image.set_colorkey(colorkey, RLEACCEL)
    if center_pos:
        sprite.rect.center = (x, y)
    else:
        sprite.rect.bottomleft = (x, y)
    return sprite

def createWall(coordinates):
    """
    Create walls based on a list of coordinates.
    Args:
        coordinates(list): list of tuples containing the coordinates of the walls
    Returns:
        walls(pygame.sprite.Group): a group of wall sprites created from the coordinates
    """
    walls = pygame.sprite.Group()
    for i in range(len(coordinates)):
        if coordinates[i] == coordinates[0]: # Create the first wall
            wall = createSprite('wall/vertical', coordinates[0][0], coordinates[0][1], False)
        else:
            if coordinates[i][0] > coordinates[i-1][0]: # horizontal wall to the right
                for x in range(0, coordinates[i][0]-coordinates[i-1][0]-20, 20):
                    wall = createSprite('wall/horizontal', coordinates[i-1][0]+x, coordinates[i][1], False)
                    walls.add(wall)
            elif coordinates[i][0] < coordinates[i-1][0]: # horizontal wall to the left
                for x in range(20, coordinates[i-1][0]-coordinates[i][0]-20, 20): # Start at 20 to avoid overlap
                    wall = createSprite('wall/horizontal', coordinates[i-1][0]-x, coordinates[i][1], False)
                    walls.add(wall)
            elif coordinates[i][1] > coordinates[i-1][1]: # vertical wall downwards
                for y in range(20, coordinates[i][1]-coordinates[i-1][1]-20, 20):
                    wall = createSprite('wall/vertical', coordinates[i][0], coordinates[i-1][1]+y, False)
                    walls.add(wall)
            elif coordinates[i][1] < coordinates[i-1][1]: # vertical wall upwards
                for y in range(0, coordinates[i-1][1]-coordinates[i][1]-20, 20):
                    wall = createSprite('wall/vertical', coordinates[i][0], coordinates[i-1][1]-y, False)
                    walls.add(wall)
    return walls

def playSound(sound_file, channel=0, loops=0, volume=1.0):
    """
    Play a sound
    Args:
        sound_file(str): the name of the sound file to play
        channel(int): the channel to play the sound on (default: 0)
        loops(int): number of times to loop the sound (default: 0, no loop)
        volume(float): volume level (0.0 to 1.0, default: 1.0)
    """
    try:
        pygame.mixer.Channel(channel).play(pygame.mixer.Sound(f'audio/{sound_file}'), loops=loops)
    except Exception as e:
        print(f"Error playing sound '{sound_file}': {e}")
    pygame.mixer.music.set_volume(volume)

def updateButton(screen, audioParams, buttonNormal, buttonHover, buttonPress, hover_key):
    """
    Update the button state based on mouse position and clicks.
    Args:
        screen: the window of the game
        audioParams(dict): contains audio parameters such as 'hover flags' and 'start'
        buttonNormal(sprite): the normal state of the button
        buttonHover(sprite): the hover state of the button
        buttonPress(sprite): the pressed state of the button
        hover_key(str): the key to update in gameParams['hover_flags']
    Returns:
        (bool): True if the button was clicked, False otherwise
    """
    mouse_pos = pygame.mouse.get_pos()
    button_clicked = False

    if buttonNormal.rect.collidepoint(mouse_pos): # Hovering over the button
        if pygame.mouse.get_pressed()[0]:  # Left Click
            screen.blit(buttonPress.image, buttonPress.rect)
            button_clicked = True
            if not audioParams['start']:
                playSound('start.mp3', 0)
                audioParams['start'] = True
        else:
            screen.blit(buttonHover.image, buttonHover.rect)
            if not audioParams['hover flags'][hover_key]:
                playSound('hover.mp3', 1)
                audioParams['hover flags'][hover_key] = True
    else:
        screen.blit(buttonNormal.image, buttonNormal.rect)
        audioParams['hover flags'][hover_key] = False

    return button_clicked

def fade_effect(screen, image=None, direction='in', mode='black', alpha=0, fade_speed=5):
    """
    Fade effect for the screen, can fade in or out with an image or black background.
    Args:
        screen: pygame screen surface
        image: optional image to fade in or out (default: None)
        direction(str): 'in' to fade in, 'out' to fade out (default: 'in')
        mode(str): 'black' for black background, 'image' for image background (default: 'black')
        alpha(int): initial alpha value (0-255), default is 0 for fade in and 255 for fade out
        fade_speed(int): speed of the fade effect (default: 5)
    """
    if direction not in ['in', 'out'] or mode not in ['black', 'image']:
        raise ValueError("Invalid direction or mode. Direction: 'in' or 'out'; Mode: 'black' or 'image'.")

    alpha = 0 if (alpha is None and direction == 'in') else 255 if alpha is None else alpha

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == KEYDOWN:
                return 'skip'
        
        # Fade to image
        if image and mode == 'image':
            image_copy = image.copy()
            image_copy.set_alpha(alpha if direction == 'in' else 255 - alpha)
            screen.blit(image_copy, (0, 0))
        # Fade to or from black
        elif image:
            screen.blit(image, (0, 0))
        
        # Create a fade surface
        fade_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        # Fade to black
        if mode == 'black':
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(alpha if direction == 'out' else 255 - alpha)
            screen.blit(fade_surface, (0,0))

        pygame.display.flip()
        pygame.time.delay(10)

        # Update alpha value
        alpha += fade_speed if direction == 'in' else -fade_speed
        if (direction == 'in' and alpha >= 255) or (direction == 'out' and alpha <= 0):
            done = True

    return None

def dialogue(screen, background_image, text, font, text_speed=1):
    """
    Dialogue system with typewriter effect using counter method.
    Args:
        screen: pygame screen surface
        background_image: background image to display
        text: dialogue text to display (single line)
        font: pygame font object
        text_speed: speed of typing (higher = slower, 3 is good default)
    Returns:
        'quit' if user wants to exit, 'skip' to skip cutscene, None when complete
    """
    screen_w, screen_h = screen.get_size()
    box_height = 80
    margin = 20
    padding = 20
    
    # Create dialogue box
    dialogue_box = pygame.Surface((screen_w - 2 * margin, box_height))
    dialogue_box.fill((0, 0, 0))
    dialogue_box.set_alpha(180)
    
    box_x, box_y = margin, screen_h - box_height - margin
    text_x, text_y = box_x + padding, box_y + padding
    
    counter = 0
    done = False
    
    # Pre-render continue prompt
    continue_prompt = font.render("Press ANY KEY to continue...", True, (200, 200, 200))
    prompt_x = box_x + dialogue_box.get_width() - continue_prompt.get_width() - padding
    prompt_y = box_y + box_height - continue_prompt.get_height() - 5
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == KEYDOWN:
                if not done:
                    # Skip typing animation
                    counter = text_speed * len(text)
                    done = True
                else:
                    # Continue to next scene
                    return None
        
        # Typewriter effect
        if counter < text_speed * len(text):
            counter += 1
        elif counter >= text_speed * len(text):
            done = True
        
        # Text snippet based on counter 
        snip = font.render(text[0:counter // text_speed], True, (255, 255, 255))
        
        screen.blit(background_image, (0, 0))
        screen.blit(dialogue_box, (box_x, box_y))
        screen.blit(snip, (text_x, text_y))
        
        # Continue prompt
        if done:
            screen.blit(continue_prompt, (prompt_x, prompt_y))
        
        pygame.display.flip()
        clock.tick(60)

def start(gameParams, screen, audioParams):
    """
    The title screen, includes the play and exit buttons.
    Args:
        gameParams(dict): contains constants and variables such as SCREEN_WIDTH
        screen: the window of the game
        audioParams(dict): contains audio parameters such as 'hover flags' and 'start'
    Returns:
        (str): used to update gameParams['status']
    """
    bg = pygame.image.load('other/title screen.png')
    frame = createSprite('button/frame', gameParams['SCREEN_WIDTH']/2, 462, True)

    # Create buttons
    startNormal = createSprite('button/start normal', gameParams['SCREEN_WIDTH']/2, 398, True)
    startHover = createSprite('button/start hover', gameParams['SCREEN_WIDTH']/2, 398, True)
    startPress = createSprite('button/start press', gameParams['SCREEN_WIDTH']/2, 400, True)
    
    optionNormal = createSprite('button/options normal', gameParams['SCREEN_WIDTH']/2, 462, True)
    optionHover = createSprite('button/options hover', gameParams['SCREEN_WIDTH']/2, 462, True)
    optionPress = createSprite('button/options press', gameParams['SCREEN_WIDTH']/2, 464, True)

    exitNormal = createSprite('button/exit normal', gameParams['SCREEN_WIDTH']/2, 526, True)
    exitHover = createSprite('button/exit hover', gameParams['SCREEN_WIDTH']/2, 526, True)
    exitPress = createSprite('button/exit press', gameParams['SCREEN_WIDTH']/2, 528, True)

    # Draw background
    screen.blit(bg, (0, 0))
    screen.blit(frame.image, frame.rect)
    
    # Return which button was clicked
    if updateButton(screen, audioParams, startNormal, startHover, startPress, 'start'):
        fade_effect(screen, direction='out')
        gameParams['start'] = False
        return 'cutscene'
    elif updateButton(screen, audioParams, exitNormal, exitHover, exitPress, 'exit'):
        return 'exit'
    elif updateButton(screen, audioParams, optionNormal, optionHover, optionPress, 'option'):
        return 'option'

    return 'start'

def optionsMenu(screen, font):
    """
    Options menu that is under construction, it will return to the start screen when clicked.
    Args:
        screen: the window of the game
        font(pygame.font.Font): the font to use for the text
    Returns:
        (str): used to update gameParams['status']
    """
    text = font.render("Under construction (Click to go back to start screen)", True, (255, 255, 255))
    text_rect = text.get_rect(center=(gameParams['SCREEN_WIDTH']/2, gameParams['SCREEN_HEIGHT']/2))
    screen.fill((0, 0, 0))
    screen.blit(text, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    if text_rect.collidepoint(mouse_pos):
        text = my_font.render("Under construction (Click to go back to start screen)", True, (255, 255, 0))
        screen.blit(text, text_rect)
        if pygame.mouse.get_pressed()[0]:
            return 'start'

    return 'option'

def introCutscene(screen, text, font, i=1):
    """
    Cutscene for the introduction of the game, which shows a series of images.
    Args:
        screen: the window of the game
        text(dict): dictionary containing the text for each scene
        font(pygame.font.Font): the font to use for the text
        i(int): the index of the image to show, starts at 1
    Returns:
        (str): if all scenes are shown or exit, it will update gameParams['status']
        function: if the user wants to skip the cutscene or go to the next scene, it will return the next scene
    """
    if i > 21:
        return 'game'

    image = pygame.image.load(f'scene/{i}.png')

    # Fade in the image
    result = fade_effect(screen, image)
    if result == 'quit':
        return 'exit'
    elif result == 'skip':
        return introCutscene(screen, text, font, i + 1)
    
    # Display scene with dialogue
    if i in text:
        result = dialogue(screen, image, text[i], font)
        if result == 'quit':
            return 'exit'
        elif result == 'skip':
            return introCutscene(screen, text, font, i + 1)
    else:
        # Display scene for 1 second
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < 1000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'exit'
                if event.type == pygame.KEYDOWN:
                    return introCutscene(screen, text, font, i + 1)
            pygame.time.delay(10)

    # Fade out the image
    result = fade_effect(screen, image, direction='out')
    if result == 'quit':
        return 'exit'
    elif result == 'skip':
        return introCutscene(screen, text, font, i + 1)

    return introCutscene(screen, text, my_font, i + 1)

def updatePlayer(pressed_keys, bg, collide_walls, gameParams, playerParams, demonParams, audioParams):
    """
    Update player state and animations based on input and game logic.
    Args:
        pressed_keys(list): list of currently pressed keys
        bg(pygame.Surface): background surface for the game
        collide_walls(list): list of walls that the player can collide with
        gameParams(dict): contains constants and variables such as SCREEN_WIDTH
        playerParams(dict): contains player parameters such as state, health, etc.
        demonParams(dict): contains demon parameters such as state, health, etc.
        audioParams(dict): contains audio parameters such as 'player running', 'player hit', etc.
    Returns:
        playerParams(dict): updated player parameters
        demonParams(dict): updated demon parameters
    """
    # Initilization
    current_time = pygame.time.get_ticks()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    player_rect = pygame.Rect(playerParams['pos'][0]-30, playerParams['pos'][1] - 44, 60, 88)
    demon_rect = pygame.Rect(demonParams['pos'][0]-60, demonParams['pos'][1] - 117, 120, 234)

    # Update facing direction based on mouse position
    playerParams['facing'] = 'l' if mouse_x < screen.get_width()//2 else 'r'
    if playerParams['state'] not in ['death', 'hit']:  # Don't interrupt these critical animations
        playerAnim.set_animation(f'{playerParams["facing"]}_{playerParams["state"]}')

    # ======= DEATH STATE ========
    if playerParams['health'] <= 0:
        if not audioParams['player death']:
            playSound('player death.mp3', 0)
            audioParams['player death'] = True
        if playerParams['state'] != 'death':
            playerParams['state'] = 'death'
            playerParams['death_start_time'] = current_time
            playerAnim.set_animation(f'{playerParams["facing"]}_hit')
            # Running stop when dying
            audioParams['player running'] = False
        
        else:  # Already in death state
            time_since_death = current_time - playerParams['death_start_time']
        
            if time_since_death > playerParams['hit_duration'] and time_since_death <= playerParams['hit_duration'] + 100:
                # Switch to death animation
                playerAnim.set_animation(f'{playerParams["facing"]}_death')
            
            elif time_since_death > playerParams['hit_duration'] + playerParams['death_duration']:
                gameParams['status'] = 'end'
            
        return playerParams, demonParams

    # ======= HIT STATE ========
    elif playerParams['state'] == 'hit':
        # Running stop when hit
        audioParams['player running'] = False
        if playerAnim.is_animation_finished() and current_time - playerParams['hit_time'] > playerParams['hit_duration']:
            playerParams['state'] = 'idle'
            playerParams['hitting'] = False
        return playerParams, demonParams

    # ======= ATTACK STATE ========
    elif playerParams['state'] in ['attack1', 'attack2', 'attack3']:
        # Running stop when attacking
        audioParams['player running'] = False
            
        # Calculate how far through the attack we are (0.0 to 1.0)
        attack_progress = (current_time - playerParams['attack_time']) / playerParams['attack_duration']
    
        # Check for chaining window (70% through current attack)
        if (mouse_pressed[0] and 0.7 <= attack_progress < 1.0 and 
            playerParams['state'] in ['attack1', 'attack2'] and 
            playerParams['stamina'] > 0):
            audioParams['player hit'] = False
            audioParams['player miss'] = False
            # Chain to next attack
            new_state = 'attack2' if playerParams['state'] == 'attack1' else 'attack3'
            playerParams['state'] = new_state
            playerParams['stamina'] -= 1
            playerParams['stamina_time'] = current_time
            playerParams['attack_time'] = current_time  # Reset timer for new attack
            playerParams['hitting'] = False
    
        # Check if attack is completely finished
        elif attack_progress >= 1.0:
            playerParams['state'] = 'idle'
            playerParams['hitting'] = False
    
        # Always update animation (this ensures it plays through completely)
        playerAnim.set_animation(f'{playerParams["facing"]}_{playerParams["state"]}')
    
        # Check for hit detection during active frames (30-80%)
        if 0.3 <= attack_progress <= 0.8 and demonParams['state'] not in ['hit', 'death'] and not playerParams['hitting']:
            if player_rect.colliderect(demon_rect):
                if not audioParams['player hit']:
                    playSound('player hit.mp3', 1)
                    audioParams['player hit'] = True
                demonParams['state'] = 'hit'
                demonParams['health'] -= 1
                playerParams['hitting'] = True
                demonParams['hit_time'] = current_time
            else:
                if not audioParams['player miss']:
                    playSound('player miss.mp3', 2)
                    audioParams['player miss'] = True
    
        return playerParams, demonParams

    # ======= BLOCK STATE ========
    if playerParams['state'] == 'block':
        # Running stop when blocking
        audioParams['player running'] = False
        if not mouse_pressed[2] or playerAnim.is_animation_finished():
            playerParams['state'] = 'idle'
        return playerParams, demonParams

    # ======= INPUT HANDLING ========
    # Attack input
    if mouse_pressed[0] and playerParams['stamina'] > 0:
        playerParams['state'] = 'attack1'
        playerParams['stamina'] -= 1
        playerParams['stamina_time'] = current_time
        playerParams['attack_time'] = current_time
        playerParams['hitting'] = False
        audioParams['player hit'] = False
        audioParams['player miss'] = False
        # Running stop when attacking
        audioParams['player running'] = False
    # Block input
    elif mouse_pressed[2] and playerParams['stamina'] > 0:
        playerParams['state'] = 'block'
        playerParams['stamina'] -= 1
        playerParams['stamina_time'] = current_time
        playerParams['block_time'] = current_time
    # Movement input
    else:
        moving = False
        speed = playerParams['r_speed'] if pressed_keys[K_LSHIFT] else playerParams['w_speed']
        old_pos = playerParams['pos'].copy()

        dx = 0
        dy = 0

        # Move up
        if pressed_keys[K_w] and playerParams['pos'][1] > 360:
            dy -= 1
            moving = True
        # Move down
        if pressed_keys[K_s] and playerParams['pos'][1] < bg.get_height() - 360:
            dy += 1
            moving = True
        # Move left
        if pressed_keys[K_a] and playerParams['pos'][0] > 640:
            dx -= 1
            moving = True
        # Move right
        if pressed_keys[K_d] and playerParams['pos'][0] < bg.get_width() - 640:
            dx += 1
            moving = True

        # Diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Move on x axis
        playerParams['pos'][0] += dx * speed
        temp_sprite = pygame.sprite.Sprite()
        temp_sprite.rect = pygame.Rect(playerParams['pos'][0] - 30, old_pos[1] + 12, 60, 32)
        if pygame.sprite.spritecollideany(temp_sprite, collide_walls):
            playerParams['pos'][0] = old_pos[0]

        # Move on Y axis
        playerParams['pos'][1] += dy * speed
        temp_sprite.rect = pygame.Rect(playerParams['pos'][0] - 30, playerParams['pos'][1] + 12, 60, 32)
        if pygame.sprite.spritecollideany(temp_sprite, collide_walls):
            playerParams['pos'][1] = old_pos[1]

        # Update animation state and running sounds
        if moving:
            new_state = 'run' if pressed_keys[K_LSHIFT] else 'walk'
            if playerParams['state'] != new_state:
                playerParams['state'] = new_state
                
            # Running sound
            if new_state == 'run':
                if not audioParams['player running']:
                    # Start playing running sound on loop
                    playSound('player running.mp3', 5, loops=-1)
                    audioParams['player running'] = True
            else:  # walking
                audioParams['player running'] = False
        else:
            # Running stop when not moving
            audioParams['player running'] = False
                
            if playerParams['state'] != 'idle':
                playerParams['state'] = 'idle'

    # Update player animation
    playerAnim.set_animation(f'{playerParams["facing"]}_{playerParams["state"]}')

    # Update current frame in playerParams
    current_player_frame = playerAnim.get_current_frame()
    if current_player_frame:
        playerParams['current_frame'].image = current_player_frame
        playerParams['current_frame'].rect = current_player_frame.get_rect(center=playerParams['pos'])

    # Reset stamina after a certain amount of time
    if playerParams['stamina'] < 4 and current_time - playerParams['stamina_time'] > playerParams['stamina_duration']:
        playerParams['stamina'] += 1
        playerParams['stamina_time'] = current_time

    return playerParams, demonParams


def updateBoss(collide_walls, gameParams, playerParams, demonParams, audioParams):
    """
    Update demon state and animations based on player position and game logic.
    Args:
        pressed_keys(list): list of currently pressed keys
        bg(pygame.Surface): background surface for the game
        collide_walls(list): list of walls that the demon can collide with
        gameParams(dict): contains constants and variables such as SCREEN_WIDTH
        playerParams(dict): contains player parameters such as state, health, etc.
        demonParams(dict): contains demon parameters such as state, health, etc.
        audioParams(dict): contains audio parameters such as 'demon running', 'demon hit', etc.
    Returns:
        playerParams(dict): updated player parameters
        demonParams(dict): updated demon parameters
    """
    # Initialization
    current_time = pygame.time.get_ticks()
    player_rect = pygame.Rect(playerParams['pos'][0]-30, playerParams['pos'][1] - 44, 60, 88)
    demon_rect = pygame.Rect(demonParams['pos'][0]-60, demonParams['pos'][1] - 117, 120, 234)
    dx = playerParams['pos'][0] - demonParams['pos'][0]
    dy = playerParams['pos'][1] - demonParams['pos'][1]
    distance = (dx**2 + dy**2)**0.5

    # ======= DEATH STATE ========
    if demonParams['health'] <= 0:
        if not audioParams['demon death']:
            playSound('demon death.mp3', 3)
            audioParams['demon death'] = True
        if demonParams['state'] != 'death':
            demonParams['state'] = 'death'
            demonParams['death_start_time'] = current_time
            demonAnim.set_animation(f'{demonParams["facing"]}_hit')
            # Running stop when dying
            audioParams['demon running'] = False
        
        else:  # Already in death state
            time_since_death = current_time - demonParams['death_start_time']
        
            if time_since_death > demonParams['hit_duration'] and time_since_death <= demonParams['hit_duration'] + 100:
                # Switch to death animation
                demonAnim.set_animation(f'{demonParams["facing"]}_death')
            
            elif time_since_death > demonParams['hit_duration'] + demonParams['death_duration']:
                gameParams['status'] = 'end'
            
        return playerParams, demonParams

    # ======= HIT STATE ========
    elif demonParams['state'] == 'hit':
        # Running stop when hit
        audioParams['demon running'] = False
        if demonAnim.current_animation != f'{demonParams["facing"]}_hit':
            demonAnim.set_animation(f'{demonParams["facing"]}_hit')
        if demonAnim.is_animation_finished() and current_time - demonParams['hit_time'] > demonParams['hit_duration']:
            demonParams['state'] = 'idle'
            demonParams['hitting'] = False
        return playerParams, demonParams

    # ======= ATTACK STATE ========
    elif demonParams['state'] == 'attack':
        # Running stop when attacking
        audioParams['demon running'] = False
        
        if demonAnim.is_animation_finished():
            demonParams['state'] = 'idle'
            demonParams['hitting'] = False
            demonAnim.set_animation(f'{demonParams["facing"]}_idle')
        else:
            # Calculate which frame of the attack animation we're on
            animation = demonAnim.animations[demonAnim.current_animation]
            total_frames = len(animation['frames'])
            attack_progress = (current_time - demonParams['attack_time']) / demonParams['attack_duration']
            current_frame_index = int(attack_progress * total_frames)

            damage_frames = range(10, 13)
    
            # Create attack rect
            if demonParams['facing'] == 'r':
                attack_x = demonParams['pos'][0] - 180
                demon_attack_rect = pygame.Rect(attack_x, demonParams['pos'][1] - 130, 180, 260)
            else:  # facing left
                attack_x = demonParams['pos'][0] + 30
                demon_attack_rect = pygame.Rect(attack_x, demonParams['pos'][1] - 130, 180, 260)
    
            # Check for attack hit only during damage frames
            if (current_frame_index in damage_frames and 
                demon_attack_rect.colliderect(player_rect)):
        
                if not demonParams['hitting']:  # Only register one hit per attack
                    if playerParams['state'] == 'block' and (
                        (playerParams['facing'] == 'r' and demonParams['facing'] == 'l') or 
                        (playerParams['facing'] == 'l' and demonParams['facing'] == 'r')):
                        demonParams['hitting'] = True
                        playSound('player block.mp3', 4)
                    else:
                        playerParams['health'] -= 1
                        playerParams['state'] = 'hit'
                        demonParams['hitting'] = True
                        playerParams['hit_time'] = current_time
                        playerAnim.set_animation(f'{playerParams["facing"]}_hit')
                        playSound('player hit.mp3', 4)
            elif (current_frame_index >= max(damage_frames) and 
                    demonParams['hitting']):
                # Reset hitting after damage frames
                demonParams['hitting'] = False
    
        return playerParams, demonParams
    
    # Update facing direction
    demonParams['facing'] = 'l' if dx > 0 else 'r'
    if demonParams['state'] not in ['death', 'hit']:  # Don't interrupt these critical animations
        demonAnim.set_animation(f'{demonParams["facing"]}_{demonParams["state"]}')

    # ======= BEHAVIOR LOGIC ========
    if (distance < demonParams['attack_range'] and playerParams['state'] != 'death' and 
        playerParams['pos'][1] - 50 <= demonParams['pos'][1] <= playerParams['pos'][1] + 50):
        # Running stop when attacking
        audioParams['demon running'] = False
        # Play demon growl before attacking (occasionally)
        if not audioParams['demon growl']:
            playSound('demon growl.mp3', 7)
            audioParams['demon growl'] = True
        demonParams['state'] = 'attack'
        demonParams['attack_time'] = current_time
        demonParams['hitting'] = False
        demonAnim.set_animation(f'{demonParams["facing"]}_attack')
    elif distance < demonParams['chase_range'] and playerParams['state'] != 'death':
        # Reset growl flag when not attacking
        audioParams['demon growl'] = False
        
        demonParams['state'] = 'run'
        old_pos = demonParams['pos'].copy()
        
        # Handle demon running sound
        if not audioParams['demon running']:
            playSound('demon running.mp3', 6, loops=-1)
            audioParams['demon running'] = True
        
        # Move towards player
        if demonParams['facing'] == 'l':
            # Boss is facing left, offset 50 pixels to the left
            target_x = playerParams['pos'][0] - 100
        else:
            # Boss is facing right, offset 50 pixels to the right  
            target_x = playerParams['pos'][0] + 100
        
        target_y = playerParams['pos'][1]
        
        # Calculate direction to target position
        target_dx = target_x - demonParams['pos'][0]
        target_dy = target_y - demonParams['pos'][1]
        target_distance = (target_dx**2 + target_dy**2)**0.5
        
        # Move towards target position (with offset)
        if target_distance > 0:
            move_x = (target_dx / target_distance) * demonParams['speed']
            move_y = (target_dy / target_distance) * demonParams['speed']
            demonParams['pos'][0] += move_x
            demonParams['pos'][1] += move_y

        # Keep within bounds
        demonParams['pos'][0] = max(640, min(bg.get_width() - 640, demonParams['pos'][0]))
        demonParams['pos'][1] = max(360, min(bg.get_height() - 360, demonParams['pos'][1]))

        # Check wall collision
        temp_sprite = pygame.sprite.Sprite()
        temp_sprite.rect = pygame.Rect(demonParams['pos'][0] - 60, demonParams['pos'][1] - 117, 120, 234)
        if pygame.sprite.spritecollideany(temp_sprite, collide_walls):
            demonParams['pos'] = old_pos.copy()

            # Try moving only horizontally
            demonParams['pos'][0] += move_x
            temp_sprite.rect.x = demonParams['pos'][0] - 60
            if pygame.sprite.spritecollideany(temp_sprite, collide_walls):
                demonParams['pos'][0] = old_pos[0]
                
            # Try moving only vertically
            demonParams['pos'][1] += move_y
            temp_sprite.rect.y = demonParams['pos'][1] - 117
            if pygame.sprite.spritecollideany(temp_sprite, collide_walls):
                demonParams['pos'][1] = old_pos[1]

        demonAnim.set_animation(f'{demonParams["facing"]}_run')
    else:
        # Reset audio when idle
        audioParams['demon growl'] = False
        audioParams['demon running'] = False
            
        demonParams['state'] = 'idle'
        demonAnim.set_animation(f'{demonParams["facing"]}_idle')

    # Update current frame in demonParams
    current_demon_frame = demonAnim.get_current_frame()
    if current_demon_frame:
        demonParams['current_frame'].image = current_demon_frame
        demonParams['current_frame'].rect = current_demon_frame.get_rect(center=demonParams['pos'])

    return playerParams, demonParams

def updatePlayerUI(screen, healthbar, staminabar, playerParams):
    """
    Update the player UI with health and stamina bars.
    Args:
        screen: the window of the game
        healthbar(list): list of health bar sprites
        staminabar(list): list of stamina bar sprites
        playerParams(dict): contains player parameters such as health, stamina, etc.
    """
    frame = createSprite('player/frame', 40, 136, False)
    screen.blit(frame.image, frame.rect)
    # Health
    if playerParams['health'] > 0:
        screen.blit(healthbar[playerParams['health']-1].image, healthbar[playerParams['health']-1].rect)
    # Stamina
    if playerParams['stamina'] > 0:
        screen.blit(staminabar[playerParams['stamina']-1].image, staminabar[playerParams['stamina']-1].rect)

def updateDemonUI(screen, healthbar, demonParams, gameParams):
    """
    Update the demon UI with health bar.
    Args:
        screen: the window of the game
        healthbar(list): list of health bar sprites
        demonParams(dict): contains demon parameters such as health, etc.
        gameParams(dict): contains game parameters such as SCREEN_WIDTH
    """
    frame = createSprite('demon/frame', gameParams['SCREEN_WIDTH']//2, 600)
    screen.blit(frame.image, frame.rect)
    # Health
    if demonParams['health'] > 0:
        screen.blit(healthbar[demonParams['health']-1].image, healthbar[demonParams['health']-1].rect)

def endMenu(screen, playerParams, demonParams, gameParams, audioParams):
    """
    Display the end menu with defeat or victory screen and buttons to restart or exit.
    Args:
        screen: the window of the game
        playerParams(dict): contains player parameters such as state, health, etc.
        demonParams(dict): contains demon parameters such as state, health, etc.
        gameParams(dict): contains game parameters such as SCREEN_WIDTH, end status, etc.
        audioParams(dict): contains audio parameters such as 'defeat', 'victory', etc.
    Returns:
        (str): 'game' if restart button is clicked, 'exit' if exit button is clicked, or 'end' to continue showing the end menu
    """
    # Load background image
    if playerParams['state'] == 'death':
        if not audioParams['defeat']:
            playSound('defeat.mp3', 0)
            audioParams['defeat'] = True
        image = createSprite('other/defeat', 0, 0, False)
    elif demonParams['state'] == 'death':
        if not audioParams['victory']:
            playSound('victory.mp3', 0)
            audioParams['victory'] = True
        image = createSprite('other/victory', 0, 0, False)
    

    if not gameParams['end']:
        result = fade_effect(screen)
        if result == 'quit':
            return 'exit'
        if result == None:
            result2 = fade_effect(screen, image.image, mode='image')
            if result2 == 'quit':
                return 'exit'
            if result2 == None:
                gameParams['end'] = True
    else:
        screen.blit(image.image, (0, 0))

    # Create buttons
    restartNormal = createSprite('button/restart normal', gameParams['SCREEN_WIDTH']/2, 526, True)
    restartHover = createSprite('button/restart hover', gameParams['SCREEN_WIDTH']/2, 526, True)
    restartPress = createSprite('button/restart press', gameParams['SCREEN_WIDTH']/2, 528, True)

    exitNormal = createSprite('button/exit normal', gameParams['SCREEN_WIDTH']/2, 590, True)
    exitHover = createSprite('button/exit hover', gameParams['SCREEN_WIDTH']/2, 590, True)
    exitPress = createSprite('button/exit press', gameParams['SCREEN_WIDTH']/2, 592, True)
    
    # Return which button was clicked
    if updateButton(screen, audioParams, restartNormal, restartHover, restartPress, 'restart'):
        # Reset game parameters
        gameParams['end'] = False
        gameParams['status'] = 'start'
        playerParams['health'] = 7
        playerParams['stamina'] = 4
        demonParams['health'] = 20
        playerParams['pos'] = [1836, 3100]
        demonParams['pos'] = [bg.get_width() // 2, 1600]
        playerAnim.set_animation('r_idle')
        demonAnim.set_animation('r_idle')
        gameParams['victory'] = False
        gameParams['defeat'] = False
        gameParams['end'] = False
        fade_effect(screen, direction='out')
        return 'game'
    elif updateButton(screen, audioParams, exitNormal, exitHover, exitPress, 'exit'):
        return 'exit'

    cursor_img_rect.topleft = pygame.mouse.get_pos()
    screen.blit(cursor_img, cursor_img_rect)

    return 'end'

# ================== GAME PARAMETERS =============
audioParams = {
    # Title screen sounds
    'start': False,
    'hover flags': {'start': False, 'option': False, 'exit': False, 'restart': False},

    # End menu sounds
    'defeat': False,
    'victory': False,

    # Background music
    'bossfight': False,
    
    # Death sounds
    'player death': False,
    'demon death': False,
    
    # Attack/Miss sounds
    'player hit': False,
    'player miss': False,
    
    # Running sounds
    'player running': False,
    'demon running': False,
    
    # Demon behavior
    'demon growl': False,
}    

playerParams = {
    'state' : 'idle',
    'prev_state' : 'idle',
    'facing' : 'l',
    'health' : 7,
    'stamina' : 4,
    'hit_time' : None,
    'attack_time' : None,
    'block_time' : None,
    'death_time' : None,
    'stamina_time' : None,
    'last_frame_time' : 0,
    'hitting' : False,
    'w_speed' : 3,
    'r_speed' : 5,
    'attack_duration' : 700,
    'hit_duration' : 400,
    'block_duration' : 600,
    'death_duration' : 1200,
    'stamina_duration' : 3000,
    'frame' : 0,
    'pos': [1836, 3100],
}

demonParams = {
    'state' : 'idle',
    'prev_state' : 'idle',
    'facing' : 'r',
    'health' : 20,
    'hit_time' : None,
    'attack_time' : None,
    'death_time' : None,
    'last_frame_time' : 0,
    'hitting' : False,
    'speed' : 6,
    'attack_duration' : 750,
    'hit_duration' : 500,
    'death_duration' : 2200,
    'frame' : 0,
    'attack_range' : 200,
    'chase_range' : 400,
    'pos': [2027, 1600],
}

gameParams = {
    # Screen Constants
    'SCREEN_WIDTH': 1280,
    'SCREEN_HEIGHT': 720,
    
    # Game State
    'status': 'start',
    
    # Colors
    'black': (0, 0, 0),

    # Defeat/Victory images
    'end': False,
}
# ================= INITIALIZATION =============
screen = pygame.display.set_mode([gameParams['SCREEN_WIDTH'], gameParams['SCREEN_HEIGHT']])
bg = pygame.image.load('dark dimension/background.png')

# ================== ANIMATION =============
playerAnim = Animation('player/spritesheet.png', 61, 44, scale=2)
demonAnim = Animation('demon/spritesheet.png', 262, 117, scale=2)

# Add player animations (adjust rows based on your spritesheet layout)
# Assuming rows are organized as: idle, walk, run, attack1, attack2, attack3, block, hit, death
playerAnim.add_animation('l_idle', playerAnim.extract_frames(0, 7, True), 0.1)
playerAnim.add_animation('l_walk', playerAnim.extract_frames(1, 8, True), 0.1)
playerAnim.add_animation('l_run', playerAnim.extract_frames(2, 8, True), 0.1)
playerAnim.add_animation('l_attack1', playerAnim.extract_frames(3, 6, True), 0.12, False)
playerAnim.add_animation('l_attack2', playerAnim.extract_frames(4, 5, True), 0.1, False)
playerAnim.add_animation('l_attack3', playerAnim.extract_frames(5, 6, True), 0.12, False)
playerAnim.add_animation('l_block', playerAnim.extract_frames(6, 6, True), 0.1, False)
playerAnim.add_animation('l_hit', playerAnim.extract_frames(7, 4, True), 0.1, False)
playerAnim.add_animation('l_death', playerAnim.extract_frames(8, 11, True), 0.1, False)

# Right-facing animations (same as left but not flipped)
playerAnim.add_animation('r_idle', playerAnim.extract_frames(0, 7, False), 0.1)
playerAnim.add_animation('r_walk', playerAnim.extract_frames(1, 8, False), 0.1)
playerAnim.add_animation('r_run', playerAnim.extract_frames(2, 8, False), 0.1)
playerAnim.add_animation('r_attack1', playerAnim.extract_frames(3, 6, False), 0.12, False)
playerAnim.add_animation('r_attack2', playerAnim.extract_frames(4, 5, False), 0.1, False)
playerAnim.add_animation('r_attack3', playerAnim.extract_frames(5, 6, False), 0.12, False)
playerAnim.add_animation('r_block', playerAnim.extract_frames(6, 6, False), 0.1, False)
playerAnim.add_animation('r_hit', playerAnim.extract_frames(7, 4, False), 0.1, False)
playerAnim.add_animation('r_death', playerAnim.extract_frames(8, 11, False), 0.1, False)

# Add demon animations (adjust rows based on your spritesheet layout)
demonAnim.add_animation('l_idle', demonAnim.extract_frames(0, 7, True), 0.1)
demonAnim.add_animation('l_run', demonAnim.extract_frames(1, 12, True), 0.1)
demonAnim.add_animation('l_attack', demonAnim.extract_frames(2, 15, True), 0.05, False)
demonAnim.add_animation('l_hit', demonAnim.extract_frames(3, 4, True), 0.1, False)
demonAnim.add_animation('l_death', demonAnim.extract_frames(4, 22, True), 0.1, False)

# Right-facing animations
demonAnim.add_animation('r_idle', demonAnim.extract_frames(0, 7, False), 0.1)
demonAnim.add_animation('r_run', demonAnim.extract_frames(1, 12, False), 0.1)
demonAnim.add_animation('r_attack', demonAnim.extract_frames(2, 15, False), 0.05, False)
demonAnim.add_animation('r_hit', demonAnim.extract_frames(3, 4, False), 0.1, False)
demonAnim.add_animation('r_death', demonAnim.extract_frames(4, 22, False), 0.1, False)

# ================= MORE GAME PARAMETERS =============
# Set initial animations
playerAnim.set_animation('r_idle')
demonAnim.set_animation('r_idle')

# Get current frames and create rects
player_frame = playerAnim.get_current_frame()
demon_frame = demonAnim.get_current_frame()

# Create sprite objects or rects for collision/positioning
playerParams['current_frame'] = pygame.sprite.Sprite()
playerParams['current_frame'].image = player_frame
playerParams['current_frame'].rect = player_frame.get_rect(center=playerParams['pos'])

demonParams['current_frame'] = pygame.sprite.Sprite()
demonParams['current_frame'].image = demon_frame
demonParams['current_frame'].rect = demon_frame.get_rect(center=demonParams['pos'])

# ================== MORE INITIALIZATION =============
# Coordinates for walls outside of the map
coordinates =  [
    [1512, 3629], [1512, 2378], [1549, 2378], [1549, 2410], [1608, 2410], [1608, 2314],
    [1702, 2314], [1702, 2188], [1542, 2188], [1542, 2125], [1510, 2125], [1510, 1707],
    [1416, 1707], [1416, 1676], [1318, 1676], [1318, 1612], [1288, 1612], [1288, 1513],
    [1318, 1513], [1318, 1481], [1384, 1481], [1384, 1417], [1479, 1417], [1479, 1352],
    [1510, 1352], [1510, 1194], [2475, 1194], [2475, 1257], [2570, 1257], [2570, 1320],
    [2636, 1320], [2636, 1353], [2700, 1353], [2700, 1482], [2762, 1482], [2762, 2092],
    [2634, 2092], [2634, 2191], [2605, 2191], [2605, 2248], [2634, 2248], [2634, 2315],
    [2670, 2315], [2670, 2347], [2696, 2347], [2696, 2407], [2762, 2407], [2762, 3628],
    [2502, 3628], [2502, 3565], [2409, 3565], [2409, 3532], [2343, 3532], [2343, 3500],
    [2220, 3500], [2220, 3532], [2155, 3532], [2155, 3629], [1513, 3629]
]   
# Coordinates for the hole in the wall
hole_coordinates = [
    [2157, 2889], [2157, 2858], [2091, 2858], [2091, 2825], [2029, 2825], [2029, 2790], [1998, 2790], [1998, 2703], [2029, 2703], [2029, 2638],  
    [2059, 2638], [2059, 2606], [2185, 2606], [2185, 2638], [2216, 2638], [2216, 2668], [2247, 2668], [2247, 2858], [2216, 2858], [2216, 2889],  
    [2158, 2889]
]
collide_walls = createWall(coordinates)
hole = createWall(hole_coordinates)
cave = createWall([[1690, 3100], [1690, 2908], [1882, 2908], [1882, 3100], [1691, 3100]])
collide_walls.add(hole, cave)

# List instead of sprite group in order to find the rect.bottom and sort it with the player
image_walls = [
    # Structures
    createSprite('dark dimension/cave', 1690, 3100, False),
    createSprite('dark dimension/castle', 1520, 1230, False),

    # Grass
    createSprite('dark dimension/grass/1', 1386, 1643, False),
    createSprite('dark dimension/grass/2', 2504, 3272, False),
    createSprite('dark dimension/grass/3', 1644, 2652, False),
    createSprite('dark dimension/grass/4', 2654, 1805, False),
    createSprite('dark dimension/grass/5', 1654, 2585, False),
    createSprite('dark dimension/grass/6', 2358, 2836, False),
    createSprite('dark dimension/grass/7', 1664, 2616, False),
    createSprite('dark dimension/grass/8', 2587, 1490, False),
    createSprite('dark dimension/grass/9', 2251, 2536, False),
    createSprite('dark dimension/grass/9', 1684, 3350, False),

    # Rocks
    createSprite('dark dimension/rock/1', 1621, 2563, False),
    createSprite('dark dimension/rock/1', 2098, 2010, False),
    createSprite('dark dimension/rock/2', 1847, 1593, False),
    createSprite('dark dimension/rock/2', 2001, 3480, False),
    createSprite('dark dimension/rock/3', 2298, 3366, False),
    createSprite('dark dimension/rock/4', 2167, 2366, False),
    createSprite('dark dimension/rock/5', 2678, 1976, False),
    createSprite('dark dimension/rock/5', 2081, 1836, False),
    createSprite('dark dimension/rock/6', 1354, 1516, False),
    createSprite('dark dimension/rock/7', 1861, 2713, False),
    createSprite('dark dimension/rock/7', 2701, 3553, False),

    # Crystals
    createSprite('dark dimension/crystal/1', 2294, 1926, False),
    createSprite('dark dimension/crystal/2', 1711, 1526, False),
    createSprite('dark dimension/crystal/2', 1594, 2076, False),
    createSprite('dark dimension/crystal/3', 2494, 2213, False),
    createSprite('dark dimension/crystal/4', 2038, 2483, False),
    createSprite('dark dimension/crystal/5', 1581, 2710, False),
    createSprite('dark dimension/crystal/6', 2034, 3206, False),
    createSprite('dark dimension/crystal/7', 2051, 3146, False),
    createSprite('dark dimension/crystal/8', 1741, 2893, False),
    createSprite('dark dimension/crystal/9', 2034, 3536, False),

    # Floating crystals
    createSprite('dark dimension/floating crystal/1', 2058, 3110, False),
    createSprite('dark dimension/floating crystal/1', 2511, 1916, False),
    createSprite('dark dimension/floating crystal/2', 2667, 3313, False),
    createSprite('dark dimension/floating crystal/2', 1634, 2510, False),
    createSprite('dark dimension/floating crystal/2', 1627, 1796, False),
    createSprite('dark dimension/floating crystal/3', 1921, 3533, False),
    createSprite('dark dimension/floating crystal/3', 2678, 2006, False),
    createSprite('dark dimension/floating crystal/3', 1558, 1473, False),

    # Floating rocks
    createSprite('dark dimension/floating rock/1', 2254, 2583, False),
    createSprite('dark dimension/floating rock/1', 2291, 1837, False),
    createSprite('dark dimension/floating rock/1', 1678, 1687, False),
    createSprite('dark dimension/floating rock/2', 2458, 3013, False),
    createSprite('dark dimension/floating rock/2', 2411, 1880, False),

    # Statues
    createSprite('dark dimension/statue', 2061, 2447, False),
    createSprite('dark dimension/statue', 1947, 3567, False),
]

# Create player and demon UI sprites
player_healthbar = [createSprite(f'player/health/{i}', 144, 60, False) for i in range(7)]
player_staminabar = [createSprite(f'player/stamina/{i}', 144, 84, False) for i in range(4)]
demon_healthbar = [createSprite(f'demon/health/{i}', gameParams['SCREEN_WIDTH']//2 - 380, 610, False) for i in range(20)]

# Dialgue text for the intro cutscene
dialogue_text = {
    1: "The fallen leaves tell a story.",
    2: "The great Elden Ring was shattered.",
    3: "In our home, across the fog, in the Lands Between.",
    4: "Now, Queen Marika the Eternal is nowhere to be found.",
    5: "and in the night of the Black Knives, Godwyn the Golden was slain.",
    6: "Soon, Marika's offspring, demigods all, claimed the shards of the Elden Ring.",
    7: "The mad taint of their newfound strength triggered a war, the Shattering.",
    8: "A war from which no lord arose.", 
    9: "A war leading to abandonment by the Greater Will.",
    10: "Arise now, ye tarnished.",
    11: "Ye dead who yet live.",
    12: "The call of long-lost grace speaks to us all.",
    13: "Hoarah Loux, chieftan of the badlands.",
    14: "The ever-brilliant Goldmask.",
    15: "Fia, the Deathbed Companion.",
    16: "The loathsome Dung Eater.",
    17: "And Sir Gideon Ofnir, the All-Knowing.",
    18: "And one other whom Grace would again bless.",
    19: "A tarnished of no renown.",
    20: "Cross the fog to the Lands Between.",
    21: "to stand before the Elden Ring, and become the Elden Lord.",
}

# ================== LOAD CURSOR =============
pygame.mouse.set_visible(False)  # Hide the mouse cursor
cursor_img = pygame.image.load('cursor/leather glove.png').convert_alpha()
cursor_img_rect = cursor_img.get_rect()

# ================== MAIN GAME LOOP =============
clock = pygame.time.Clock()
running = True
debug_frame_count = 0

while running:
    debug_frame_count += 1
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif gameParams['status'] == 'exit':
            running = False
        # Add escape key to exit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    pressed_keys = pygame.key.get_pressed()
    
    # State machine
    if gameParams['status'] == 'start':
        gameParams['status'] = start(gameParams, screen, audioParams)
    elif gameParams['status'] == 'cutscene':
        gameParams['status'] = introCutscene(screen, dialogue_text, my_font)
    elif gameParams['status'] == 'option':
        gameParams['status'] = optionsMenu(screen, my_font)
    elif gameParams['status'] == 'game':
        if not audioParams['bossfight']:
            pygame.mixer.music.load('audio/bossfight.mp3')
            pygame.mixer.music.play(-1)
            audioParams['bossfight'] = True

        # Update game state
        playerParams, demonParams = updatePlayer(pressed_keys, bg, collide_walls, gameParams, playerParams, demonParams, audioParams)
        playerParams, demonParams = updateBoss(collide_walls, gameParams, playerParams, demonParams, audioParams)
        
        player = playerParams['current_frame']
        demon = demonParams['current_frame']

        # Calculate camera offset
        camera_offset = (
            player.rect.centerx - screen.get_width() // 2,
            player.rect.centery - screen.get_height() // 2
        )
        
        # Draw background
        screen.blit(bg, (-camera_offset[0], -camera_offset[1]))

        # Update current frames
        current_player_frame = playerAnim.get_current_frame()
        current_demon_frame = demonAnim.get_current_frame()

        if current_player_frame:
            playerParams['current_frame'].image = current_player_frame
        if current_demon_frame:
            demonParams['current_frame'].image = current_demon_frame
        
        # Prepare sprites for rendering (sorted by y-position)
        render_sprites = image_walls + [player, demon]
        render_sprites.sort(key=lambda sprite: sprite.rect.bottom)
        
        # Draw all sprites with debug rectangles
        for sprite in render_sprites:
            sprite_screen_pos = (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1])
            screen.blit(sprite.image, sprite_screen_pos)

        updateDemonUI(screen, demon_healthbar, demonParams, gameParams)
        updatePlayerUI(screen, player_healthbar, player_staminabar, playerParams)

    elif gameParams['status'] == 'end':
        gameParams['status'] = endMenu(screen, playerParams, demonParams, gameParams, audioParams)
        
    elif gameParams['status'] == 'exit':
        running = False
    
    # Custom cursor
    cursor_img_rect.topleft = pygame.mouse.get_pos()
    screen.blit(cursor_img, cursor_img_rect)
    
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
exit()