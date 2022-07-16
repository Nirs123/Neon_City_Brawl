import pygame
import os
import random
import csv
import button
import time
import configparser

pygame.mixer.init()
pygame.init()

config = configparser.ConfigParser()
config.read("user_setting.ini")

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Neon City Brawl')

#initialisation framerate
clock = pygame.time.Clock()
FPS = 60

#varibales du jeu
GRAVITY = 0.5
ROWS = 13
COLS = 130
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 46 
level = 1
SCROLL_THRESH = 250
screen_scroll = 0
bg_scroll = 0
start_game = False
pause = False
setting = False
sound = False
control = False
MAX_LEVELS = 2
change_key = False
key_to_change = None
pop_msg_key = False
choose_difficulty = False
play_trans = False
s_music = True
s_audio_death = True
s_effects_load = True
play_trans_end = False
end_game = False

#difficultés
d_easy = {"heal_box":55,"ammo_box":20,"grenade_box":4,"player_dmg":35,"enemy_dmg":15,"grenade_dmg":40}
d_medium = {"heal_box":50,"ammo_box":15,"grenade_box":3,"player_dmg":25,"enemy_dmg":17,"grenade_dmg":50}
d_hard = {"heal_box":45,"ammo_box":12,"grenade_box":2,"player_dmg":20,"enemy_dmg":20,"grenade_dmg":60}
d_difficulty = None

#audio
audio_death = pygame.mixer.Sound("audio/effects/death.wav")
audio_grenade = pygame.mixer.Sound("audio/effects/grenade.wav")
audio_jump = pygame.mixer.Sound("audio/effects/jump.wav")
audio_shoot = pygame.mixer.Sound("audio/effects/shoot.wav")
audio_loading1 = pygame.mixer.Sound("audio/effects/loading_1.wav")
audio_loading2 = pygame.mixer.Sound("audio/effects/loading_2.wav")
audio_loading3 = pygame.mixer.Sound("audio/effects/loading_3.wav")
audio_end = pygame.mixer.Sound("audio/effects/end.wav")
l_effects = [audio_loading3,audio_loading2,audio_loading1,audio_jump,audio_shoot,audio_grenade,audio_end]
l_audio_loading = [audio_loading3,audio_loading2,audio_loading1]

#Debug
DEBUG_HITBOX = False
DEBUG_VISION = False
DEBUG_INVICIBLE = False

#initialisation action du player
moving_left = False
moving_right = False
shoot = False
grenade = False

#chargement des images
#background
city1_img = pygame.image.load('img/Background/city1.png').convert_alpha()
city2_img = pygame.image.load('img/Background/city2.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
#tiles
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f"img/tile/{x}.png")
	img = pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
	img_list.append(img)
pink_bullet_img = pygame.image.load("img/icons/pink_bullet.png").convert_alpha()
blue_bullet_img = pygame.image.load("img/icons/blue_bullet.png").convert_alpha()
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
ammo_box_img = pygame.image.load("img/tile/41.png").convert_alpha()
grenade_box_img = pygame.image.load("img/tile/42.png").convert_alpha()
health_box_img = pygame.image.load("img/tile/43.png").convert_alpha()
item_boxes = {'Ammo':ammo_box_img, 'Grenade': grenade_box_img, 'Health': health_box_img}
#settings and menu
play_img = pygame.image.load("img/menu/play.png").convert_alpha()
quit_img = pygame.image.load("img/menu/quit.png").convert_alpha()
resume_img = pygame.image.load("img/menu/resume.png").convert_alpha()
setting_img = pygame.image.load("img/menu/setting.png").convert_alpha()
restart_img = pygame.image.load("img/menu/restart.png").convert_alpha()
controls_img = pygame.image.load("img/menu/controls.png").convert_alpha()
sound_img = pygame.image.load("img/menu/sound.png").convert_alpha()
return_img = pygame.image.load("img/menu/return.png").convert_alpha()
effects_img = pygame.image.load("img/menu/effects.png").convert_alpha()
music_img = pygame.image.load("img/menu/music.png").convert_alpha()
moins_img = pygame.image.load("img/menu/moins.png").convert_alpha()
plus_img = pygame.image.load("img/menu/plus.png").convert_alpha()
grenade_img_menu = pygame.image.load("img/menu/grenade.png").convert_alpha()
hand_img_menu = pygame.image.load("img/menu/hand.png").convert_alpha()
jump_img_menu = pygame.image.load("img/menu/jump.png").convert_alpha()
left_img_menu = pygame.image.load("img/menu/left.png").convert_alpha()
rifle_img_menu = pygame.image.load("img/menu/rifle.png").convert_alpha()
right_img_menu = pygame.image.load("img/menu/right.png").convert_alpha()
key_input_img = pygame.image.load("img/menu/key_input.png").convert_alpha()
difficulty_img = pygame.image.load("img/menu/difficulty.png").convert_alpha()
easy_img = pygame.image.load("img/menu/easy.png").convert_alpha()
medium_img = pygame.image.load("img/menu/medium.png").convert_alpha()
hard_img = pygame.image.load("img/menu/hard.png").convert_alpha()
save_setting_img = pygame.image.load("img/menu/save_setting.png").convert_alpha()
default_setting_img = pygame.image.load("img/menu/default_setting.png").convert_alpha()

#couleurs
BG = (41, 41, 41)
MENU_BG = (48, 41, 49)
RED = (255, 0, 0)
GREEN = (53, 186, 28)
WHITE = (255, 255, 255)

def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(4):
		screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
		screen.blit(city1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - city1_img.get_height()-50))
		screen.blit(city2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - city2_img.get_height()-50))

font = pygame.font.SysFont('Futura',30)
font2 = pygame.font.SysFont('Futura',45)
font3 = pygame.font.SysFont('Futura',80)
def draw_text(text, font, text_col, x , y):
	img = font.render(text, True, text_col,None)
	screen.blit(img, (x,y))

def draw_image(image,x,y,scale):
	width = image.get_width()
	height = image.get_height()
	n_image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
	n_rect = n_image.get_rect()
	n_rect.topleft = (x, y)
	screen.blit(n_image, (x,y))

def restart_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	exit_group.empty()

	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)
	return data

default_d_keys = {"music":1.0,"effects":1.0,"left":113,"right":100,"jump":32,"rifle":49,"grenade":50,"hand":51}
d_keys = {}
def load_settings():
	for key in default_d_keys.keys():
		if key != "music" and key != "effects":
			d_keys[key] = int(config.get("SETTINGS",key))
		else:
			d_keys[key] = float(config.get("SETTINGS",key))

def save_settings():
	for k,v in d_keys.items():
		config.set("SETTINGS",str(k),str(v))
	with open("user_setting.ini","w") as config_file:
		config.write(config_file)

def reset_settings():
	for k,v in default_d_keys.items():
		d_keys[k] = v
		config.set("SETTINGS",str(k),str(v))
	pygame.mixer.music.pause()
	pygame.mixer.music.set_volume(d_keys["music"])
	pygame.mixer.music.unpause()
	with open("user_setting.ini","w") as config_file:
		config.write(config_file)

def f_start_game():
	start_game = True
	choose_difficulty = False
	play_trans = True
	return start_game,choose_difficulty,play_trans

class Character(pygame.sprite.Sprite):
	def __init__(self, x, y, scale, speed, type, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.health = 100
		self.alive = True
		self.ammo = ammo
		self.start_ammo = 30
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.speed = speed
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.hud_ext_index = 0
		self.type = type
		#AI
		self.move_counter = 0
		self.vision = pygame.Rect(0,0,175,5)
		self.idling = False
		self.idling_counter = 0

		self.update_time = pygame.time.get_ticks()

		self.weapon = 0
		self.temp_weapon = 0

		animation_types = ['Idle', 'Run', 'Jump','Idle_Grenade','Jump_Grenade','Run_Grenade','Idle_Rifle','Jump_Rifle','Run_Rifle','Death']
		for animation in animation_types:
			#liste temporaire pour stockage de toutes les img d'une animation
			temp_list = []
			#longueur du fichier
			longueur_fichier = len(os.listdir(f'img/{self.type}/{animation}'))
			#ouverture du fichier
			for i in range(longueur_fichier):
				img = pygame.image.load(f'img/{self.type}/{animation}/{i}.png')
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()

		self.hud_ext_list = []
		longueur_fichier_2 = len(os.listdir(f'img/hud'))
		for j in range(longueur_fichier_2):
			img2 = pygame.image.load(f'img/hud/{j}.png')
			self.hud_ext_list.append(img2)
		self.img_hud_ext = self.hud_ext_list[self.hud_ext_index]
		self.rect2 = self.img_hud_ext.get_rect()
		self.rect2.center = (70, 30)

	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(9)

	def move(self, moving_left, moving_right):
		#variables pour le mouvement
		screen_scroll = 0
		dx = 0
		dy = 0

		#execution de moving left ou right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		#on applique la gravité
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#check fin de niveau
		level_complete = False
		if pygame.sprite.spritecollide(self,exit_group,False):
			if self.type == "player1":
				level_complete = True

		#Check si tombé dans le vide
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0

		#check des collisions
		for tile in world.obstacle_list:
			#obstacle gauche ou droit
			if tile[0][1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				if tile[1] == 39:
					pass
				else:
					dx = 0
			#obstacle haut ou bas
			if tile[0][1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				if tile[1] == 39:
					pass
				else:
					if self.vel_y < 0:
						self.vel_y = 0
						dy = tile[0][1].bottom - self.rect.top
					elif self.vel_y >= 0:
						self.vel_y = 0
						self.in_air = False
						dy = tile[0][1].top - self.rect.bottom

		#update la position de l'entité
		if level_complete != True:
			self.rect.x += int(dx)
			self.rect.y += int(dy)

		#update scroll
		if self.type == "player1":
			if self.rect.right > SCREEN_WIDTH - SCROLL_THRESH or self.rect.left < SCROLL_THRESH -150:
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll,level_complete

	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1,50) == 1 and self.vel_y <= 0:
				self.update_action(0)
				self.idling = True
				self.idling_counter = 75
			if self.vision.colliderect(player.rect):
				self.update_action(0)
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)
					self.move_counter += 1
					if self.action == 0:
						self.vision.center = (self.rect.centerx + 123 * self.direction, self.rect.centery-15)
					else: 
						self.vision.center = (self.rect.centerx + 103 * self.direction, self.rect.centery-15)
					if DEBUG_VISION:
						pygame.draw.rect(screen,RED, self.vision)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.vision.center = (self.rect.centerx + 83 * self.direction, self.rect.centery-15)
					if self.vision.colliderect(player.rect):
						self.update_action(0)
						self.shoot()
					if DEBUG_VISION:
						pygame.draw.rect(screen,RED, self.vision)
					self.idling_counter -=1
					if self.idling_counter <= 0:
						self.idling = False

		#scroll
		self.rect.x += screen_scroll

	def update(self):
		self.update_animation()
		self.check_alive()
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1

	def update_animation(self):
		ANIMATION_COOLDOWN = 160
		ANIMATION_COOLDOWN_2 = 150
		self.image = self.animation_list[self.action][self.frame_index]
		self.img_hud_ext = self.hud_ext_list[self.hud_ext_index]
		#check du temps passé depuis le dernier update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN_2:
			self.hud_ext_index += 1
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#si l'animation a fini, reviens au début
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 9:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0
		if self.hud_ext_index >= len(self.hud_ext_list):
			self.hud_ext_index = 0

	def shoot(self):
		if self.ammo > 0 and self.shoot_cooldown == 0:
			self.shoot_cooldown = 20
			if self.type == "player1":
				bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery-10, self.direction,"blue")
			elif self.type == "enemy":
				bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery-10, self.direction,"pink")
			bullet_group.add(bullet)
			self.ammo -= 1
			audio_shoot.play()

	def update_action(self, new_action):
		#check si la nouvelle action est différente de la précedente
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def update_weapon(self, new_weapon):
		#check si la nouvelle arme  est différente de la précedente
		if new_weapon != self.weapon:
			self.weapon = new_weapon
			self.weapon_frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
		if self.type == "player1":
			screen.blit(self.img_hud_ext, self.rect2)
		if DEBUG_HITBOX:
			pygame.draw.rect(screen, RED, self.rect, 1)

class Bullet(pygame.sprite.Sprite):
	def __init__(self,x,y,direction,color):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 6
		self.color = color
		if self.color == "blue":
			self.image = blue_bullet_img
			self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*0.5), int(self.image.get_height()* 0.5)))
		elif self.color == "pink":
			self.image = pink_bullet_img
			self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*0.7), int(self.image.get_height()* 0.7)))
		self.rect = self.image.get_rect()
		if self.color == "blue":
			self.rect.center = (x,y+5)
		elif self.color == "pink":
			self.rect.center = (x,y-15)
		self.direction = direction

	def update(self):
		self.rect.x += (self.direction * self.speed) + screen_scroll
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				self.kill()
				if DEBUG_INVICIBLE == False:
					player.health -= d_difficulty["enemy_dmg"]
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					self.kill()
					enemy.health -= d_difficulty["player_dmg"]
		for tile in world.obstacle_list:
			if tile[0][1].colliderect(self.rect.x, self.rect.y, 5, 5):
				self.kill()

class Grenade(pygame.sprite.Sprite):
	def __init__(self,x,y,direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 135
		self.vel_y = -12
		self.speed = 6
		self.image = grenade_img
		self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*0.5), int(self.image.get_height()* 0.5)))
		self.rect = self.image.get_rect()
		self.rect.center = (x,y)
		self.direction = direction
		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self):
		self.vel_y += GRAVITY
		dx = self.speed * self.direction
		dy = self.vel_y

		for tile in world.obstacle_list:
			if tile[0][1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			if tile[0][1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y =0 
					dy = tile[1].top - self.rect.bottom

		self.rect.x += dx + screen_scroll
		self.rect.y += dy + 2

		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			audio_grenade.play()
			explosion = Explosion(self.rect.x,self.rect.y, 2)
			explosion_group.add(explosion)
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 1.5 and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 1.5:
				player.health -= d_difficulty["grenade_dmg"]
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 1.5 and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 1.5:
					enemy.health -= d_difficulty["grenade_dmg"]

class Explosion(pygame.sprite.Sprite):
	def __init__(self,x,y,scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(15):
			img = pygame.image.load(f'img/explosion/{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()* scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x,y-20)
		self.counter = 0

	def update(self):
		self.rect.x += screen_scroll
		EXPLOSION_SPEED = 5
		self.counter += 1
		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			if self.frame_index >= len(self.images):
				self.kill
			else:
				self.image = self.images[self.frame_index]

class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self,data):
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >=0 and tile <= 5:
						tile_data[1][3] -= 30
						self.obstacle_list.append([tile_data,tile])
					if tile >= 6 and tile <= 16:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					if tile == 17:
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)
					if tile >= 18 and tile <= 25:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					if tile >= 26 and tile <= 40:
						self.obstacle_list.append([tile_data,tile])
					if tile == 41:
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					if tile == 42:
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					if tile == 43:
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					if tile == 44:
						player = Character(x * TILE_SIZE, y * TILE_SIZE, 1.65, 3, "player1",30,5)
						health_bar = Healthbar(10,10,player.health, player.health)
					if tile == 45:
						enemy = Character(x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, "enemy",60,0)
						enemy_group.add(enemy)
		return player,health_bar

	def draw(self):
		for tile in self.obstacle_list:
			tile[0][1][0] += screen_scroll
			screen.blit(tile[0][0],tile[0][1])

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll
		if pygame.sprite.collide_rect(self,player):
			if self.item_type == 'Ammo':
				player.ammo += d_difficulty["ammo_box"]
			if self.item_type == 'Grenade':
				player.grenades += d_difficulty["grenade_box"]
			if self.item_type == 'Health':
				if player.health + d_difficulty["heal_box"] >= 100:
					player.health = 100
				else:
					player.health += d_difficulty["heal_box"]
			self.kill()

class Healthbar():
	def __init__(self,x,y,health,max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self,health):
		self.health = health
		ratio = self.health/self.max_health
		pygame.draw.rect(screen, RED, (self.x,self.y,120,40))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 120 * ratio, 40))


class Fade():
	def __init__(self,type,colour,speed):
		self.type = type
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0

	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.type == 1:
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
			if self.fade_counter >= SCREEN_WIDTH * 0.5:
				fade_complete = True
		if self.type == 2:
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
			if self.fade_counter >= SCREEN_WIDTH * 1:
				fade_complete = True
		if self.type == 3:
			pygame.draw.rect(screen, self.colour, (-400 + self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH - self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, -60 + self.fade_counter))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT - self.fade_counter + 60, SCREEN_WIDTH, SCREEN_HEIGHT))
			if self.fade_counter >= SCREEN_WIDTH * 0.5:
				fade_complete = True
		return fade_complete

#Création des transitions
play_transition = Fade(1,MENU_BG,4)
death_transition = Fade(2,MENU_BG,7)
end_transition = Fade(3,MENU_BG,4)

#Création des boutons
play_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 225, play_img, 2)
resume_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 225, resume_img, 2)
setting_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 50, setting_img, 2)
quit_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 + 125, quit_img, 2)
restart_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 225, restart_img, 2)
controls_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 250, controls_img, 2)
sound_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 90, sound_img, 2)
moins_music = button.Button(SCREEN_WIDTH - 350, SCREEN_HEIGHT // 2 - 120, moins_img, 1.25)
plus_music = button.Button(SCREEN_WIDTH - 180, SCREEN_HEIGHT // 2 - 120, plus_img, 1.25)
moins_effects = button.Button(SCREEN_WIDTH - 350, SCREEN_HEIGHT // 2 + 55, moins_img, 1.25)
plus_effects = button.Button(SCREEN_WIDTH - 180, SCREEN_HEIGHT // 2 + 55, plus_img, 1.25)
return_button = button.Button(10, 10, return_img, 1.5)
left_button = button.Button(SCREEN_WIDTH - 600, SCREEN_HEIGHT // 2 - 280, left_img_menu, 1.5)
right_button = button.Button(SCREEN_WIDTH - 600, SCREEN_HEIGHT // 2 - 180, right_img_menu, 1.5)
jump_button = button.Button(SCREEN_WIDTH - 600, SCREEN_HEIGHT // 2 - 80, jump_img_menu, 1.5)
rifle_button = button.Button(SCREEN_WIDTH - 600, SCREEN_HEIGHT // 2 + 20, rifle_img_menu, 1.5)
grenade_button = button.Button(SCREEN_WIDTH - 600, SCREEN_HEIGHT // 2 + 120, grenade_img_menu, 1.5)
hand_button = button.Button(SCREEN_WIDTH - 600, SCREEN_HEIGHT // 2 + 220, hand_img_menu, 1.5)
easy_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 100, easy_img, 2)
medium_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 + 25, medium_img, 2)
hard_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 + 150, hard_img, 2)
save_setting_button = button.Button(SCREEN_WIDTH - 730, SCREEN_HEIGHT // 2 + 100, save_setting_img, 1.25)
default_setting_button = button.Button(SCREEN_WIDTH - 360, SCREEN_HEIGHT // 2 + 100, default_setting_img, 1.25)

#Création des sprites groupes
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
with open(f'levels/level{level}_data.csv',newline='') as csvfile:
	reader = csv.reader(csvfile,delimiter=",")
	for x,row in enumerate(reader):
		for y,tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player,health_bar = world.process_data(world_data)

load_settings()
pygame.mixer.music.load("audio/music.wav")
pygame.mixer.music.set_volume(d_keys["music"])
pygame.mixer.music.play(-1, 0.0, 5000)
run = True
while run:
	clock.tick(FPS)

	if s_effects_load:
		for elem in l_effects:
			elem.set_volume(d_keys["effects"])
	if start_game == False or pause == True:
		screen.fill(MENU_BG)
		if setting == True:
			if sound == True:
				if return_button.draw(screen):
					sound = False
				draw_image(music_img,SCREEN_WIDTH // 3 - 100, SCREEN_HEIGHT // 2 - 137.5,2)
				draw_text(str(d_keys["music"]),font,WHITE,SCREEN_WIDTH - 250, SCREEN_HEIGHT // 2 - 97.5)
				draw_image(effects_img,SCREEN_WIDTH // 3 - 100, SCREEN_HEIGHT // 2 + 37.5,2)
				draw_text(str(d_keys["effects"]),font,WHITE,SCREEN_WIDTH - 250, SCREEN_HEIGHT // 2 + 77.5)
				if moins_music.draw(screen):
					if d_keys["music"] >= 0.05:
						d_keys["music"] = round(d_keys["music"] - 0.05,2)
						pygame.mixer.music.set_volume(d_keys["music"])
				if plus_music.draw(screen):
					if d_keys["music"] <= 0.95:
						d_keys["music"] = round(d_keys["music"] + 0.05,2)
						pygame.mixer.music.set_volume(d_keys["music"])
				if plus_effects.draw(screen):
					if d_keys["effects"] <= 0.95:
						d_keys["effects"] = round(d_keys["effects"] + 0.05,2)
						for elem in l_effects:
							elem.set_volume(d_keys["effects"])
				if moins_effects.draw(screen):
					if d_keys["effects"] >= 0.05:
						d_keys["effects"] = round(d_keys["effects"] - 0.05,2)
						for elem in l_effects:
							elem.set_volume(d_keys["effects"])
			elif control == True:
				if return_button.draw(screen):
					control = False
				if left_button.draw(screen) and pop_msg_key == False:
					change_key = True
					key_to_change = "left"
					pop_msg_key = True
				draw_text(pygame.key.name(d_keys["left"]),font2,WHITE,SCREEN_WIDTH - 255, SCREEN_HEIGHT // 2 - 260)
				if right_button.draw(screen) and pop_msg_key == False:
					change_key = True
					key_to_change = "right"
					pop_msg_key = True
				draw_text(pygame.key.name(d_keys["right"]),font2,WHITE,SCREEN_WIDTH - 255, SCREEN_HEIGHT // 2 - 160)
				if jump_button.draw(screen) and pop_msg_key == False:
					change_key = True
					key_to_change = "jump"
					pop_msg_key = True
				draw_text(pygame.key.name(d_keys["jump"]),font2,WHITE,SCREEN_WIDTH - 255, SCREEN_HEIGHT // 2 - 60)
				if rifle_button.draw(screen) and pop_msg_key == False:
					change_key = True
					key_to_change = "rifle"
					pop_msg_key = True
				draw_text(pygame.key.name(d_keys["rifle"]),font2,WHITE,SCREEN_WIDTH - 255, SCREEN_HEIGHT // 2 + 40)
				if grenade_button.draw(screen) and pop_msg_key == False:
					change_key = True
					key_to_change = "grenade"
					pop_msg_key = True
				draw_text(pygame.key.name(d_keys["grenade"]),font2,WHITE,SCREEN_WIDTH - 255, SCREEN_HEIGHT // 2 + 140)
				if hand_button.draw(screen) and pop_msg_key == False:
					change_key = True
					key_to_change = "hand"
					pop_msg_key = True
				draw_text(pygame.key.name(d_keys["hand"]),font2,WHITE,SCREEN_WIDTH - 255, SCREEN_HEIGHT // 2 + 240)
				if pop_msg_key:
					draw_image(key_input_img,SCREEN_WIDTH // 5, SCREEN_HEIGHT // 3.25,2)
			else:
				if return_button.draw(screen):
					setting = False
				if sound_button.draw(screen):
					sound = True
				if save_setting_button.draw(screen):
					save_settings()
				if default_setting_button.draw(screen):
					reset_settings()
				if controls_button.draw(screen):
					control = True
					time.sleep(0.06)
		elif choose_difficulty:
			draw_image(difficulty_img,SCREEN_WIDTH // 4, SCREEN_WIDTH - 755,1.5)
			if return_button.draw(screen):
				choose_difficulty = False
			if easy_button.draw(screen):
				d_difficulty = d_easy
				start_game,choose_difficulty,play_trans = f_start_game()
			if medium_button.draw(screen):
				d_difficulty = d_medium
				start_game,choose_difficulty,play_trans = f_start_game()
			if hard_button.draw(screen):
				d_difficulty = d_hard
				start_game,choose_difficulty,play_trans = f_start_game()
		else:
			if pause == True:
				if resume_button.draw(screen):
					l_audio_loading[random.randint(0,2)].play
					pause = False
					play_trans = True
			else:
				if play_button.draw(screen):
					choose_difficulty = True
			if setting_button.draw(screen):
				setting = True
				time.sleep(0.06)
			if quit_button.draw(screen):
				run = False
	elif end_game:
		screen.fill(MENU_BG)
		draw_text("Congratulations !",font3,WHITE,150, 200)
		draw_text("You finished the game!",font3,WHITE,105, 270)
		if quit_button.draw(screen):
			run = False
	else:
		draw_bg()
		world.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.draw()
			enemy.update()

		bullet_group.update()
		bullet_group.draw(screen)
		grenade_group.update()
		grenade_group.draw(screen)
		explosion_group.update()
		explosion_group.draw(screen)
		item_box_group.update()
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		decoration_group.update()
		exit_group.draw(screen)
		exit_group.update()

		health_bar.draw(player.health)
		player.draw()
		player.update()
		draw_text(f"Ammo: {player.ammo}",font,WHITE, 15, 60)
		draw_text(f"Grenade: {player.grenades}",font,WHITE, 15, 85)

		if play_trans:
			if play_transition.fade():
				tmp = random.randint(0,2)
				l_audio_loading[random.randint(0,2)].play()
				play_trans = False
				play_transition.fade_counter = 0
		elif play_trans_end:
			if end_transition.fade():
				play_trans_end = False
				end_game = True
		else:
			if player.alive:
				if shoot:
					player.shoot()
				elif grenade and player.grenades > 0:
					tmp_grenade = Grenade(player.rect.centerx + (player.rect.size[0]*0.15*player.direction), player.rect.top+10, player.direction)
					grenade_group.add(tmp_grenade)
					player.grenades -= 1
				shoot = False
				grenade = False
				if player.in_air:
					if player.weapon == 0:
						player.update_action(2) # 2 = Jump
					if player.weapon == 1:
						player.update_action(4) # 4 = Jump_Grnade
					if player.weapon == 2:
						player.update_action(7) # 7 = Jump_Rifle
				elif moving_left or moving_right:
					if player.weapon == 0:
						player.update_action(1) # 1 = Run
					if player.weapon == 1:
						player.update_action(5) # 5 = Run_Grenade
					if player.weapon == 2:
						player.update_action(8) # 8 = Run_Rifle
				else:
					if player.weapon == 0:
						player.update_action(0) # 0 = Idle
					if player.weapon == 1:
						player.update_action(3) # 4 = Idle_Grande
					if player.weapon == 2:
						player.update_action(6) # 6 = Idle_Rifle
				screen_scroll,level_complete = player.move(moving_left, moving_right)
				bg_scroll -= screen_scroll
				if level_complete:
					level += 1
					bg_scroll = 0
					world_data = restart_level()
					if level <= MAX_LEVELS:
						play_trans = True
						with open(f'levels/level{level}_data.csv',newline='') as csvfile:
							reader = csv.reader(csvfile,delimiter=",")
							for x,row in enumerate(reader):
								for y,tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player,health_bar = world.process_data(world_data)
					else:
						pygame.mixer.music.stop()
						audio_end.play()
						play_trans_end = True
						moving_left,moving_right = False,False

				if player.temp_weapon == 0:
					player.update_weapon(0) #0 = no weapon
				if player.temp_weapon == 1:
					player.update_weapon(1) #1 = Grenade
				if player.temp_weapon == 2:
					player.update_weapon(2) #1 = rifle
			else:
				screen_scroll = 0
				if s_audio_death == True:
						audio_death.play()
						s_audio_death = False
				if death_transition.fade():
					if restart_button.draw(screen):
						l_audio_loading[random.randint(0,2)].play()
						s_audio_death = True
						bg_scroll = 0 
						world_data = restart_level()
						with open(f'levels/level{level}_data.csv',newline='') as csvfile:
							reader = csv.reader(csvfile,delimiter=",")
							for x,row in enumerate(reader):
								for y,tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player,health_bar = world.process_data(world_data)

	for event in pygame.event.get():
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 5:
				if player.temp_weapon > 0:
					player.temp_weapon -= 1
			if event.button == 4:
				if player.temp_weapon < 3:
					player.temp_weapon += 1
			if event.button == 1 and player.weapon == 2:
				shoot = True
			if event.button == 1 and player.weapon == 1:
				grenade = True
		#quit
		if event.type == pygame.QUIT:
			run = False
		#touche appuyées
		if event.type == pygame.KEYDOWN:
			if change_key == True:
				d_keys[key_to_change] = event.key
				change_key = False
				pop_msg_key = False
			if event.key == d_keys["left"]:
				moving_left = True
			if event.key == d_keys["right"]:
				moving_right = True
			if event.key == d_keys["jump"] and player.alive and start_game:
				player.jump = True
				audio_jump.play()
			if event.key == d_keys["rifle"]:
				player.temp_weapon = 2
			if event.key == d_keys["grenade"]:
				player.temp_weapon = 1
			if event.key == d_keys["hand"]:
				player.temp_weapon = 0
			if event.key == pygame.K_F1:
				DEBUG_HITBOX = not DEBUG_HITBOX
			if event.key == pygame.K_F2:
				DEBUG_VISION = not DEBUG_VISION
			if event.key == pygame.K_F3:
				DEBUG_INVICIBLE = not DEBUG_INVICIBLE
			if event.key == pygame.K_ESCAPE:
				if start_game == False:
					if setting == True:
						if control == True:
							control = not control
						elif sound == True:
							sound = not sound
						else:
							setting = not setting
					elif choose_difficulty == True:
						choose_difficulty = not choose_difficulty
				else:
					if setting == True:
						if control == True:
							control = not control
						elif sound == True:
							sound = not sound
						else:
							setting = not setting
					else:
						pause = not pause
						moving_right,moving_left = False,False
						player.update_action(0)
						play_trans = True
		#touches relachées
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_q or event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False

	pygame.display.update()

pygame.quit()