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
GRAVITY = 0.75

#initialisation action du player
moving_left = False
moving_right = False

#couleurs
BG = (41, 41, 41)
RED = (255, 0, 0)
GREEN = (53, 186, 28)

def draw_bg():
	screen.fill(BG)
	#ligne temporaire
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


class Character(pygame.sprite.Sprite):
	def __init__(self, x, y, scale, speed):
		pygame.sprite.Sprite.__init__(self)
		self.health = 100
		self.alive = True
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

		self.update_time = pygame.time.get_ticks()

		self.weapon = 0
		self.temp_weapon = 0

		animation_types = ['Idle', 'Run', 'Jump','Idle_Sword','Jump_Sword','Run_Sword','Idle_Rifle','Jump_Rifle','Run_Rifle']
		for animation in animation_types:
			#liste temporaire pour stockage de toutes les img d'une animation
			temp_list = []
			#longueur du fichier
			longueur_fichier = len(os.listdir(f'img/player1/{animation}'))
			#ouverture du fichier
			for i in range(longueur_fichier):
				img = pygame.image.load(f'img/player1/{animation}/{i}.png')
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

		self.hud_ext_list = []
		longueur_fichier_2 = len(os.listdir(f'img/hud'))
		for j in range(longueur_fichier_2):
			img2 = pygame.image.load(f'img/hud/{j}.png')
			self.hud_ext_list.append(img2)
		self.img_hud_ext = self.hud_ext_list[self.hud_ext_index]
		self.rect2 = self.img_hud_ext.get_rect()
		self.rect2.center = (70, 30)

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
			self.vel_y = -13
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
			self.frame_index = 0
		if self.hud_ext_index >= len(self.hud_ext_list):
			self.hud_ext_index = 0


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
		screen.blit(self.img_hud_ext, self.rect2)

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

player = Character(200, 200, 4, 4)
health_bar = Healthbar(10,10,player.health, player.health)

run = True
while run:

	clock.tick(FPS)

	draw_bg()

	health_bar.draw(player.health)
	player.draw()
	player.update_animation()

	if player.alive:
		if player.in_air:
			if player.weapon == 0:
				player.update_action(2) # 2 = Jump
			if player.weapon == 1:
				player.update_action(4) # 4 = Jump_Sword
			if player.weapon == 2:
				player.update_action(7) # 7 = Jump_Rifle
		elif moving_left or moving_right:
			if player.weapon == 0:
				player.update_action(1) # 1 = Run
			if player.weapon == 1:
				player.update_action(5) # 5 = Run_Sword
			if player.weapon == 2:
				player.update_action(8) # 8 = Run_Rifle
		else:
			if player.weapon == 0:
				player.update_action(0) # 0 = Idle
			if player.weapon == 1:
				player.update_action(3) # 4 = Idle_Sword
			if player.weapon == 2:
				player.update_action(6) # 6 = Idle_Rifle
		player.move(moving_left, moving_right)


		if player.temp_weapon == 0:
			player.update_weapon(0) #0 = no weapon
		if player.temp_weapon == 1:
			player.update_weapon(1) #1 = sword
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
				player.temp_weapon = 0
			if event.key == pygame.K_2:
				player.temp_weapon = 1
			if event.key == pygame.K_3:
				player.temp_weapon = 2

		#touches relachées
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_q or event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False

	pygame.display.update()

pygame.quit()