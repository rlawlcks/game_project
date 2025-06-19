from ursina import *
import time
import random

game = Ursina()

# 게임 효과 사운드
bgm = Audio('bgm.wav', loop=True, autoplay=False)
coin_sound = Audio("coin_sound.mp3", autoplay=False)
ending_sound = Audio("finish.mp3", autoplay=False)

# 게임 환경 설정
player = Entity(model="sphere", color=color.green, position=(0, 3, -400), scale=(5, 5, 5), collider="box")
camera.z = -15
camera.add_script(SmoothFollow(target=player, offset=(0, 5, -30)))
road = Entity(model="plane", scale=(100, 10, 30000), color=color.black)
rows = [-15, -10, -5, 0, 5, 10, 15] # 장애물이 랜덤하게 나타남
median_r = Entity(model='cube', collider='box', position=(25, 2, 0), scale=(5, 10, 30000), color=color.white)
median_l = Entity(model='cube', collider='box', position=(-25, 2, 0), scale=(5, 10, 30000), color=color.white)
score_board = Text(text="0", scale=5, x=-0.75, y=0.45)
speed = 200

# 전역 변수
enemies = []
coins = []
coin_score = 0
game_over = False
restart_text = None

# 장애물, 코인 생성 함수
def generate_enemies_and_coins():
    for i in range(0, 30000, 100):
        enemy = Entity(
            model='cube',
            collider='box',
            position=(random.choice(rows), 6, i),
            color=color.random_color(),
            scale=(10, 10, 10)
        )
        enemies.append(enemy)

    for i in range(0, 30000, 300):
        coin = Entity(
            model='sphere',
            color=color.yellow,
            position=(random.choice(rows), 3, i + 50),
            scale=2,
            collider='box'
        )
        coins.append(coin)

# 게임 종료
def show_game_over(final_score):
    global game_over, restart_text
    game_over = True
    bgm.stop()
    restart_text = Text(
        text=f"GAME OVER!\nFINAL SCORE: {final_score}pt\nPress Enter to restart",
        origin=(0, 0),
        scale=2,
        position=(0, 0),
        color=color.red,
        background=True
    )
    ending_sound.play() #게임이 종료가 되면 bgm도 중단됨

# 게임 재시작할 경우
def reset_game():
    global coin_score, game_over, restart_text
    player.position = Vec3(0, 3, -400)
    player.rotation = Vec3(0, 0, 0)
    score_board.text = "0"
    coin_score = 0
    game_over = False

    if restart_text:
        destroy(restart_text)

    for e in enemies:
        destroy(e)
    enemies.clear()

    for c in coins:
        destroy(c)
    coins.clear()

    generate_enemies_and_coins()
    bgm.play()

def update():
    global coin_score

    if game_over:
        if held_keys['enter']:
            reset_game()
        return

    player.z += time.dt * speed
    player.rotation_x += time.dt * 50

    if held_keys['d']:
        player.x += time.dt * 25
        player.rotation_z += time.dt * 60
    if held_keys['a']:
        player.x -= time.dt * 25
        player.rotation_z += time.dt * 100

    hit = player.intersects()
    if hit.hit and hit.entity not in coins:
        final_score = int(player.z + 400 + coin_score)
        show_game_over(final_score)
        return

    #코인을 먹으면 500점 추가
    for coin in coins[:]:
        if player.intersects(coin).hit:
            coin_score += 500
            coin_sound.play()
            destroy(coin)
            coins.remove(coin)

    # 사용자의 위치가 -400에서 시작하기 때문에 400을 더했음
    base_score = player.z + 400
    total_score = base_score + coin_score
    score_board.text = str(int(total_score))

generate_enemies_and_coins()
bgm.play()

# 배경
window.fullscreen = True
sky = Sky()
game.run()