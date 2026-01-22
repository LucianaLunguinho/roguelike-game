import pgzrun
from pgzero.actor import Actor
from random import randint

WIDTH = 1200
HEIGHT = 800

hero = Actor("hero_idle_0", pos=(WIDTH//2, HEIGHT//2))
hero_speed = 10
hero_health = 3
hero_points = 0
hero_invulnerable = False
hero_flash_timer = 0

hero_sprites = {
    'idle': ["hero_idle_0"],
    'walk': ["hero_walk_0", "hero_walk_1", "hero_walk_2", "hero_walk_3", "hero_walk_4", "hero_walk_5", "hero_walk_6"],
    'attack': ["hero_attack_0", "hero_attack_1","hero_attack_2","hero_attack_3","hero_attack_4","hero_attack_5"],
}

enemy_sprites = ["enemy_walk_0", "enemy_walk_1", "enemy_walk_2"]

hero_anim_timer = 0
hero_facing_right = True       
hero_current_frame_name = "hero_idle_0" 
hero_attack_timer = 0  
ATTACK_RANGE = 200     
ATTACK_COOLDOWN = 25  
MAX_ENEMIES = 3          
enemy_spawn_timer = 0   
SPAWN_DELAY = 60   
enemy_speed = 3         
enemies = []
enemy_speed = 1
game_state = "menu"
sound_on = True

buttons = {
    "start": Actor("button_start_resize", pos=(WIDTH//2, HEIGHT//2)),
    "sound": Actor("button_sound_resize", pos=(WIDTH//2 - 100, HEIGHT//2 + 150)),
    "exit": Actor("button_exit_resize", pos=(WIDTH//2 + 100, HEIGHT//2 + 150))
}

try:
    music.play("background")
    music.set_volume(0.1)
except Exception:
    print("Aviso: Música não encontrada.")

def get_spawn_point():
    corner = randint(0,1)
    corners = [-50,WIDTH+50]
    return corners[corner]

def spawn_enemy():
    global enemy_speed
    
    side = randint(0, 3)
    
    if side == 0:
        x = randint(0, WIDTH)
        y = -50 
    elif side == 1: 
        x = WIDTH + 50
        y = randint(0, HEIGHT)
    elif side == 2: 
        x = randint(0, WIDTH)
        y = HEIGHT + 50
    else: 
        x = -50
        y = randint(0, HEIGHT)

    enemy_type = "enemy_walk_0"
    enemy_speed *= 1.05
    new_enemy = Actor(enemy_type, pos=(x, y))
    new_enemy.anim_timer = 0
    new_enemy.current_frame = 0
    enemies.append(new_enemy)

def trigger_attack():
    global hero_attack_timer, enemy_speed, hero_points
    
    if hero_attack_timer == 0:
        hero_attack_timer = ATTACK_COOLDOWN 
        
        if sound_on: sounds.load("slash").play()
        for enemy in enemies[:]:
            if hero.distance_to(enemy) < ATTACK_RANGE:
                hero_points += 1
                enemies.remove(enemy)

def update_hero():
    global hero_anim_timer, hero_flash_timer, hero_facing_right, hero_current_frame_name, hero_attack_timer
    
    moving = False

    if hero_attack_timer > 0:
        hero_attack_timer -= 1
    
    if keyboard.left and hero.x > 0:
        hero.x -= hero_speed
        moving = True
        hero_facing_right = False
    elif keyboard.right and hero.x < WIDTH:
        hero.x += hero_speed
        moving = True
        hero_facing_right = True 
        
    if keyboard.up and hero.y > 0:
        hero.y -= hero_speed
        moving = True
    elif keyboard.down and hero.y < HEIGHT:
        hero.y += hero_speed
        moving = True

    if hero_attack_timer > 0:
        frames = hero_sprites['attack']
        num_frames = len(frames)
        ticks_per_frame = ATTACK_COOLDOWN / num_frames
        time_passed = ATTACK_COOLDOWN - hero_attack_timer
        frame_index = int(time_passed // ticks_per_frame)
        if frame_index >= num_frames:
            frame_index = num_frames - 1
            
        hero_current_frame_name = frames[frame_index]

    else:
        hero_anim_timer += 1
        if hero_anim_timer > 5:
            hero_anim_timer = 0
            tipo = 'walk' if moving else 'idle'
            frames = hero_sprites[tipo]

            if hero_current_frame_name not in frames:
                next_frame_name = frames[0]
            else:
                idx = frames.index(hero_current_frame_name)
                next_idx = (idx + 1) % len(frames)
                next_frame_name = frames[next_idx]
            
            hero_current_frame_name = next_frame_name

    if hero_facing_right:
        hero.image = hero_current_frame_name
    else:
        hero.image = hero_current_frame_name + "_left"
    if hero_invulnerable:
        hero_flash_timer += 1
    else:
        hero_flash_timer = 0

def update_enemies():
    global hero_health, hero_invulnerable, game_state

    for enemy in enemies:

        enemy.anim_timer += 1

        if enemy.anim_timer > 10:
            enemy.anim_timer = 0
            enemy.current_frame = (enemy.current_frame + 1) % len(enemy_sprites)

        current_image_name = enemy_sprites[enemy.current_frame]

        if enemy.x < hero.x: 
            enemy.x += enemy_speed
            enemy.image = current_image_name
        elif enemy.x > hero.x: 
            enemy.x -= enemy_speed
            enemy.image = current_image_name + "_left"
        if enemy.y < hero.y: enemy.y += enemy_speed
        elif enemy.y > hero.y: enemy.y -= enemy_speed

        if enemy.distance_to(hero) < 100 and not hero_invulnerable:
            hero_health -= 1
            if sound_on: 
               sounds.hit.play() 
            if hero_health <= 0:
                game_state = "game_over"
                music.stop()
            else:
                hero_invulnerable = True
                clock.schedule(end_invulnerability, 1.5)

def update_spawn():
    global enemy_spawn_timer
    
    if len(enemies) < MAX_ENEMIES:
        enemy_spawn_timer += 1
        if enemy_spawn_timer > SPAWN_DELAY:
            spawn_enemy()
            enemy_spawn_timer = 0 

def end_invulnerability():
    global hero_invulnerable
    hero_invulnerable = False

def update():
    if game_state == "playing":
        update_hero()
        update_enemies()
        update_spawn()

def draw():
    screen.blit("dungeon", (0, 0))
    
    if game_state == "menu":
        screen.draw.text("HERÓI NA MASMORRA", center=(WIDTH//2, HEIGHT//2 - 200), fontsize=70, color="white")
        for btn in buttons.values():
            btn.draw()

    elif game_state == "playing":

        should_draw_hero = True
        if hero_invulnerable and hero_flash_timer % 10 < 5:
                should_draw_hero = False
        if should_draw_hero:
            hero.draw()
        for enemy in enemies:
            enemy.draw()
            
        screen.draw.text(f"VIDA: {hero_health}", (10, 10), fontsize=30, color="red")
        screen.draw.text(f"PONTOS: {hero_points}", (130, 10), fontsize=30, color="yellow")

    elif game_state == "game_over":
        screen.fill((20, 0, 0))
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="red")
        screen.draw.text(f"Você conseguiu {hero_points} pontos!", center=(WIDTH//2, HEIGHT//2 - 200), fontsize=60, color="red")
        screen.draw.text("Espaço para Sair", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=30, color="white")
        if keyboard.space:
            quit()

def on_key_down(key):
    global game_state
    if game_state == "playing":
        if key == keys.SPACE:
            trigger_attack()         
    elif game_state == "game_over":
        if key == keys.SPACE:
            quit()

def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == "menu":
        if buttons["start"].collidepoint(pos):
            game_state = "playing"
        elif buttons["exit"].collidepoint(pos):
            quit()
        elif buttons["sound"].collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                try: music.play("background")
                except: pass
                buttons["sound"].alpha = 1.0
            else:
                music.stop()
                buttons["sound"].alpha = 0.5

pgzrun.go()