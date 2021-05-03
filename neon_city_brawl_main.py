import pygame
import os

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
BG = (249, 148, 143)
RED = (255, 0, 0)

def draw_bg():
	screen.fill(BG)
	#ligne temporaire
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

class Character(pygame.sprite.Sprite):
	def __init__(self, x, y, scale, speed):
		pygame.sprite.Sprite.__init__(self)
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
		self.update_time = pygame.time.get_ticks()

		animation_types = ['Idle', 'Run', 'Jump']
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
		self.rect.x += dx
		self.rect.y += dy

	def update_animation(self):
		ANIMATION_COOLDOWN = 140
		self.image = self.animation_list[self.action][self.frame_index]
		#check du temps passé depuis le dernier update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#si l'animation a fini, reviens au début
		if self.frame_index >= len(self.animation_list[self.action]):
			self.frame_index = 0

	def update_action(self, new_action):
		#check si la nouvelle action est différente de la précedente
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


player = Character(200, 200, 4, 4)

run = True
while run:

	clock.tick(FPS)

	draw_bg()

	'''player.draw()
	player.update_animation()'''

	if player.alive:
		if player.in_air:
			player.update_action(2) #2 = Jump
		elif moving_left or moving_right:
			player.update_action(1) #1 = Run
		else:
			player.update_action(0) #0 = Idle
		player.move(moving_left, moving_right)

	for event in pygame.event.get():
		#quit
		if event.type == pygame.QUIT:
			run = False
		#touche appuyées
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE and player.alive:
				player.jump = True

		#touches relachées
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_q:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False

	pygame.display.update()

pygame.quit()