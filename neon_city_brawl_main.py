import pygame
import os
from pygame import mixer
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Neon City Brawl')

#initialisation framerate
clock = pygame.time.Clock()
FPS = 60

#varibales du jeu
GRAVITY = 0.5
TILE_SIZE = 40

#Debug
DEBUG_HITBOX = False
DEBUG_VISION = False

#initialisation action du player
moving_left = False
moving_right = False
shoot = False
grenade = False

#chargement des images
pink_bullet_img = pygame.image.load("img/icons/pink_bullet.png").convert_alpha()
blue_bullet_img = pygame.image.load("img/icons/blue_bullet.png").convert_alpha()
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
ammo_box_img = pygame.image.load("img/tile/41.png").convert_alpha()
grenade_box_img = pygame.image.load("img/tile/42.png").convert_alpha()
health_box_img = pygame.image.load("img/tile/43.png").convert_alpha()
item_boxes = {'Ammo':ammo_box_img, 'Grenade': grenade_box_img, 'Health': health_box_img}

#couleurs
BG = (41, 41, 41)
RED = (255, 0, 0)
GREEN = (53, 186, 28)
WHITE = (255, 255, 255)

def draw_bg():
	screen.fill(BG)
	#ligne temporaire
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

font = pygame.font.SysFont('Futura',30)
def draw_text(text, font, text_col, x , y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x,y))

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
		self.vision = pygame.Rect(0,0,150 ,20)
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
		pygame.Rect.inflate_ip(self.rect, -15, 0)

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

		#application de la gravité
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#check collision avec le sol
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.in_air = False

		#update la position de l'entité
		self.rect.x += int(dx)
		self.rect.y += int(dy)

	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1,150) == 1:
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
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
					if DEBUG_VISION:
						pygame.draw.rect(screen,RED, self.vision)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -=1
					if self.idling_counter <= 0:
						self.idling = False

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
		self.rect.x += (self.direction * self.speed)
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				self.kill()
				player.health -= 15
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					self.kill()
					enemy.health -= 25

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

	def update(self):
		self.vel_y += GRAVITY
		dx = self.speed * self.direction
		dy = self.vel_y

		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.speed = 0

		if self.rect.left + dx < 0 or self.rect.right + dx> SCREEN_WIDTH:
			self.direction *= -1

		self.rect.x += dx
		self.rect.y += dy + 2

		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			explosion = Explosion(self.rect.x,self.rect.y, 2)
			explosion_group.add(explosion)
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50

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
		self.rect.center = (x,y-23)
		self.counter = 0

	def update(self):
		EXPLOSION_SPEED = 5
		self.counter += 1
		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			if self.frame_index >= len(self.images):
				self.kill
			else:
				self.image = self.images[self.frame_index]

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		if pygame.sprite.collide_rect(self,player):
			if self.item_type == 'Ammo':
				player.ammo += 15
			if self.item_type == 'Grenade':
				player.grenades += 3
			if self.item_type == 'Health':
				if player.health + 50 >= 100:
					player.health = 100
				else:
					player.health += 50
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

bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

item_box = ItemBox('Ammo', 550, 260)
item_box_group.add(item_box)
item_box2 = ItemBox('Grenade', 750, 260)
item_box_group.add(item_box2)
item_box3 = ItemBox('Health', 650, 260)
item_box_group.add(item_box3)

player = Character(200, 200, 1.85, 2, "player1", 30, 5)
health_bar = Healthbar(10,10,player.health, player.health)
enemy = Character(400, 200, 1.85, 2, "enemy", 60, 0)
enemy2 = Character(650, 200, 1.85, 2, "enemy", 60, 0)
enemy_group.add(enemy)
enemy_group.add(enemy2)

run = True
while run:
	clock.tick(FPS)

	draw_bg()
	draw_text(f"Ammo: {player.ammo}",font,WHITE, 15, 60)
	draw_text(f"Grenade: {player.grenades}",font,WHITE, 15, 85)

	health_bar.draw(player.health)
	player.draw()
	player.update()

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
		player.move(moving_left, moving_right)

		if player.temp_weapon == 0:
			player.update_weapon(0) #0 = no weapon
		if player.temp_weapon == 1:
			player.update_weapon(1) #1 = Grenade
		if player.temp_weapon == 2:
			player.update_weapon(2) #1 = rifle

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
			if event.key == pygame.K_q or event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE and player.alive:
				player.jump = True
			if event.key == pygame.K_1:
				player.temp_weapon = 2
			if event.key == pygame.K_2:
				player.temp_weapon = 1
			if event.key == pygame.K_3:
				player.temp_weapon = 0
			if event.key == pygame.K_F1:
				DEBUG_HITBOX = not DEBUG_HITBOX
			if event.key == pygame.K_F2:
				DEBUG_VISION = not DEBUG_VISION
		#touches relachées
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_q or event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False

	pygame.display.update()

pygame.quit()