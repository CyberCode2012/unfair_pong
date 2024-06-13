import arcade
import random
import time

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Unfair Pong"

PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_SIZE = 20
BALL_SPEED_INCREMENT = 0.1
EVENT_INTERVAL = 15  # Events happen every 15 seconds
WINNING_SCORE = 10

class PongGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.balls = []
        self.left_paddle = None
        self.right_paddle = None
        self.left_paddle_speed = 0
        self.right_paddle_speed = 0
        self.right_paddle_speed_value = 5
        self.miss_message = ""
        self.miss_message_time = 0
        self.score = 0
        self.last_event_time = time.time()
        self.start_time = time.time()
        self.countdown_active = True
        self.last_event = None
        self.setup()

    def setup(self):
        self.balls.append(self.create_ball())
        self.left_paddle = arcade.SpriteSolidColor(PADDLE_WIDTH, PADDLE_HEIGHT, arcade.color.WHITE)
        self.left_paddle.center_x = PADDLE_WIDTH // 2 + 10
        self.left_paddle.center_y = SCREEN_HEIGHT // 2

        self.right_paddle = arcade.SpriteSolidColor(PADDLE_WIDTH, PADDLE_HEIGHT, arcade.color.WHITE)
        self.right_paddle.center_x = SCREEN_WIDTH - PADDLE_WIDTH // 2 - 10
        self.right_paddle.center_y = SCREEN_HEIGHT // 2

    def create_ball(self):
        ball = arcade.SpriteCircle(BALL_SIZE // 2, arcade.color.WHITE)
        ball.center_x = SCREEN_WIDTH // 2
        ball.center_y = SCREEN_HEIGHT // 2
        ball.change_x = random.choice([3, -3])
        ball.change_y = random.choice([3, -3])
        return ball

    def on_draw(self):
        arcade.start_render()
        for ball in self.balls:
            ball.draw()
        self.left_paddle.draw()
        self.right_paddle.draw()

        # Draw the score
        arcade.draw_text(f"Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50,
                        arcade.color.WHITE, 24, anchor_x="center")

        # Draw the miss message if there is one
        if self.miss_message:
            arcade.draw_text(self.miss_message, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                            arcade.color.RED, 24, anchor_x="center")

        # Draw the countdown message
        if self.countdown_active:
            countdown = 5 - int(time.time() - self.start_time)
            arcade.draw_text(f"Starting in: {countdown}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                            arcade.color.GREEN, 24, anchor_x="center")
            arcade.draw_text("Get a score of 10 to win!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
                            arcade.color.YELLOW, 24, anchor_x="center")

        # Draw the winning message
        if self.score >= WINNING_SCORE:
            arcade.draw_text("You win!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
                            arcade.color.YELLOW, 36, anchor_x="center")

    def on_update(self, delta_time):
        if self.countdown_active:
            if time.time() - self.start_time < 5:
                return
            else:
                self.countdown_active = False
                self.start_time = time.time()  # Reset start time to avoid immediate event trigger

        for ball in self.balls:
            ball.center_x += ball.change_x
            ball.center_y += ball.change_y

            # Ball collision with top and bottom
            if ball.top > SCREEN_HEIGHT or ball.bottom < 0:
                ball.change_y *= -1

            # Ball collision with paddles
            if arcade.check_for_collision(ball, self.right_paddle) or arcade.check_for_collision(ball, self.left_paddle):
                ball.change_x *= -1
                ball.change_x += BALL_SPEED_INCREMENT if ball.change_x > 0 else -BALL_SPEED_INCREMENT
                ball.change_y += BALL_SPEED_INCREMENT if ball.change_y > 0 else -BALL_SPEED_INCREMENT

            # Ball out of bounds
            if ball.left > SCREEN_WIDTH:
                self.miss_message = "Lol you're such a noob"
                self.miss_message_time = time.time()
                self.score -= 1
                self.balls.remove(ball)
                if not self.balls:
                    self.balls.append(self.create_ball())

            if ball.right < 0:
                self.miss_message = ""
                self.score += 1
                self.balls.remove(ball)
                if not self.balls:
                    self.balls.append(self.create_ball())

        # Left paddle tracks the ball
        if self.left_paddle.center_y < self.balls[0].center_y:
            self.left_paddle.center_y += self.right_paddle_speed_value
        elif self.left_paddle.center_y > self.balls[0].center_y:
            self.left_paddle.center_y -= self.right_paddle_speed_value

        # Keep left paddle within screen bounds
        if self.left_paddle.top > SCREEN_HEIGHT:
            self.left_paddle.top = SCREEN_HEIGHT
        if self.left_paddle.bottom < 0:
            self.left_paddle.bottom = 0

        self.right_paddle.center_y += self.right_paddle_speed

        # Keep right paddle within screen bounds
        if self.right_paddle.top > SCREEN_HEIGHT:
            self.right_paddle.top = SCREEN_HEIGHT
        if self.right_paddle.bottom < 0:
            self.right_paddle.bottom = 0

        # Remove miss message after 2 seconds
        if time.time() - self.miss_message_time > 2:
            self.miss_message = ""

        # Check for random events every EVENT_INTERVAL seconds
        if time.time() - self.last_event_time > EVENT_INTERVAL:
            self.trigger_random_event()
            self.last_event_time = time.time()

    def trigger_random_event(self):
        events = ["shorten_paddle", "multiply_ball", "speed_up_ball"]
        events = [event for event in events if event != self.last_event]
        event = random.choice(events)
        self.last_event = event

        if event == "shorten_paddle":
            self.right_paddle.height = PADDLE_HEIGHT // 2
            arcade.schedule(self.reset_paddle_size, 10)
        elif event == "multiply_ball":
            for _ in range(2):
                self.balls.append(self.create_ball())
        elif event == "speed_up_ball":
            for ball in self.balls:
                ball.change_x *= 1.5
                ball.change_y *= 1.5

    def reset_paddle_size(self, delta_time):
        self.right_paddle.height = PADDLE_HEIGHT

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.right_paddle_speed = self.right_paddle_speed_value
        elif key == arcade.key.DOWN:
            self.right_paddle_speed = -self.right_paddle_speed_value

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.right_paddle_speed = 0

def main():
    game = PongGame()
    arcade.run()

if __name__ == "__main__":
    main()
