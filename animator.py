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
    def __init__(self, card_surface, start_pos, delay=0.0, screen_w=1280, screen_h=900, card_w=110, card_h=154):
        self.card_surface = card_surface
        self.x = float(start_pos[0])
        self.y = float(start_pos[1])
        self.vx = random.uniform(-6.5, 6.5)
        self.vy = random.uniform(-11.0, -4.0)
        self.gravity = 0.55
        self.bounce = 0.65       # Energy restitution per vertical bounce
        self.friction = 0.70     # Ground friction dampening horizontal momentum on floor contact
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.card_w = card_w
        self.card_h = card_h
        self.bounces = 0
        self.max_bounces = random.randint(3, 4)  # Realistically settle after 3 to 4 jumps
        self.at_rest = False
        self.delay = delay
        self.start_time = time.time() + delay
        self.started = delay <= 0.0

    def update(self):
        if not self.started:
            if time.time() >= self.start_time:
                self.started = True
            else:
                return

        if self.at_rest:
            return

        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity

        floor_y = self.screen_h - self.card_h

        # Bounce on floor
        if self.y >= floor_y:
            self.y = floor_y
            self.bounces += 1
            self.vy = -self.vy * self.bounce
            self.vx *= self.friction

            # Stop moving realistically after a few jumps or when kinetic energy is depleted
            if self.bounces >= self.max_bounces or (abs(self.vy) < 1.8 and self.bounces >= 2):
                self.y = floor_y
                self.vy = 0.0
                self.vx = 0.0
                self.at_rest = True

    def draw(self, surface):
        if not self.started:
            return
        # If card has traveled far outside visible window view, skip drawing
        if self.x < -self.card_w - 50 or self.x > self.screen_w + 50:
            return
        surface.blit(self.card_surface, (round(self.x), round(self.y)))


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
        for i, (surf, pos) in enumerate(zip(card_surfaces, positions)):
            delay = i * 0.05
            self.victory_particles.append(VictoryCascadeParticle(surf, pos, delay=delay))
