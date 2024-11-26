"""
Modifikasi yang ditambahkan
1. Peningkatan Kecepatan Bola Secara Bertahap
2. Penambahan Skor
3. Fitur Pause/Resume (Dengan menekan tombol 'p')
4. Emoji saat Kehilangan Nyawa (Saat bola keluar layar, emoji 😢 ditampilkan)
5. Emoji saat Kalah (Emoji 💀 ditampilkan sebagai bagian dari pesan "Game Over")
6. Perubahan warna
"""

import tkinter as tk
import time


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.base_speed = 5
        self.speed = self.base_speed
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='crimson')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()
                self.speed += 0.1  # Increase speed after hitting a brick


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#8C0004')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#f08080', 2: '#f8ad9d', 3: '#ffdab9'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#FCEDE0',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.score_text = None
        self.text = None
        self.paused = False
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))
        self.canvas.bind('p', self.toggle_pause)

    def setup_game(self):
        self.add_ball()
        self.update_hud()
        if self.text is not None:
            self.canvas.delete(self.text)
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_hud(self):
        lives_text = 'Lives: %s' % self.lives
        score_text = 'Score: %s' % self.score
        if self.hud is None:
            self.hud = self.draw_text(50, 20, lives_text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=lives_text)
        if self.score_text is None:
            self.score_text = self.draw_text(150, 20, score_text, 15)
        else:
            self.canvas.itemconfig(self.score_text, text=score_text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        if self.paused:
            return
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = 0
            self.show_message('You win! 🎉')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = 0  # Hentikan bola
            self.lives -= 1
            if self.lives < 0:
                self.show_message('You Lose! 💀 Game Over!')
            else:
                # Tampilkan emoji 😢 saat kehilangan nyawa
                emoji = self.draw_text(300, 200, '😢', size='50')
                self.after(1000, lambda: self.canvas.delete(emoji))  # Hapus emoji setelah 1 detik
                self.after(1000, self.setup_game)  # Restart game setelah 1 detik
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        if objects:
            self.ball.collide(objects)
            for obj in objects:
                if isinstance(obj, Brick):
                    self.score += 10
                    self.update_hud()

    def show_message(self, message):
        if self.text is not None:
            self.canvas.delete(self.text)
        self.text = self.draw_text(300, 200, message, 30)

    def toggle_pause(self, event):
        self.paused = not self.paused
        if self.paused:
            self.show_message('Paused')
        else:
            self.canvas.delete(self.text)
        self.game_loop()



def add_ball(self):
    if self.ball is not None:
        self.ball.delete()
    paddle_coords = self.paddle.get_position()
    x = (paddle_coords[0] + paddle_coords[2]) * 0.5
    self.ball = Ball(self.canvas, x, 310)
    self.paddle.set_ball(self.ball)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()
