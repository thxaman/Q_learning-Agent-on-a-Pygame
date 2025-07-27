import math
import pygame
from sys import exit
from random import randint

# --- CONSTANTS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 538
GROUND_HEIGHT = 425
FPS = 60

# Gameplay Constants
GRAVITY = 0.2
JUMP_STRENGTH = -4
PIPE_SPEED = 5
PIPE_GAP = 140
PIPE_SPAWN_RATE = 1200  # milliseconds

# File Paths
FONT_PATH_IMPACT = "impact"
FONT_PATH_PAPYRUS = "papyrus"
BIRD_IMGS = [
    "graphics/yellowbird-upflap.png",
    "graphics/yellowbird-midflap.png",
    "graphics/yellowbird-downflap.png",
]
PIPE_IMG = "graphics/pipe-green.png"
BG_IMG = "graphics/background-night.png"
GROUND_IMG = "graphics/base.png"
DEAD_BIRD_IMG = "graphics/yellowbird-dead.png"


# --- CLASSES ---


class Bird(pygame.sprite.Sprite):
    """
    Represents the player's bird. Handles animation, gravity, and jumping.
    """

    def __init__(self, bird_images):
        super().__init__()
        self.animation_frames = [
            pygame.image.load(img).convert_alpha() for img in bird_images
        ]
        self.animation_index = 0

        self.image = self.animation_frames[self.animation_index]
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT / 2))

        self.gravity = 5
        self.mask = pygame.mask.from_surface(self.image)

    def _animate(self):
        """Cycles through bird flapping animations."""
        self.animation_index += 0.15
        if self.animation_index >= len(self.animation_frames):
            self.animation_index = 0
        self.image = self.animation_frames[int(self.animation_index)]

    def _apply_gravity(self):
        """Applies gravity to the bird, making it fall."""
        self.gravity += GRAVITY
        self.rect.y += self.gravity

    def _rotate(self):
        """Rotates the bird image based on its vertical velocity."""
        rotated_image = pygame.transform.rotozoom(self.image, -self.gravity * 4, 1)
        self.image = rotated_image
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        """Makes the bird jump upwards."""
        self.gravity = JUMP_STRENGTH

    def reset(self):
        """Resets the bird's position and gravity for a new game."""
        self.rect.center = (100, SCREEN_HEIGHT / 2)
        self.gravity = 0

    def update(self):
        """Main update method called each frame."""
        self._apply_gravity()
        self._animate()
        self._rotate()


class Pipe(pygame.sprite.Sprite):
    """
    Represents a single pipe obstacle (either upright or inverted).
    """

    def __init__(self, pos, image, is_inverted=False):
        super().__init__()
        self.image = image
        if is_inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midbottom=pos)
        else:
            self.rect = self.image.get_rect(midtop=pos)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """Moves the pipe to the left and destroys it when off-screen."""
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()


class Game:
    """
    The main game class. Manages the game loop, state, assets, and all objects.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.state = "START"  # Game states: START, PLAYING, GAME_OVER
        self.score = 0
        self.start_time = 0
        self.bg_scroll = 0
        self.ground_scroll = 0

        # Load assets once
        self._load_assets()

        # Create sprite groups
        self.bird_group = pygame.sprite.GroupSingle()
        self.pipe_group = pygame.sprite.Group()

        # Create player
        self.player = Bird(BIRD_IMGS)
        self.bird_group.add(self.player)

        # Setup timers
        self.pipe_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.pipe_timer, PIPE_SPAWN_RATE)

    def _load_assets(self):
        """Loads all game images and fonts."""
        # Fonts
        self.score_font = pygame.font.SysFont(FONT_PATH_IMPACT, 30)
        self.lidar_font = pygame.font.SysFont(FONT_PATH_IMPACT, 15)
        self.game_over_font = pygame.font.SysFont(FONT_PATH_PAPYRUS, 40, bold=True)
        self.prompt_font = pygame.font.SysFont(FONT_PATH_IMPACT, 30)

        # Images
        self.bg_surface = pygame.image.load(BG_IMG).convert()
        self.ground_surface = pygame.image.load(GROUND_IMG).convert()
        self.pipe_surface = pygame.image.load(PIPE_IMG).convert_alpha()
        self.dead_bird_surface = pygame.image.load(DEAD_BIRD_IMG).convert_alpha()
        self.dead_bird_surface = pygame.transform.rotozoom(
            self.dead_bird_surface, 20, 2
        )

    def _handle_events(self):
        """Handles all player input and events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.state == "PLAYING":
                    self.player.jump()
                elif self.state == "START" or self.state == "GAME_OVER":
                    self._reset_game()
                    self.state = "PLAYING"

            if event.type == self.pipe_timer and self.state == "PLAYING":
                self._spawn_pipes()

    def _LIDAR(self):
        """Simulates a LIDAR system to detect obstacles in the game."""
        max_distance = 500
        start_pos = self.player.rect.center
        angle_total = 190
        angle_step = 10
        array = {}
        for angle in range(0, angle_total, angle_step):
            actual_dist = max_distance
            end_pos = (
                start_pos[0] + max_distance * math.sin(math.radians(angle)),
                start_pos[1] + max_distance * math.cos(math.radians(angle)),
            )
            if end_pos[1] > GROUND_HEIGHT:
                end_pos = (end_pos[0], GROUND_HEIGHT)
                actual_dist = math.hypot(
                    end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
                )
            if end_pos[1] < 0:
                end_pos = (end_pos[0],0)
                actual_dist = math.hypot(
                    end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
                )
            hit_point = end_pos
            for pipe in self.pipe_group:
                clipp = pipe.rect.clipline(start_pos, end_pos)
                if clipp:
                    intersection = clipp[0]
                    dist = math.hypot(
                        intersection[0] - start_pos[0], intersection[1] - start_pos[1]
                    )
                    if dist < actual_dist:
                        actual_dist = dist
                        hit_point = intersection
            pygame.draw.line(
                self.screen, (0, 255, 0), start_pos=start_pos, end_pos=hit_point
            )
            pygame.draw.circle(self.screen, (255, 0, 0), hit_point, 4)
            dist_text = self.lidar_font.render(f"{actual_dist:.0f}", True, (0, 0, 0))
            self.screen.blit(dist_text, (hit_point[0] - 10, hit_point[1] + 5))
            # print(hit_point, actual_dist)
            array[angle] = actual_dist
        print(array)

    def _spawn_pipes(self):
        """
        Spawns pipes based on the original game's random logic,
        which includes pairs, single top pipes, and single bottom pipes.
        """
        # Randomly choose one of the three original spawn patterns
        spawn_type = ["both", "upright", "inverted"][randint(0, 2)]
        x_pos = SCREEN_WIDTH + 50  # Start pipes just off-screen

        if spawn_type == "both":
            # Spawns a standard pair of pipes with a gap
            bottom_pipe_y = randint(220, 350)
            top_pipe_y = (
                bottom_pipe_y - PIPE_GAP
            )  # Calculate top pipe pos based on bottom

            bottom_pipe = Pipe((x_pos, bottom_pipe_y), self.pipe_surface)
            top_pipe = Pipe((x_pos, top_pipe_y), self.pipe_surface, is_inverted=True)
            self.pipe_group.add(bottom_pipe, top_pipe)

        elif spawn_type == "upright":
            # Spawns only a bottom pipe
            bottom_pipe_y = randint(220, 350)
            bottom_pipe = Pipe((x_pos, bottom_pipe_y), self.pipe_surface)
            self.pipe_group.add(bottom_pipe)

        elif spawn_type == "inverted":
            # Spawns only a top pipe.
            # The original code's logic resulted in the bottom edge of the
            # top pipe being between y=120 and y=320. This replicates that.
            top_pipe_y = randint(120, 320)
            top_pipe = Pipe((x_pos, top_pipe_y), self.pipe_surface, is_inverted=True)
            self.pipe_group.add(top_pipe)

    def _check_collisions(self):
        """Checks for collisions between the bird and pipes or screen boundaries."""
        # Collision with pipes
        if pygame.sprite.spritecollide(
            self.player,
            self.pipe_group,
            False,
            pygame.sprite.collide_mask,
        ):
            self.state = "GAME_OVER"

        # Collision with ground or ceiling
        if not (0 < self.player.rect.centery < GROUND_HEIGHT):
            self.state = "GAME_OVER"

    def _update(self):
        """Updates all game objects based on the current state."""
        if self.state == "PLAYING":
            self.bird_group.update()
            self.pipe_group.update()
            self._check_collisions()
            self.score = (pygame.time.get_ticks() - self.start_time) // 1000

    def _draw_scrolling_bg(self):
        """Draws the continuously scrolling background and ground."""
        bg_width = self.bg_surface.get_width()
        ground_width = self.ground_surface.get_width()

        # Background
        for i in range(4):
            self.screen.blit(self.bg_surface, (i * bg_width + self.bg_scroll, 0))
        self.bg_scroll -= 1
        if abs(self.bg_scroll) > bg_width:
            self.bg_scroll = 0

        # Ground
        for i in range(4):
            self.screen.blit(
                self.ground_surface,
                (i * ground_width + self.ground_scroll, GROUND_HEIGHT),
            )
        self.ground_scroll -= PIPE_SPEED
        if abs(self.ground_scroll) > ground_width:
            self.ground_scroll = 0

    def _draw(self):
        """Draws all elements to the screen."""
        self._draw_scrolling_bg()

        if self.state == "PLAYING":
            self.bird_group.draw(self.screen)
            self.pipe_group.draw(self.screen)
            self._LIDAR()
            self._draw_score()
        elif self.state == "START":
            self._draw_start_screen()
        elif self.state == "GAME_OVER":
            self.pipe_group.draw(self.screen)  # Draw pipes at the moment of death
            self._draw_game_over_screen()

        pygame.display.update()

    def _draw_score(self):
        score_surf = self.score_font.render(f"Score: {self.score}", True, "black")
        score_rect = score_surf.get_rect(topleft=(20, 10))
        self.screen.blit(score_surf, score_rect)

    def _draw_start_screen(self):
        self.player.rect.center = (100, SCREEN_HEIGHT / 2)
        self.bird_group.draw(self.screen)
        prompt_surf = self.prompt_font.render("Press SPACE to Play", True, "white")
        prompt_rect = prompt_surf.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60)
        )
        self.screen.blit(prompt_surf, prompt_rect)

    def _draw_game_over_screen(self):
        self.screen.fill((122, 165, 202))

        # Dead bird image
        dead_bird_rect = self.dead_bird_surface.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        )
        self.screen.blit(self.dead_bird_surface, dead_bird_rect)

        # Game over text
        game_over_surf = self.game_over_font.render("GAME OVER", True, "black")
        game_over_rect = game_over_surf.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 6)
        )
        self.screen.blit(game_over_surf, game_over_rect)

        # Final score
        score_surf = self.score_font.render(
            f"Your Score Is: {self.score}", True, "white"
        )
        score_rect = score_surf.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
        )
        self.screen.blit(score_surf, score_rect)

        # Prompt to play again
        prompt_surf = self.prompt_font.render(
            "Press SPACE to Play Again", True, "white"
        )
        prompt_rect = prompt_surf.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60)
        )
        self.screen.blit(prompt_surf, prompt_rect)

    def _reset_game(self):
        """Resets the game to its initial state for a new round."""
        self.player.reset()
        self.pipe_group.empty()
        self.score = 0
        self.start_time = pygame.time.get_ticks()

    def run(self):
        """The main game loop."""
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)


# --- ENTRY POINT ---
if __name__ == "__main__":
    game = Game()
    game.run()
