from os import path
import os.path
from spritesv3 import *
from tilemapv3 import *
import random
import sqlite3
import hashlib, binascii, os

spawns = []


# creates database connection
def dbconnect():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "Database.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(e)


def hash_password(password):
    # Hash a password for storing
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    # Verify a stored password against one provided by user
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def regplayer(uname, password):
    con, curr = dbconnect()
    passhash = hash_password(password)
    try:
        print("anything out")
        curr.execute("INSERT INTO Users (Username, Password) values (?, ?)", (uname, passhash))
        con.commit()
        con.close()
    except:
        print("Exception")


def draw_player_health(surf, x, y, percent):
    # draws a health bar on the screen
    if percent < 0:
        percent = 0
    HEALTH_BAR_LENGTH = 100
    HEALTH_BAR_HEIGHT = 20
    fill = percent * HEALTH_BAR_LENGTH
    outline_rect = pg.Rect(x, y, HEALTH_BAR_LENGTH, HEALTH_BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, HEALTH_BAR_HEIGHT)
    # changes health colour based on percentage of health left
    if percent > 0.6:
        col = GREEN
    elif percent > 0.3:
        col = YELLOW
    else:
        col = RED
    # fills the health bar with the required colour
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


class Game:
    # creates the game class and sets all variables needed for the game
    def __init__(self):
        self.paused = False
        self.round_paused = False
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE), pg.FULLSCREEN
        self.clock = pg.time.Clock()
        pg.key.set_repeat(100, 100)
        self.load_data()
        self.last_spawn = 0
        self.round_num = 1
        self.round_max = ROUND_BASE_MOBS
        self.mob_multiplier = ROUND_MOB_MULTIPLIER
        self.round_spawned = 0
        self.round_kills = 0
        self.points = 999990
        self.total_points = 0
        self.juggernog_price = JUG_PRICE
        self.jug_lvl = 0
        self.mulekick_price = MULE_PRICE
        self.mule_lvl = 0
        self.double_tap_price = DOUBLE_TAP_PRICE
        self.double_tap_lvl = 0
        self.speed_cola_price = SPEED_COLA_PRICE
        self.speed_cola_lvl = 0
        self.deadshot_price = DEADSHOT_PRICE
        self.deadshot_lvl = 0
        self.fire_rate_up_price = FIRE_RATE_PRICE
        self.fire_rate_lvl = 0
        self.damage = DAMAGE
        self.go_screen = False
        self.shots_hit = 0
        self.kills = 0
        self.mob_health = MOB_HEALTH
        self.menus = True
        self.start_screen = True
        self.login = False
        self.register = False
        self.username_in = ""
        self.password_in = ""
        self.type_limit = 0
        self.selected_box = 0
        self.last_update = ""
        self.taken = False
        self.no_uname = False
        self.no_pass = False
        self.added_user = False
        self.score_screen = False

    def draw_text(self, text, font, size, colour, x, y, align="c"):
        # draws text on the screen using given parameters
        font = pg.font.Font(font, size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        # States where type will be set (eg. typed from the left/right)
        if align == "c":
            text_rect.center = (x, y)
        elif align == "l":
            text_rect.midleft = (x, y)
        elif align == "r":
            text_rect.midright = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        # Load the map and all other images needed
        game_folder = path.dirname(__file__)
        image_folder = path.join(game_folder, "Assests")
        self.map = Map(path.join(game_folder, 'map2.txt'))
        self.pause_font = path.join(image_folder, "Plane Crash.TTF")
        self.point_font = path.join(image_folder, "ColdCoffee.TTF")
        self.player_img = pg.image.load(path.join(image_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(image_folder, BULLET_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(image_folder, WALL_IMG)).convert_alpha()
        self.mob_img = pg.image.load(path.join(image_folder, MOB_IMG)).convert_alpha()
        self.sprinter_img = pg.image.load(path.join(image_folder, SPRINT_IMG)).convert_alpha()
        self.shooter_img = pg.image.load(path.join(image_folder, SHOOTER_IMG)).convert_alpha()
        self.quit_button = pg.image.load(path.join(image_folder, QUIT_BUTTON)).convert_alpha()
        self.back_button = pg.image.load(path.join(image_folder, BACK_BUTTON)).convert_alpha()
        self.juggernog = pg.image.load(path.join(image_folder, JUGGERNOG)).convert_alpha()
        self.double_tap = pg.image.load(path.join(image_folder, DOUBLETAP)).convert_alpha()
        self.mulekick = pg.image.load(path.join(image_folder, MULEKICK)).convert_alpha()
        self.deadshot = pg.image.load(path.join(image_folder, DEADSHOT)).convert_alpha()
        self.fire_rate_up = pg.image.load(path.join(image_folder, FIRE_RATE_UP)).convert_alpha()
        self.speed_cola = pg.image.load(path.join(image_folder, SPEED_COLA)).convert_alpha()
        self.continue_button = pg.image.load(path.join(image_folder, CONTINUE_BUTTON)).convert_alpha()
        self.play_button = pg.image.load(path.join(image_folder, PLAY_BUTTON)).convert_alpha()
        self.menu_quit_button = pg.image.load(path.join(image_folder, MENU_QUIT_BUTTON)).convert_alpha()
        self.log_in_button = pg.image.load(path.join(image_folder, LOGIN_BUTTON)).convert_alpha()
        self.register_button = pg.image.load(path.join(image_folder, REGISTER_BUTTON)).convert_alpha()
        self.scores_button = pg.image.load(path.join(image_folder, SCORE_BUTTON)).convert_alpha()

    def draw_shop(self):
        # displays the shop and all prices / names
        shop_bg = pg.Rect(100, 100, WIDTH / 1.2, HEIGHT / 1.2)
        shop_bg.center = (WIDTH / 2, HEIGHT / 2)
        pg.draw.rect(self.screen, LIGHTGREY, shop_bg)
        self.draw_text(str(self.points), self.point_font, 40, WHITE, WIDTH / 1.22, HEIGHT / 2)
        self.cont_but = self.screen.blit(self.continue_button, (WIDTH / 1.35, HEIGHT / 1.3))
        # max health
        self.juggernog_drawn = self.screen.blit(self.juggernog, (WIDTH / 2 - 489, HEIGHT / 2 - 310))
        self.draw_text(str(self.juggernog_price), self.point_font, 32, WHITE, WIDTH / 2 - 400, HEIGHT / 2 - 60)
        # damage boost
        self.double_tap_drawn = self.screen.blit(self.double_tap, (WIDTH / 2 - 189, HEIGHT / 2 - 310))
        self.draw_text(str(self.double_tap_price), self.point_font, 32, WHITE, WIDTH / 2 - 100, HEIGHT / 2 - 60)
        # max ammo
        self.mulekick_drawn = self.screen.blit(self.mulekick, (WIDTH / 2 + 111, HEIGHT / 2 - 310))
        self.draw_text(str(self.mulekick_price), self.point_font, 32, WHITE, WIDTH / 2 + 200, HEIGHT / 2 - 60)
        # clip size
        self.speed_cola_drawn = self.screen.blit(self.speed_cola, (WIDTH / 2 - 489, HEIGHT / 2))
        self.draw_text(str(self.speed_cola_price), self.point_font, 32, WHITE, WIDTH / 2 - 400, HEIGHT / 1.2 - 10)
        # accuracy up
        self.deadshot_drawn = self.screen.blit(self.deadshot, (WIDTH / 2 - 189, HEIGHT / 2))
        self.draw_text(str(self.deadshot_price), self.point_font, 32, WHITE, WIDTH / 2 - 100, HEIGHT / 1.2 - 10)
        # fire rate up
        self.fire_rate_up_drawn = self.screen.blit(self.fire_rate_up, (WIDTH / 2 + 111, HEIGHT / 2))
        self.draw_text(str(self.fire_rate_up_price), self.point_font, 32, WHITE, WIDTH / 2 + 200, HEIGHT / 1.2 - 10)

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        # sets the map based on the map file
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                # sets items on the map based on the character
                if tile == "1":
                    Wall(self, col, row)
                if tile == "P":
                    self.player = Player(self, col, row)
                if tile == "M":
                    spawn = [col, row]
                    spawns.append(spawn)
        self.paused = False

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            start_x, start_y = self.player.pos
            if self.paused == False:
                if self.round_paused == False:
                    if not self.go_screen:
                        if not self.menus:
                            self.update()
                else:
                    pass
            else:
                pass
            self.draw()
            self.type_limit += 1

    def quit(self):
        pg.quit()
        exit()

    def draw_reloading(self):
        reloading_percent = (self.player.reload_tick_start / self.player.reload_time) * 100
        RELOAD_BAR_LENGTH = 100
        RELOAD_BAR_HEIGHT = 20
        reloading_fill = reloading_percent
        outline_rect = pg.Rect(WIDTH / 2 - 50, HEIGHT * 0.8, RELOAD_BAR_LENGTH, RELOAD_BAR_HEIGHT)
        fill_rect = pg.Rect(WIDTH / 2 - 50, HEIGHT * 0.8, reloading_fill, RELOAD_BAR_HEIGHT)
        pg.draw.rect(self.screen, WHITE, fill_rect)
        pg.draw.rect(self.screen, WHITE, outline_rect, 2)

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.Camera.update(self.player)
        self.player.rotate_player()
        # bullet collisions
        # bullets hit mobs
        for bullet in self.bullets:
            if bullet.shooter == "p":
                hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
                for hit in hits:
                    self.shots_hit += 1
                    hit.health -= random.randint(int(self.damage * 0.6), int(self.damage * 1.2))
                    self.points += 10
                    self.total_points += 10
                    if hit.health <= 0:
                        self.points += 50
                        self.total_points += 50
                        self.round_kills += 1
                        self.kills += 1
            else:
                # checks if enemy bullets hit player
                hits = pg.sprite.spritecollide(self.player, self.bullets, False, collide_hit_rect)
                for hit in hits:
                    if bullet.shooter == "m":
                        self.player.health -= 10
                        hit.kill()
                        if self.player.health <= 0:
                            # Displays the game over screen on death
                            self.go_screen = True
        # mob hits player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                # Displays the game over screen on death
                self.go_screen = True
            if hits:
                self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # mob spawning
        if self.round_spawned < self.round_max:
            if len(self.mobs) == 30:
                pass
            else:
                spawning = pg.time.get_ticks()
                if spawning - self.last_spawn > SPAWN_INTERVAL:
                    self.last_spawn = spawning
                    this_spawn = random.choice(spawns)
                    zombie_type = random.randint(1, 20)
                    if zombie_type == 20:
                        Shooter(self, this_spawn[0], this_spawn[1])
                    elif zombie_type == 19:
                        Sprinter(self, this_spawn[0], this_spawn[1])
                    else:
                        Mob(self, this_spawn[0], this_spawn[1])
                    self.round_spawned += 1
                else:
                    pass
        else:
            pass
        # Round switching
        if self.round_kills == self.round_max:
            self.round_num += 1
            self.round_max = int(self.round_max * ROUND_MOB_MULTIPLIER)
            self.round_spawned = 0
            self.round_kills = 0
            self.round_paused = True
        # reloading action
        if self.player.reloading:
            self.player.reload_start += 1
            self.player.reload_tick_start += 1
            if self.player.reload_start > self.player.reload_end:
                self.player.reloading = False
                clip_used = self.player.clip_max - self.player.clip
                self.player.clip = self.player.clip_max
                self.player.ammo = self.player.ammo - clip_used
                if self.player.ammo < 0:
                    self.player.clip += self.player.ammo
                    self.player.ammo = 0

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        # self.draw_grid()
        if not self.menus:
            if not self.go_screen:
                for sprite in self.all_sprites:
                    self.screen.blit(sprite.image, self.Camera.apply(sprite))
                self.draw_text(str(self.round_num), self.pause_font, 50, WHITE, 150, HEIGHT - 150)
                if self.round_paused == True:
                    self.draw_shop()
                else:
                    draw_player_health(self.screen, 100, 100, self.player.health / self.player.max_health)
                    self.draw_text(str(self.points), self.point_font, 40, WHITE, 150, 150)
                    self.draw_text(str(self.player.clip), self.point_font, 40, WHITE, WIDTH * 0.8 - 10,
                                   HEIGHT * 0.8 - 10, "r")
                    self.draw_text("/", self.point_font, 60, WHITE, WIDTH * 0.8, HEIGHT * 0.8)
                    self.draw_text(str(self.player.ammo), self.point_font, 40, WHITE, WIDTH * 0.8 + 10,
                                   HEIGHT * 0.8 + 10, "l")
                if self.paused == True:
                    paused_rec = pg.Surface(self.screen.get_size()).convert_alpha()
                    paused_rec.fill((0, 0, 0, 130))
                    self.screen.blit(paused_rec, (0, 0))
                    self.draw_text("paused", self.pause_font, 100, WHITE, (WIDTH / 2), ((HEIGHT / 2) * 0.7))
                    self.draw_text("press esc to continue", self.pause_font, 20, WHITE, (WIDTH / 2),
                                   ((HEIGHT / 2) * 0.9))
                    self.b_but = self.screen.blit(self.back_button, (WIDTH / 2 + 50, HEIGHT / 2))
                    self.q_but = self.screen.blit(self.quit_button, (WIDTH / 2 - 170, HEIGHT / 2))
                else:
                    pass
                if self.player.reloading:
                    self.draw_reloading()
            else:
                if self.go_screen:
                    # Displays the game over screen with stats from the played game
                    pg.draw.rect(self.screen, DARKGREY, (0, 0, WIDTH, HEIGHT))
                    self.draw_text("you survived until round:", self.pause_font, 40, WHITE, WIDTH / 2, HEIGHT * 0.1)
                    self.draw_text(str(self.round_num), self.pause_font, 80, WHITE, WIDTH / 2, HEIGHT * 0.1 + 80)

                    if self.player.shots > 0 and self.shots_hit > 0:
                        accuracy = int(self.shots_hit / self.player.shots * 100)
                    else:
                        accuracy = 0
                    # collum 1
                    self.draw_text("final score:", self.pause_font, 40, WHITE, WIDTH * 0.1, HEIGHT * 0.4, "l")
                    self.draw_text(str(self.total_points), self.pause_font, 40, WHITE, WIDTH * 0.33, HEIGHT * 0.4, "l")
                    self.draw_text("shots fired:", self.pause_font, 40, WHITE, WIDTH * 0.1, HEIGHT * 0.5, "l")
                    self.draw_text(str(self.player.shots), self.pause_font, 40, WHITE, WIDTH * 0.33, HEIGHT * 0.5, "l")
                    self.draw_text("shots hit:", self.pause_font, 40, WHITE, WIDTH * 0.1, HEIGHT * 0.6, "l")
                    self.draw_text(str(self.shots_hit), self.pause_font, 40, WHITE, WIDTH * 0.33, HEIGHT * 0.6, "l")
                    self.draw_text("accuracy:", self.pause_font, 40, WHITE, WIDTH * 0.1, HEIGHT * 0.7, "l")
                    self.draw_text("%", self.pause_font, 40, WHITE, WIDTH * 0.33 + 75, HEIGHT * 0.7, "l")
                    self.draw_text(str(accuracy), self.pause_font, 40, WHITE, WIDTH * 0.33, HEIGHT * 0.7, "l")
                    self.draw_text("reloads:", self.pause_font, 40, WHITE, WIDTH * 0.1, HEIGHT * 0.8, "l")
                    self.draw_text(str(self.player.reloads), self.pause_font, 40, WHITE, WIDTH * 0.33, HEIGHT * 0.8,
                                   "l")
                    self.draw_text("zombie kills:", self.pause_font, 40, WHITE, WIDTH * 0.1, HEIGHT * 0.9, "l")
                    self.draw_text(str(self.kills), self.pause_font, 40, WHITE, WIDTH * 0.33, HEIGHT * 0.9, "l")
                    # collum 2
                    self.draw_text("health level:", self.pause_font, 40, WHITE, WIDTH * 0.59, HEIGHT * 0.4, "l")
                    self.draw_text(str(self.jug_lvl), self.pause_font, 40, WHITE, WIDTH * 0.9, HEIGHT * 0.4, "r")
                    self.draw_text("damage level:", self.pause_font, 40, WHITE, WIDTH * 0.59, HEIGHT * 0.5, "l")
                    self.draw_text(str(self.double_tap_lvl), self.pause_font, 40, WHITE, WIDTH * 0.9, HEIGHT * 0.5, "r")
                    self.draw_text("ammo level:", self.pause_font, 40, WHITE, WIDTH * 0.59, HEIGHT * 0.6, "l")
                    self.draw_text(str(self.mule_lvl), self.pause_font, 40, WHITE, WIDTH * 0.9, HEIGHT * 0.6, "r")
                    self.draw_text("clip level:", self.pause_font, 40, WHITE, WIDTH * 0.59, HEIGHT * 0.7, "l")
                    self.draw_text(str(self.speed_cola_lvl), self.pause_font, 40, WHITE, WIDTH * 0.9, HEIGHT * 0.7, "r")
                    self.draw_text("accuracy level:", self.pause_font, 40, WHITE, WIDTH * 0.59, HEIGHT * 0.8, "l")
                    self.draw_text(str(self.deadshot_lvl), self.pause_font, 40, WHITE, WIDTH * 0.9, HEIGHT * 0.8, "r")
                    self.draw_text("fire rate level:", self.pause_font, 40, WHITE, WIDTH * 0.59, HEIGHT * 0.9, "l")
                    self.draw_text(str(self.fire_rate_lvl), self.pause_font, 40, WHITE, WIDTH * 0.9, HEIGHT * 0.9, "r")

                    self.cont_but_go = self.screen.blit(self.continue_button, (WIDTH / 2 - 120, HEIGHT * 0.9))

        else:
            if self.start_screen:
                self.draw_text("hotline zombani", self.pause_font, 70, WHITE, WIDTH / 2, HEIGHT * 0.1)
                self.log_in_but_drawn = self.screen.blit(self.log_in_button, (WIDTH / 2 - 120, HEIGHT / 2))
                self.register_but_drawn = self.screen.blit(self.register_button, (WIDTH / 2 - 120, HEIGHT / 1.6))
            elif self.score_screen:
                self.scores_back_drawn = self.screen.blit(self.back_button, (WIDTH / 2 - 50, HEIGHT * 0.9))
            else:
                if self.login or self.register:
                    # Draws the required elements for the login and registaration screens
                    pg.draw.rect(self.screen, DARKGREY, (0, 0, WIDTH, HEIGHT))
                    self.draw_text("hotline zombani", self.pause_font, 70, WHITE, WIDTH / 2, HEIGHT * 0.1)
                    username_rect = pg.Rect(WIDTH / 2 - 300, HEIGHT * 0.47, 600, 50)
                    self.username_box = pg.draw.rect(self.screen, WHITE, username_rect, 2)
                    password_rect = pg.Rect(WIDTH / 2 - 300, HEIGHT * 0.67, 600, 50)
                    self.password_box = pg.draw.rect(self.screen, WHITE, password_rect, 2)
                    self.draw_text("username", self.pause_font, 40, WHITE, WIDTH / 2, HEIGHT * 0.4)
                    self.draw_text(self.username_in, self.point_font, 30, WHITE, WIDTH / 2, HEIGHT * 0.5)
                    self.draw_text("password", self.pause_font, 40, WHITE, WIDTH / 2, HEIGHT * 0.6)
                    self.draw_text(self.password_in, self.point_font, 30, WHITE, WIDTH / 2, HEIGHT * 0.7)
                    self.b_but = self.screen.blit(self.back_button, (WIDTH / 2 - 60, HEIGHT * 0.8))
                    # visual differences in login and registration screens
                    if self.login:
                        self.draw_text("returning player", self.pause_font, 40, WHITE, WIDTH / 2, HEIGHT * 0.2)
                        self.log_in_but_drawn = self.screen.blit(self.log_in_button, (WIDTH / 2 - 120, HEIGHT * 0.9))
                    else:
                        self.draw_text("new player", self.pause_font, 40, WHITE, WIDTH / 2, HEIGHT * 0.2)
                        self.register_but_drawn = self.screen.blit(self.register_button,
                                                                   (WIDTH / 2 - 120, HEIGHT * 0.9))
                    # handles all missing fields and other possible errors when creating an account
                    if self.taken:
                        pg.draw.rect(self.screen, LIGHTGREY, (WIDTH / 2 - WIDTH / 4, HEIGHT / 2 - HEIGHT / 4
                                                              , WIDTH / 2, HEIGHT / 2))
                        self.draw_text("this name is already taken", self.pause_font, 40, WHITE, WIDTH / 2,
                                       HEIGHT * 0.4)
                        self.alert_back = self.screen.blit(self.back_button, (WIDTH / 2 - 60, HEIGHT * 0.6))
                    if self.no_uname:
                        pg.draw.rect(self.screen, LIGHTGREY, (WIDTH / 2 - WIDTH / 4, HEIGHT / 2 - HEIGHT / 4
                                                              , WIDTH / 2, HEIGHT / 2))
                        self.draw_text("please provide a name", self.pause_font, 40, WHITE, WIDTH / 2,
                                       HEIGHT * 0.4)
                        self.alert_back = self.screen.blit(self.back_button, (WIDTH / 2 - 60, HEIGHT * 0.6))
                    if self.no_pass:
                        pg.draw.rect(self.screen, LIGHTGREY, (WIDTH / 2 - WIDTH / 4, HEIGHT / 2 - HEIGHT / 4
                                                              , WIDTH / 2, HEIGHT / 2))
                        self.draw_text("please provide a password", self.pause_font, 40, WHITE, WIDTH / 2,
                                       HEIGHT * 0.4)
                        self.alert_back = self.screen.blit(self.back_button, (WIDTH / 2 - 60, HEIGHT * 0.6))
                    if self.added_user:
                        # message to state that the user has successfully registered
                        pg.draw.rect(self.screen, LIGHTGREY, (WIDTH / 2 - WIDTH / 4, HEIGHT / 2 - HEIGHT / 4
                                                              , WIDTH / 2, HEIGHT / 2))
                        self.draw_text("user registered", self.pause_font, 40, WHITE, WIDTH / 2, HEIGHT * 0.4)
                        self.draw_text("successfully", self.pause_font, 40, WHITE, WIDTH / 2, HEIGHT * 0.4 + 50)
                        self.alert_back = self.screen.blit(self.back_button, (WIDTH / 2 - 60, HEIGHT * 0.6))
                else:
                    # Draws the required elements for the main menu screen
                    pg.draw.rect(self.screen, DARKGREY, (0, 0, WIDTH, HEIGHT))
                    self.draw_text("hotline zombani", self.pause_font, 70, WHITE, WIDTH / 2, HEIGHT * 0.1)
                    self.play_but_drawn = self.screen.blit(self.play_button, (WIDTH / 2 - 120, HEIGHT / 2))
                    self.quit_button_drawn = self.screen.blit(self.menu_quit_button,
                                                              (WIDTH / 2 - 120, HEIGHT / 2 + 200))
                    self.score_but_drawn = self.screen.blit(self.scores_button, (WIDTH / 2 - 120, HEIGHT / 2 + 100))

        pg.display.flip()

    def events(self):
        # catch all events
        for event in pg.event.get():
            if self.menus:
                if self.start_screen:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        click_x, click_y = pg.mouse.get_pos()
                        if self.log_in_but_drawn.collidepoint(click_x, click_y):
                            self.start_screen = False
                            self.login = True
                        elif self.register_but_drawn.collidepoint(click_x, click_y):
                            self.start_screen = False
                            self.register = True
                else:
                    if self.login or self.register:
                        if self.taken or self.no_uname or self.no_pass or self.added_user:
                            if event.type == pg.MOUSEBUTTONDOWN:
                                click_x, click_y = pg.mouse.get_pos()
                                if self.alert_back.collidepoint(click_x, click_y):
                                    self.taken = False
                                    self.no_pass = False
                                    self.no_uname = False
                                    self.added_user = False
                                    self.username_in = ""
                                    self.password_in = ""
                        else:
                            if event.type == pg.MOUSEBUTTONDOWN:
                                click_x, click_y = pg.mouse.get_pos()
                                if self.username_box.collidepoint(click_x, click_y):
                                    self.selected_box = 0
                                elif self.password_box.collidepoint(click_x, click_y):
                                    self.selected_box = 1
                                elif self.b_but.collidepoint(click_x, click_y):
                                    self.register = False
                                    self.login = False
                                    self.start_screen = True
                                    self.password_in = ""
                                    self.username_in = ""
                                if self.register:
                                    if self.register_but_drawn.collidepoint(click_x, click_y):
                                        if self.username_in == "":
                                            self.no_uname = True
                                        else:
                                            if self.password_in == "":
                                                self.no_pass = True
                                            else:
                                                con, curr = dbconnect()
                                                passhash = hash_password(self.password_in)
                                                try:
                                                    curr.execute("INSERT INTO Users (Username, Password) values (?, ?)",
                                                                 (self.username_in, passhash))
                                                    con.commit()
                                                    con.close()
                                                    self.added_user = True
                                                except:
                                                    self.taken = True
                                elif self.login:
                                    # log in system that takes input for username and password
                                    if self.log_in_but_drawn.collidepoint(click_x, click_y):
                                        # checks to ensure name/pass boxes are filled
                                        if self.username_in == "":
                                            self.no_uname = True
                                        else:
                                            if self.password_in == "":
                                                self.no_pass = True
                                            else:
                                                self.password_check = hash_password(self.password_in)
                                                con, curr = dbconnect()
                                                # checks input against each username in database
                                                curr.execute("SELECT Username FROM Users")
                                                for row in curr.fetchall():
                                                    row = row[0]
                                                    print(row)
                                                    print(self.username_in)
                                                    if row == self.username_in:
                                                        print("MATCH")
                                                        # checks password against stored password of user input
                                                        curr.execute("SELECT Password FROM Users WHERE Username =?;",
                                                                     [self.username_in])
                                                        for row in curr.fetchall():
                                                            passcheck = verify_password(row[0], self.password_in)
                                                            if passcheck:
                                                                self.login = False
                                                con.close()

                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_BACKSPACE:
                                    if self.selected_box == 0:
                                        self.username_in = self.username_in[:-1]
                                    else:
                                        self.password_in = self.password_in[:-1]

                                if event == self.last_update:
                                    pass
                                else:
                                    self.last_update = event
                                    if self.selected_box == 0:
                                        if len(self.username_in) == 16:
                                            pass
                                        else:
                                            self.username_in += event.unicode
                                    else:
                                        self.password_in += event.unicode
                            if event.type == pg.KEYUP:
                                self.last_update = ""
                    else:
                        if event.type == pg.MOUSEBUTTONDOWN:
                            click_x, click_y = pg.mouse.get_pos()
                            if self.quit_button_drawn.collidepoint(click_x, click_y):
                                quit()
                            elif self.play_but_drawn.collidepoint(click_x, click_y):
                                self.menus = False
                            elif self.score_but_drawn.collidepoint(click_x, click_y):
                                self.score_screen = True
            else:
                if self.go_screen:
                    # checks for continue pressed on go screen
                    if event.type == pg.MOUSEBUTTONDOWN:
                        click_x, click_y = pg.mouse.get_pos()
                        if self.cont_but_go.collidepoint(click_x, click_y):
                            self.go_screen = False
                            self.playing = False
                            # adds game data to the database after death
                            try:
                                con, curr = dbconnect()
                                curr.execute(
                                    "INSERT INTO Play (Username, Shots, Hits, Reloads, Kills, Healthlvl, Damagelvl, "
                                    "Ammolvl, Cliplvl, Accuracylvl, Fireratelvl, Round) VALUES (?, ?, ?, ?, ?, ?, ?, "
                                    "?, ?, ?, ?, ?)",
                                    (self.username_in, self.player.shots, self.shots_hit, self.player.reloads,
                                     self.kills, self.jug_lvl, self.double_tap_lvl, self.mule_lvl, self.speed_cola_lvl,
                                     self.deadshot_lvl, self.fire_rate_lvl, self.round_num))
                                con.commit()
                                con.close()
                            except Exception as e:
                                print(e)
                # checks for buttons pressed on pause screen
                if self.paused:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        click_x, click_y = pg.mouse.get_pos()
                        if self.q_but.collidepoint(click_x, click_y):
                            quit()
                        if self.b_but.collidepoint(click_x, click_y):
                            self.go_screen = True
                # buying items in shop
                if self.round_paused:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        click_x, click_y = pg.mouse.get_pos()
                        # buying +max health
                        if self.juggernog_drawn.collidepoint(click_x, click_y):
                            if self.juggernog_price != "Max":
                                if self.points >= self.juggernog_price:
                                    self.points -= self.juggernog_price
                                    self.juggernog_price += JUG_PRICE
                                    self.jug_lvl += 1
                                    self.player.max_health += int(self.player.max_health / 1.8)
                                    if self.jug_lvl == 5:
                                        self.juggernog_price = "Max"

                        # buying damage buff
                        if self.double_tap_drawn.collidepoint(click_x, click_y):
                            if self.double_tap_price != "Max":
                                if self.points >= self.double_tap_price:
                                    self.points -= self.double_tap_price
                                    self.double_tap_price += DOUBLE_TAP_PRICE
                                    self.double_tap_lvl += 1
                                    self.damage += 3
                                    if self.double_tap_lvl == 12:
                                        self.double_tap_price = "Max"
                        # buying +max ammo
                        if self.mulekick_drawn.collidepoint(click_x, click_y):
                            if self.mulekick_price != "Max":
                                if self.points >= self.mulekick_price:
                                    self.points -= self.mulekick_price
                                    self.mulekick_price += MULE_PRICE
                                    self.mule_lvl += 1
                                    self.player.max_ammo += int(self.player.max_ammo / 1.9)
                                    if self.mule_lvl == 10:
                                        self.mulekick_price = "Max"
                        # buying +max clip size
                        if self.speed_cola_drawn.collidepoint(click_x, click_y):
                            if self.speed_cola_price != "Max":
                                if self.points >= self.speed_cola_price:
                                    self.points -= self.speed_cola_price
                                    self.speed_cola_price += SPEED_COLA_PRICE
                                    self.speed_cola_lvl += 1
                                    self.player.clip_max += 15
                                    if self.speed_cola_lvl == 12:
                                        self.speed_cola_price = "Max"
                        # buying +accuracy
                        if self.deadshot_drawn.collidepoint(click_x, click_y):
                            if self.deadshot_price == "Max":
                                pass
                            else:
                                if self.points >= self.deadshot_price:
                                    self.points -= self.deadshot_price
                                    self.deadshot_price += DEADSHOT_PRICE
                                    self.deadshot_lvl += 1
                                    self.player.spread -= 2
                                    if self.player.spread == 0:
                                        self.deadshot_price = "Max"
                        # buying +fire rare
                        if self.fire_rate_up_drawn.collidepoint(click_x, click_y):
                            if self.fire_rate_up_price != "Max":
                                if self.points >= self.fire_rate_up_price:
                                    self.points -= self.fire_rate_up_price
                                    self.fire_rate_up_price += FIRE_RATE_PRICE
                                    self.fire_rate_lvl += 1
                                    self.player.fire_rate -= 30
                                    if self.fire_rate_lvl == 10:
                                        self.fire_rate_up_price = "Max"
                        # close shop + resume next round
                        if self.cont_but.collidepoint(click_x, click_y):
                            self.round_paused = False
                            self.player.health = self.player.max_health
                            self.player.ammo = self.player.max_ammo
                            self.player.clip = self.player.clip_max
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if not self.paused:
                            self.paused = True
                        else:
                            self.paused = False

    def show_start_screen(self):
        pass

    def game_prep(self):
        # Reseats all variables after the game is concluded
        self.points = 0
        self.total_points = 0
        self.round_kills = 0
        self.round_spawned = 0
        self.round_num = 1
        self.juggernog_price = JUG_PRICE
        self.jug_lvl = 0
        self.mulekick_price = MULE_PRICE
        self.mule_lvl = 0
        self.double_tap_price = DOUBLE_TAP_PRICE
        self.double_tap_lvl = 0
        self.speed_cola_price = SPEED_COLA_PRICE
        self.speed_cola_lvl = 0
        self.deadshot_price = DEADSHOT_PRICE
        self.deadshot_lvl = 0
        self.fire_rate_up_price = FIRE_RATE_PRICE
        self.fire_rate_lvl = 0
        self.damage = DAMAGE
        self.player.shots = 0
        self.shots_hit = 0
        self.player.reloads = 0
        self.kills = 0
        self.menus = True
        self.go_screen = False
        self.round_paused = False


# create the game object
g = Game()
g.show_start_screen()
g.new()
g.Camera = Camera(g.map.width, g.map.height)
g.run()
g.game_prep()
while True:
    conn, cur = dbconnect()
    g.game_prep()
    g.show_start_screen()
    g.new()
    g.run()
