import time
import math
import random
import pygame

def ease_out_cubic(t):
    """Cubic ease-out formula for smooth card sliding."""
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3)

class ActiveCardAnimation:
    def __init__(self, card_surface, start_pos, target_pos, duration=0.25, on_complete=None):
        self.card_surface = card_surface
        self.start_x, self.start_y = start_pos
        self.target_x, self.target_y = target_pos
        self.duration = max(0.05, duration)
        self.start_time = time.time()
        self.on_complete = on_complete
        self.finished = False

    @property
    def current_pos(self):
        elapsed = time.time() - self.start_time
        t = elapsed / self.duration
        if t >= 1.0:
            self.finished = True
            if self.on_complete:
                self.on_complete()
            return (self.target_x, self.target_y)
        progress = ease_out_cubic(t)
        curr_x = self.start_x + (self.target_x - self.start_x) * progress
        curr_y = self.start_y + (self.target_y - self.start_y) * progress
        return (curr_x, curr_y)

    def draw(self, surface):
        pos = self.current_pos
        surface.blit(self.card_surface, pos)


class VictoryCascadeParticle:
    def __init__(self, card_surface, start_pos):
        self.card_surface = card_surface
        self.x, self.y = start_pos
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-12, -4)
        self.gravity = 0.6
        self.bounce = 0.75
        self.screen_h = 900

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity

        # Bounce on floor
        if self.y > self.screen_h - 154:
            self.y = self.screen_h - 154
            self.vy = -self.vy * self.bounce
            if abs(self.vy) < 1:
                self.vy = 0

    def draw(self, surface):
        surface.blit(self.card_surface, (self.x, self.y))


class AnimationManager:
    """Manages active card sliding animations and win celebration particles."""
    def __init__(self):
        self.animations = []
        self.victory_particles = []

    def add_card_animation(self, card_surface, start_pos, target_pos, duration=0.25, on_complete=None):
        anim = ActiveCardAnimation(card_surface, start_pos, target_pos, duration, on_complete)
        self.animations.append(anim)
        return anim

    def is_animating(self):
        return len(self.animations) > 0

    def update_and_draw(self, surface):
        # Update and render card translation animations
        active = []
        for anim in self.animations:
            anim.draw(surface)
            if not anim.finished:
                active.append(anim)
        self.animations = active

        # Update and render victory cascade particles
        for p in self.victory_particles:
            p.update()
            p.draw(surface)

    def start_victory_cascade(self, card_surfaces, positions):
        self.victory_particles = []
        for surf, pos in zip(card_surfaces, positions):
            self.victory_particles.append(VictoryCascadeParticle(surf, pos))
