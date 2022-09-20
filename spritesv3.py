import pygame as pg
from settingsv3 import *
import random
from random import uniform
from tilemapv3 import collide_hit_rect
import math
import time
vec = pg.math.Vector2


def wall_collides(sprite, group, dir):
    if dir == "x":
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            elif hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == "y":
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            elif hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
# Wall collisions for all required sprites


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0
        self.last_shot = 0
        self.max_health = PLAYER_HEALTH
        self.health = PLAYER_HEALTH
        self.max_ammo = 300
        self.ammo = 300
        self.clip_max = 15
        self.clip = 15
        self.reloading = False
        self.reload_time = 60
        self.fire_rate = FIRE_RATE
        self.spread = SPREAD
        self.shots = 0
        self.reloads = 0

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.vel.x = -PLAYERSPEED
        if keys[pg.K_d]:
            self.vel.x = PLAYERSPEED
        if keys[pg.K_w]:
            self.vel.y = -PLAYERSPEED
        if keys[pg.K_s]:
            self.vel.y = PLAYERSPEED
        if self.vel.y != 0 and self.vel.x != 0:
            self.vel *= 0.7071
        # shooting
        if keys[pg.K_SPACE]:
            if self.clip > 0:
                if self.reloading == False:
                    now = pg.time.get_ticks()
                    if now - self.last_shot > self.fire_rate:
                        self.last_shot = now
                        dir = vec(1, 0).rotate(-self.rot - 90)
                        Bullet(self.game, self.pos, dir, self.spread, "p")
                        self.shots += 1
                        self.clip = self.clip - 1
        # reloading trigger
        if keys[pg.K_r]:
            if self.reloading == False:
                # checks ammo and clip counts
                if self.ammo > 0:
                    if self.clip == self.clip_max:
                        pass
                    else:
                        self.reloading = True
                        self.reloads += 1
                        self.reload_start = pg.time.get_ticks()
                        self.reload_end = pg.time.get_ticks() + self.reload_time
                        self.reload_tick_start = 1
                else:
                    pass

    def rotate_player(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        angle_x, angle_y = (WIDTH/2) - mouse_x, (HEIGHT/2) - mouse_y
        player_radiens = math.atan2(angle_x, angle_y)
        self.rot = math.degrees(player_radiens)

    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        wall_collides(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        wall_collides(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect_center = self.hit_rect.center
        self.pos = vec(x, y) * TILESIZE
        self.vel = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.move_rot = 0
        self.health = MOB_HEALTH
        self.speed = random.choice(MOB_SPEEDS)
    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.vel += dist.normalize()

    def update(self):
        # rotate to player
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotozoom(self.game.mob_img, self.rot, 1)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        # movement
        self.vel = vec(self.speed, 0).rotate(-self.rot) * self.game.dt
        self.avoid_mobs()
        self.pos += self.vel
        self.rect.center = self.pos
        # collisions
        self.hit_rect.centerx = self.pos.x
        wall_collides(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        wall_collides(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center
        if self.health <= 0:
            self.kill()


class Sprinter(Mob):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.speed = PLAYERSPEED
        self.image = game.sprinter_img
        self.health = MOB_HEALTH * 0.75

    def update(self):
        # rotate to player
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotozoom(self.game.sprinter_img, self.rot, 1)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        # movement
        self.vel = vec(self.speed, 0).rotate(-self.rot) * self.game.dt
        self.avoid_mobs()
        self.pos += self.vel
        self.rect.center = self.pos
        # collisions
        self.hit_rect.centerx = self.pos.x
        wall_collides(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        wall_collides(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center
        if self.health <= 0:
            self.kill()


class Shooter(Mob):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.image = game.shooter_img
        self.shoot_timer = 0

    def update(self):
        # rotate to player
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotozoom(self.game.shooter_img, self.rot, 1)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        # movement
        self.vel = vec(self.speed, 0).rotate(-self.rot) * self.game.dt
        self.avoid_mobs()
        self.pos += self.vel
        self.rect.center = self.pos
        # collisions
        self.hit_rect.centerx = self.pos.x
        wall_collides(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        wall_collides(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center
        if self.health <= 0:
            self.kill()
        # shoot
        self.shoot_timer += 1
        if self.shoot_timer == 150:
            Bullet(self.game, self.pos, vec(75, 0).rotate(-self.rot) * self.game.dt, 0, "m")
            self.shoot_timer = 0


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, spread, shooter):
        self.game = game
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir.rotate(random.randint(-spread, spread)) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()
        self.shooter = shooter

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFE:
            self.kill()



class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
