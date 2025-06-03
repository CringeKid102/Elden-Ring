import pygame
from pygame.locals import *

class Animation:
    def __init__(self, sprite_sheet_path, frame_width, frame_height, scale=1):
        """
        Initialize the animation handler with a spritesheet.
        Args:
            sprite_sheet_path (str): Path to the spritesheet image
            frame_width (int): Width of each frame in pixels
            frame_height (int): Height of each frame in pixels
            scale (float): Scale factor for the sprites (default: 1)
        """
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale = scale
        self.animations = {}
        self.current_animation = None
        self.current_frame = 0
        self.animation_speed = 0.1  # Time between frames in seconds
        self.last_update = 0
        self.loop = True
        
    def extract_frames(self, row, num_frames, flip_x=False):
        """
        Extract frames from a specific row in the spritesheet.
        Args:
            row (int): Row number (0-based index)
            num_frames (int): Number of frames to extract
            flip_x (bool): Whether to flip frames horizontally
        Returns:
            list: List of pygame.Surface objects representing the frames
        """
        frames = []
        for col in range(num_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            frame.blit(self.sprite_sheet, (0, 0), 
                      (col * self.frame_width, row * self.frame_height, 
                       self.frame_width, self.frame_height))
            
            if flip_x:
                frame = pygame.transform.flip(frame, True, False)
                
            if self.scale != 1:
                new_width = int(self.frame_width * self.scale)
                new_height = int(self.frame_height * self.scale)
                frame = pygame.transform.scale(frame, (new_width, new_height))
                
            frames.append(frame)
        return frames
    
    def add_animation(self, name, frames, speed=None, loop=True):
        """
        Add an animation to the animation dictionary.
        Args:
            name (str): Name of the animation (e.g., "walk", "attack")
            frames (list): List of frames for the animation
            speed (float): Optional custom speed for this animation
            loop (bool): Whether the animation should loop
        """
        self.animations[name] = {
            'frames': frames,
            'speed': speed if speed is not None else self.animation_speed,
            'loop': loop
        }
        
    def set_animation(self, name):
        """Set the current animation if it's different from the current one."""
        if name != self.current_animation and name in self.animations:
            self.current_animation = name
            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            self.loop = self.animations[name]['loop']
            
    def get_current_frame(self):
        """Get the current frame of the current animation."""
        if self.current_animation is None or self.current_animation not in self.animations:
            return None
            
        now = pygame.time.get_ticks()
        animation = self.animations[self.current_animation]
        
        # Check if it's time to advance to the next frame
        if now - self.last_update > animation['speed'] * 1000:
            self.current_frame += 1
            self.last_update = now
            
            # Handle animation end
            if self.current_frame >= len(animation['frames']):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(animation['frames']) - 1
                    return animation['frames'][self.current_frame]
        
        return animation['frames'][self.current_frame]
    
    def is_animation_finished(self):
        """Check if a non-looping animation has finished."""
        if self.current_animation is None or self.loop:
            return False
            
        animation = self.animations[self.current_animation]
        return self.current_frame >= len(animation['frames']) - 1

