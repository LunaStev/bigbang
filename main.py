import pygame
import numpy as np
import sys
from scipy.spatial import cKDTree

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Big Bang Simulation")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

G = 6.67430e-11 
MASS_OF_PARTICLE = 1e20
EXPLOSION_VELOCITY = 3e8 
UNIVERSE_AGE = 13.8e9 * 365 * 24 * 3600
SIMULATION_SPEED = UNIVERSE_AGE / 60 

zoom = 1.0

class Particle:
    def __init__(self, mass, position, velocity, color):
        self.mass = mass
        self.position = np.array(position, dtype='float64')
        self.velocity = np.array(velocity, dtype='float64')
        self.force = np.zeros(2, dtype='float64')
        self.color = color

    def update_position(self, dt):
        self.velocity += self.force / self.mass * dt
        self.position += self.velocity * dt

    def draw(self, screen, width, height):
        x, y = int(self.position[0] / 1e26 * width * zoom + width / 2), int(self.position[1] / 1e26 * height * zoom + height / 2)
        if 0 <= x < width and 0 <= y < height:
            pygame.draw.circle(screen, self.color, (x, y), max(1, int(2 * zoom)))

num_particles = 1000
particles = []

for _ in range(num_particles):
    angle = np.random.uniform(0, 2 * np.pi)
    distance = np.random.uniform(0, 1e10) 
    position = distance * np.array([np.cos(angle), np.sin(angle)])
    velocity = EXPLOSION_VELOCITY * np.array([np.cos(angle), np.sin(angle)])
    color = (np.random.randint(100, 256), np.random.randint(100, 256), np.random.randint(100, 256))
    particles.append(Particle(MASS_OF_PARTICLE, position, velocity, color))

dt = SIMULATION_SPEED / 60  

def set_resolution():
    global WIDTH, HEIGHT, screen
    WIDTH = int(input("화면 너비를 입력하세요: "))
    HEIGHT = int(input("화면 높이를 입력하세요: "))
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("우주 빅뱅 시뮬레이션")

def calculate_forces(particles):
    positions = np.array([p.position for p in particles])
    tree = cKDTree(positions)
    for i, particle in enumerate(particles):
        distances, indices = tree.query(particle.position, k=num_particles, distance_upper_bound=np.inf)
        forces = np.zeros(2)
        for j, distance in zip(indices[1:], distances[1:]): 
            if j < num_particles: 
                direction = positions[j] - particle.position
                force_magnitude = G * MASS_OF_PARTICLE**2 / distance**2
                forces += force_magnitude * direction / distance
        particle.force = forces


running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                set_resolution() 
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                zoom *= 1.1 
            elif event.key == pygame.K_MINUS:
                zoom /= 1.1 

    screen.fill(BLACK)

    calculate_forces(particles)
    for particle in particles:
        particle.update_position(dt)
        particle.draw(screen, WIDTH, HEIGHT)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
