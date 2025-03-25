from ursina import *

app = Ursina()

# Player setup
player = Entity(model='cube', color=color.orange, scale=(0.5, 1, 0.5), position=(0, 1, 0))
player.collider = 'box'
player.velocity = Vec3(0, 0, 0)
player.on_ground = False
player.speed = 5

# Ground
ground = Entity(model='plane', scale=(100, 1, 100), color=color.gray, position=(0, 0, 0))
ground.collider = 'box'

# Levels
levels = [
    [(i * 3, 1, 0) for i in range(10)],  # Level 1
    [(0, 1, 0), (3, 1, 0), (7, 2, 0), (12, 1, 0), (16, 3, 0), (21, 1, 0)]  # Level 2
]
current_level = 0
blocks = []

def load_level(level_index):
    global blocks
    for block in blocks:
        destroy(block)
    blocks.clear()
    for pos in levels[level_index]:
        block = Entity(model='cube', scale=(2, 1, 2), position=pos, color=color.green)
        block.collider = 'box'
        blocks.append(block)

# Game state
game_time = 0
level_active = False
timer_text = Text(text="Time: 0.0", position=(-0.8, 0.4), scale=2)
level_text = Text(text="Level 1", position=(-0.8, 0.45), scale=2)

def reset_player():
    player.position = (0, 1, 0)
    player.velocity = Vec3(0, 0, 0)
    player.speed = 5

def start_level():
    global game_time, level_active
    game_time = 0
    level_active = True
    reset_player()
    load_level(current_level)
    level_text.text = f"Level {current_level + 1}"

# Camera
camera.position = (0, 10, -20)
camera.rotation_x = 30

def update():
    global game_time, level_active, current_level

    # Movement
    move_speed = player.speed
    player.velocity.x = held_keys['d'] * move_speed - held_keys['a'] * move_speed
    player.velocity.z = held_keys['w'] * move_speed - held_keys['s'] * move_speed
    player.velocity.y += -9.8 * time.dt

    # Ground check
    ray = raycast(player.position, direction=(0, -1, 0), distance=1.5, ignore=(player,))
    if ray.hit:
        player.on_ground = True
        player.velocity.y = 0
        player.y = ray.world_point.y + 0.5
    else:
        player.on_ground = False

    # Jumping and bunny hopping
    if held_keys['space'] and player.on_ground:
        player.velocity.y = 5
        player.speed = min(player.speed + 0.2, 10)
    if not player.on_ground:
        player.velocity.x *= 0.95
        player.velocity.z *= 0.95

    player.position += player.velocity * time.dt

    # Respawn
    if player.y < -10:
        reset_player()

    # Timer and level progression
    if level_active:
        game_time += time.dt
        timer_text.text = f"Time: {game_time:.1f}"
        last_block = blocks[-1]
        if distance_xz(player, last_block) < 1 and abs(player.y - last_block.y) < 2:
            level_active = False
            if current_level < len(levels) - 1:
                current_level += 1
                invoke(start_level, delay=1)
            else:
                timer_text.text += "\nGame Complete!"

start_level()
app.run()