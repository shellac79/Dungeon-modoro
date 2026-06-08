import pygame
import sys
import random
import json
import os
import math

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_sound("click", "click.wav")       
        self.load_sound("hit", "hit.wav")           
        self.load_sound("upgrade", "upgrade.wav")   
        self.load_sound("error", "error.wav")       
        
        self.bgm_volume = 0.5  
        self.is_bgm_on = True  

    def load_sound(self, name, filename):
        if os.path.exists(filename):
            self.sounds[name] = pygame.mixer.Sound(filename)
        else:
            self.sounds[name] = None 

    def play(self, name, play_time=0):
        if name in self.sounds and self.sounds[name] is not None:
            if play_time > 0:
                self.sounds[name].play(maxtime=play_time)
            else:
                self.sounds[name].play()

    def play_bgm(self, filename):
        if os.path.exists(filename) and self.is_bgm_on:
            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(-1)
            except:
                pass
            
    def stop_bgm(self):
        pygame.mixer.music.stop()

    def toggle_bgm(self, current_bgm_file):
        self.is_bgm_on = not self.is_bgm_on
        if self.is_bgm_on and current_bgm_file:
            self.play_bgm(current_bgm_file)
        else:
            self.stop_bgm()

    def change_volume(self, delta):
        self.bgm_volume += delta
        self.bgm_volume = max(0.0, min(1.0, self.bgm_volume)) 
        pygame.mixer.music.set_volume(self.bgm_volume)

class Player:
    def __init__(self):
        self.max_hp = 100     
        self.current_hp = 100 
        self.atk = 10
        self.hp_level = 0
        self.atk_level = 0
        self.ores = [0, 0, 0] 
        self.temp_ores = [0, 0, 0] 
        self.combo = 0 
        
        self.total_ores_gained = [0, 0, 0]
        self.forest_successes = 0
        self.cave_successes = 0
        self.focus_lost_count = 0
        self.total_study_seconds = 0

    def get_success_rate(self, level):
        if level >= 30:
            return 0.0
        return 1.0 - (level / 29.0) * 0.9

class Boss:
    def __init__(self, stage):
        self.stage = stage
        self.max_hp = 50 + (stage * 50) 
        self.current_hp = self.max_hp
        self.atk = 5 + (stage * 3)
        
        boss_names = ["거대 맹독 슬라임", "단검 고블린 정찰병", "티모", "잔혹한 흡혈귀 뱀파이어", "지옥의 악마"]
        
        if stage <= len(boss_names):
            self.name = boss_names[stage - 1]
            self.img_name = f"boss{stage}.png"
        else:
            self.name = f"지옥의 악마 (Lv.{stage})"
            self.img_name = "boss5.png"

class FloatingText:
    def __init__(self, text, x, y, color, font):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font = font
        self.alpha = 255
        self.velocity = -2  
        
    def update(self):
        self.y += self.velocity
        self.alpha -= 5  
        
    def draw(self, surface):
        if self.alpha > 0:
            surf = self.font.render(self.text, True, self.color)
            surf.set_alpha(max(0, self.alpha))
            surface.blit(surf, (self.x, self.y))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-5, 5) 
        self.vy = random.uniform(-8, -2) 
        self.life = 255
        self.size = random.randint(3, 7)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4  
        self.life -= 8  
        
    def draw(self, surface):
        if self.life > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, max(0, self.life)), (self.size, self.size), self.size)
            surface.blit(surf, (self.x - self.size, self.y - self.size))

def save_game(player, stage):
    data = {
        "max_hp": player.max_hp, "current_hp": player.current_hp, "atk": player.atk,
        "hp_level": player.hp_level, "atk_level": player.atk_level,
        "ores": player.ores, "stage": stage, "combo": player.combo,
        "total_ores_gained": player.total_ores_gained,
        "forest_successes": player.forest_successes,
        "cave_successes": player.cave_successes,
        "focus_lost_count": player.focus_lost_count,
        "total_study_seconds": player.total_study_seconds
    }
    with open("save_data.json", "w") as f:
        json.dump(data, f)

def load_game(player):
    if os.path.exists("save_data.json"):
        with open("save_data.json", "r") as f:
            data = json.load(f)
            player.max_hp = data.get("max_hp", 100)
            player.current_hp = data.get("current_hp", player.max_hp) 
            player.atk = data.get("atk", 10)
            player.hp_level = data.get("hp_level", 0)
            player.atk_level = data.get("atk_level", 0)
            player.ores = data.get("ores", [0, 0, 0])
            player.combo = data.get("combo", 0)
            
            player.total_ores_gained = data.get("total_ores_gained", [0, 0, 0])
            player.forest_successes = data.get("forest_successes", 0)
            player.cave_successes = data.get("cave_successes", 0)
            player.focus_lost_count = data.get("focus_lost_count", 0)
            player.total_study_seconds = data.get("total_study_seconds", 0)
            
            return data.get("stage", 1)
    return 1 

def draw_panel(surface, x, y, w, h, border_color=(100, 100, 100)):
    pygame.draw.rect(surface, (25, 25, 30), (x, y, w, h), border_radius=8)
    pygame.draw.rect(surface, border_color, (x, y, w, h), 3, border_radius=8)

def draw_transparent_panel(surface, x, y, w, h, border_color=(100, 100, 100), alpha=160, border_width=2, radius=12):
    temp_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(temp_surf, (20, 20, 25, alpha), (0, 0, w, h), border_radius=radius)
    if border_width > 0:
        pygame.draw.rect(temp_surf, border_color, (0, 0, w, h), border_width, border_radius=radius)
    surface.blit(temp_surf, (x, y))

def draw_hp_bar(surface, x, y, w, h, current_hp, max_hp):
    ratio = max(current_hp / max_hp, 0)
    pygame.draw.rect(surface, (80, 20, 20), (x, y, w, h)) 
    pygame.draw.rect(surface, (40, 180, 40), (x, y, int(w * ratio), h)) 
    pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 2) 

def get_upgrade_req(level):
    req = [0, 0, 0] 
    if level < 10:
        req[0] = (level % 10) + 1 
    elif level < 20:
        req[0] = 5                
        req[1] = (level % 10) + 1 
    else:
        req[0] = 10               
        req[1] = 5                
        req[2] = (level % 10) + 1 
    return req

def req_to_string(req_list):
    res = []
    if req_list[0] > 0: res.append(f"철 {req_list[0]}")
    if req_list[1] > 0: res.append(f"미스릴 {req_list[1]}")
    if req_list[2] > 0: res.append(f"아다만 {req_list[2]}")
    return ", ".join(res)

def get_valid_font(size, bold=False):
    font_path = "font.ttf"
    if os.path.exists(font_path):
        try:
            return pygame.font.Font(font_path, size)
        except:
            pass
            
    available = pygame.font.get_fonts()
    ko_candidates = ["malgungothic", "nanumgothic", "gulim", "dotum"]
    for name in ko_candidates:
        if name in available:
            return pygame.font.SysFont(name, size, bold=bold)
            
    return pygame.font.SysFont(None, size, bold=bold)

def load_image(filename, size=None):
    if os.path.exists(filename):
        try:
            img = pygame.image.load(filename).convert_alpha()
            if size:
                return pygame.transform.scale(img, size)
            return img
        except:
            pass
    return None

def get_player_title(stage):
    if stage == 1: return "[초보 탐험가]"
    elif stage == 2: return "[슬라임 헌터]"
    elif stage == 3: return "[고블린 추적자]"
    elif stage == 4: return "[심연의 생존자]"
    elif stage == 5: return "[흡혈귀 슬레이어]"
    else: return "[지옥의 정복자]"

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    display_surf = pygame.Surface((800, 600))
    pygame.display.set_caption("던전모도로 - 집중의 시간")
    clock = pygame.time.Clock()

    sm = SoundManager()
    player = Player()
    stage = load_game(player)
    
    font = get_valid_font(24)
    small_font = get_valid_font(18)
    title_font = get_valid_font(48, bold=True)
    timer_font = get_valid_font(70, bold=True) 
    
    current_state = "MENU"
    time_left = 0 
    max_time = 1 
    dungeon_type = 1 
    current_bgm_file = "" 
    
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    BATTLE_EVENT = pygame.USEREVENT + 1
    
    boss = None
    battle_log = []
    turn = "PLAYER"
    battle_status = "ONGOING" 
    
    floating_texts = []
    particles = [] 
    shake_time = 0 
    
    fade_alpha = 0
    fade_dir = 0  
    next_state = ""
    fade_surface = pygame.Surface((800, 600))
    fade_surface.fill((0, 0, 0))

    player_img = load_image("player.png", (100, 100))
    bg_forest = load_image("bg_forest.png", (800, 600))
    bg_cave = load_image("bg_cave.png", (800, 600))
    bg_menu = load_image("bg_menu.png", (800, 600)) 
    boss_img = None

    def change_state_with_fade(new_state):
        nonlocal next_state, fade_dir
        next_state = new_state
        fade_dir = 1 

    def roll_mineral():
        if random.random() < 0.30:  
            roll = random.randint(1, 100)
            if dungeon_type == 1:
                if roll <= 60: player.temp_ores[0] += 1 
                elif roll <= 90: player.temp_ores[1] += 1 
                else: player.temp_ores[2] += 1 
            elif dungeon_type == 2:
                if roll <= 45: player.temp_ores[0] += 1 
                elif roll <= 80: player.temp_ores[1] += 1 
                else: player.temp_ores[2] += 1 
            
            rx = random.randint(350, 450)
            ry = random.randint(280, 320)
            floating_texts.append(FloatingText("광물 발견!", rx, ry, (255, 215, 0), small_font))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(player, stage)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and fade_dir != 0:
                continue

            if current_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                        sm.play("click") 
                    
                    if event.key == pygame.K_1:
                        change_state_with_fade("SELECT_DUNGEON") 
                    elif event.key == pygame.K_2:
                        change_state_with_fade("UPGRADE")
                    elif event.key == pygame.K_3:
                        boss = Boss(stage)
                        boss_img = load_image(boss.img_name, (100, 100))
                        battle_log = [f"--- {boss.name} 출현! ---"]
                        turn = "PLAYER"
                        battle_status = "ONGOING"
                        pygame.time.set_timer(BATTLE_EVENT, 1000)
                        change_state_with_fade("BATTLE")
                    elif event.key == pygame.K_4:
                        change_state_with_fade("CONFIRM_RESET")
                    elif event.key == pygame.K_5:
                        change_state_with_fade("STATISTICS")

            elif current_state == "STATISTICS":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                        sm.play("click")
                        change_state_with_fade("MENU")

            elif current_state == "CONFIRM_RESET":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        player = Player() 
                        stage = 1
                        save_game(player, stage)
                        sm.play("upgrade") 
                        change_state_with_fade("MENU")
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        sm.play("click")
                        change_state_with_fade("MENU")

            elif current_state == "SELECT_DUNGEON":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_ESCAPE, pygame.K_RETURN]:
                        sm.play("click")
                        
                    if event.key == pygame.K_1:
                        time_left = 1500 
                        max_time = 1500 
                        dungeon_type = 1
                        current_bgm_file = "bgm_forest.mp3"
                        sm.play_bgm(current_bgm_file) 
                        change_state_with_fade("TIMER")
                    elif event.key == pygame.K_2:
                        time_left = 3000 
                        max_time = 3000 
                        dungeon_type = 2
                        current_bgm_file = "bgm_cave.mp3"
                        sm.play_bgm(current_bgm_file)
                        change_state_with_fade("TIMER")
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        player.combo = 0 
                        change_state_with_fade("MENU") 
            
            elif current_state == "TIMER":
                if event.type == pygame.WINDOWFOCUSLOST:
                    if sum(player.temp_ores) > 0:
                        sm.play("error") 
                        # 💡 [팀원 A 구현] 딴짓 방지 페널티 강화 로직
                        shake_time = 15 # 화면을 더 세게 흔들리게!
                        player.focus_lost_count += 1
                        
                        penalty_dmg = 10 + (player.combo * 5) # 콤보 비례 기습 데미지 산출
                        player.current_hp = max(1, player.current_hp - penalty_dmg) # 체력 강제 감소
                        player.combo = 0 # 공들인 콤보 초기화 페널티
                        
                        floating_texts.append(FloatingText(f"딴짓 발각! 기습 페널티 (-{penalty_dmg} HP)", 200, 250, (255, 50, 50), title_font))
                        
                    player.temp_ores = [0, 0, 0] 
                
                if event.type == pygame.USEREVENT:
                    if time_left > 0:
                        time_left -= 1
                        player.total_study_seconds += 1
                        if time_left > 0 and time_left % 10 == 0:
                            roll_mineral()
                    else:
                        if dungeon_type == 1: player.forest_successes += 1 
                        elif dungeon_type == 2: player.cave_successes += 1
                        
                        # 💡 [팀원 B 구현] 던전 탐험을 무사히 완료하면 데이터 손실 방지를 위한 자동 저장
                        save_game(player, stage)
                        
                        sm.stop_bgm() 
                        sm.play("upgrade") 
                        change_state_with_fade("EXPLORATION_DONE")

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        sm.toggle_bgm(current_bgm_file)
                    elif event.key == pygame.K_UP:
                        sm.change_volume(0.1) 
                    elif event.key == pygame.K_DOWN:
                        sm.change_volume(-0.1) 
                    elif event.key == pygame.K_SPACE:
                        remaining_intervals = time_left // 10
                        for _ in range(remaining_intervals):
                            roll_mineral()
                        player.total_study_seconds += time_left 
                        time_left = 0
                        if dungeon_type == 1: player.forest_successes += 1 
                        elif dungeon_type == 2: player.cave_successes += 1
                        
                        # 💡 [팀원 B 구현] 스킵으로 성공 처리되었을 때도 자동 저장 적용
                        save_game(player, stage)
                        
                        sm.stop_bgm()
                        sm.play("upgrade")
                        change_state_with_fade("EXPLORATION_DONE") 

            elif current_state == "EXPLORATION_DONE":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    sm.play("click")
                    bonus_mult = 1.0 + (player.combo * 0.1)
                    for i in range(3):
                        earned = int(player.temp_ores[i] * bonus_mult)
                        player.ores[i] += earned
                        player.total_ores_gained[i] += earned 
                    player.temp_ores = [0, 0, 0]
                    time_left = 300 if dungeon_type == 1 else 600 
                    change_state_with_fade("INN_TIMER")

            elif current_state == "INN_TIMER":
                if event.type == pygame.USEREVENT:
                    if time_left > 0:
                        time_left -= 1
                        heal_amount = max(1, player.max_hp // 300)
                        if player.current_hp < player.max_hp:
                            player.current_hp = min(player.max_hp, player.current_hp + heal_amount)
                            rx = random.randint(350, 450)
                            ry = random.randint(280, 310)
                            floating_texts.append(FloatingText(f"+{heal_amount}", rx, ry, (50, 255, 50), title_font))
                    else:
                        sm.play("upgrade")
                        change_state_with_fade("INN_CHOICE")

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    sm.play("click")
                    player.current_hp = player.max_hp 
                    change_state_with_fade("INN_CHOICE")

            elif current_state == "INN_CHOICE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        sm.play("click")
                        player.combo += 1 
                        change_state_with_fade("SELECT_DUNGEON") 
                    elif event.key == pygame.K_2:
                        sm.play("click")
                        player.combo = 0 
                        save_game(player, stage)
                        change_state_with_fade("MENU")

            elif current_state == "UPGRADE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1 and player.hp_level < 30:
                        reqs = get_upgrade_req(player.hp_level)
                        if player.ores[0] >= reqs[0] and player.ores[1] >= reqs[1] and player.ores[2] >= reqs[2]:
                            player.ores[0] -= reqs[0]
                            player.ores[1] -= reqs[1]
                            player.ores[2] -= reqs[2]
                            if random.random() < player.get_success_rate(player.hp_level):
                                player.max_hp += 20
                                player.hp_level += 1
                                player.current_hp += 20 
                                sm.play("upgrade")
                                for _ in range(40):
                                    particles.append(Particle(400, 150, random.choice([(255, 215, 0), (200, 255, 200), (255, 255, 255)])))
                            else:
                                sm.play("hit") 
                                shake_time = 12 
                        else:
                            sm.play("error") 
                            shake_time = 8
                    
                    elif event.key == pygame.K_2 and player.atk_level < 30:
                        reqs = get_upgrade_req(player.atk_level)
                        if player.ores[0] >= reqs[0] and player.ores[1] >= reqs[1] and player.ores[2] >= reqs[2]:
                            player.ores[0] -= reqs[0]
                            player.ores[1] -= reqs[1]
                            player.ores[2] -= reqs[2]
                            if random.random() < player.get_success_rate(player.atk_level):
                                player.atk += 5
                                player.atk_level += 1
                                sm.play("upgrade") 
                                for _ in range(40):
                                    particles.append(Particle(400, 150, random.choice([(255, 215, 0), (200, 255, 200), (255, 255, 255)])))
                            else:
                                sm.play("hit") 
                                shake_time = 12
                        else:
                            sm.play("error") 
                            shake_time = 8

                    elif event.key == pygame.K_RETURN:
                        sm.play("click")
                        save_game(player, stage)
                        change_state_with_fade("MENU")

            elif current_state == "BATTLE":
                if event.type == BATTLE_EVENT and battle_status == "ONGOING":
                    if turn == "PLAYER":
                        damage = player.atk
                        boss.current_hp -= damage
                        battle_log.append(f"[공격] 플레이어의 공격! 보스에게 {damage} 피해.")
                        sm.play("hit") 
                        rx = random.randint(450, 530)
                        ry = random.randint(30, 60)
                        floating_texts.append(FloatingText(f"-{damage}", rx, ry, (255, 50, 50), title_font))
                        if boss.current_hp <= 0:
                            battle_log.append(f"[승리] {boss.name} 처치! (스페이스바: 메뉴로 복귀)")
                            battle_status = "VICTORY"
                            sm.play("upgrade") 
                            pygame.time.set_timer(BATTLE_EVENT, 0) 
                        else:
                            turn = "BOSS" 
                    elif turn == "BOSS":
                        damage = boss.atk
                        player.current_hp -= damage
                        battle_log.append(f"[피격] {boss.name}의 공격! 플레이어에게 {damage} 피해.")
                        sm.play("hit") 
                        shake_time = 8 
                        rx = random.randint(70, 150)
                        ry = random.randint(30, 60)
                        floating_texts.append(FloatingText(f"-{damage}", rx, ry, (255, 50, 50), title_font))
                        if player.current_hp <= 0:
                            player.current_hp = 0  
                            battle_log.append("[패배] 전투에서 졌습니다... (스페이스바: 후퇴)") 
                            battle_status = "DEFEAT"
                            sm.play("error") 
                            pygame.time.set_timer(BATTLE_EVENT, 0)
                        else:
                            turn = "PLAYER"
                    if len(battle_log) > 6:
                        battle_log.pop(0)

                if event.type == pygame.KEYDOWN and battle_status != "ONGOING":
                    if event.key == pygame.K_SPACE:
                        sm.play("click")
                        if battle_status == "VICTORY":
                            stage += 1
                        save_game(player, stage)
                        change_state_with_fade("MENU")

        display_surf.fill((15, 15, 20)) 
        
        ore_str = f"철 {player.ores[0]} | 미스릴 {player.ores[1]} | 아다만 {player.ores[2]}"
        temp_ore_str = f"철 {player.temp_ores[0]} | 미스릴 {player.temp_ores[1]} | 아다만 {player.temp_ores[2]}"

        if current_state == "MENU":
            if bg_menu:
                display_surf.blit(bg_menu, (0, 0))
            
            title_text = title_font.render("던전모도로", True, (240, 240, 255))
            title_rect = title_text.get_rect(center=(400, 70))
            display_surf.blit(title_text, title_rect)
            
            sub_title = font.render(f"현재 위치: 스테이지 {stage}", True, (200, 200, 220))
            sub_rect = sub_title.get_rect(center=(400, 120))
            display_surf.blit(sub_title, sub_rect)
            
            pygame.draw.polygon(display_surf, (150, 100, 255), [(400, 150), (395, 155), (400, 160), (405, 155)])

            panel_x, panel_y = 140, 180
            panel_w, panel_h = 520, 380
            draw_transparent_panel(display_surf, panel_x, panel_y, panel_w, panel_h, border_color=(100, 80, 150), alpha=210)
            
            menu1 = font.render("[1] 던전 입장 (탐험 지역 선택)", True, (150, 255, 150)) 
            menu2 = font.render("[2] 대장간 입장", True, (150, 200, 255)) 
            inventory = small_font.render(f"보유 광물: [{ore_str}]", True, (255, 215, 0)) 
            hp_info = small_font.render(f"현재 체력: {player.current_hp}/{player.max_hp} (휴식으로만 회복)", True, (255, 100, 100)) 
            menu3 = font.render("[3] 보스전 도전", True, (255, 150, 150)) 
            menu4 = font.render("[4] 데이터 초기화 (새로 시작)", True, (140, 140, 140)) 
            menu5 = font.render("[5] 나의 집중 통계 확인", True, (255, 200, 150)) 
            
            display_surf.blit(menu1, (panel_x + 60, panel_y + 40))
            display_surf.blit(menu2, (panel_x + 60, panel_y + 100))
            display_surf.blit(inventory, (panel_x + 90, panel_y + 135)) 
            display_surf.blit(hp_info, (panel_x + 90, panel_y + 160))   
            display_surf.blit(menu3, (panel_x + 60, panel_y + 200))
            display_surf.blit(menu4, (panel_x + 60, panel_y + 260))
            display_surf.blit(menu5, (panel_x + 60, panel_y + 320))

        elif current_state == "STATISTICS":
            stat_title = title_font.render("나의 집중 통계", True, (150, 255, 150))
            stat_subtitle = font.render("위대한 여정의 기록", True, (150, 150, 150))
            display_surf.blit(stat_title, (280, 50))
            display_surf.blit(stat_subtitle, (310, 110))
            
            draw_panel(display_surf, 80, 160, 640, 350, border_color=(150, 200, 150))
            
            study_mins = player.total_study_seconds // 60
            stat_time = font.render(f"누적 집중 시간: {study_mins} 분", True, (200, 200, 200))
            stat_forest = font.render(f"고요한 숲 성공 횟수: {player.forest_successes} 회", True, (200, 200, 200))
            stat_cave = font.render(f"심연의 동굴 성공 횟수: {player.cave_successes} 회", True, (200, 200, 200))
            stat_lost = font.render(f"집중 이탈(딴짓) 횟수: {player.focus_lost_count} 회", True, (255, 150, 150))
            
            total_ores_sum = sum(player.total_ores_gained)
            stat_ores1 = font.render(f"누적 획득 보상: 총 {total_ores_sum} 개", True, (255, 215, 0))
            ores_detail = f"(철 {player.total_ores_gained[0]} | 미스릴 {player.total_ores_gained[1]} | 아다만 {player.total_ores_gained[2]})"
            stat_ores2 = small_font.render(ores_detail, True, (180, 180, 180))
            
            display_surf.blit(stat_time, (120, 200))
            display_surf.blit(stat_forest, (120, 250))
            display_surf.blit(stat_cave, (120, 300))
            display_surf.blit(stat_lost, (120, 350))
            display_surf.blit(stat_ores1, (120, 410))
            display_surf.blit(stat_ores2, (120, 440))
            
            guide_next = small_font.render("[Space] 또는 [Enter] 메뉴로 돌아가기", True, (100, 255, 100))
            display_surf.blit(guide_next, (250, 540))

        elif current_state == "CONFIRM_RESET":
            draw_panel(display_surf, 80, 200, 640, 220, border_color=(255, 50, 50))
            warn_title = title_font.render("경고", True, (255, 100, 100))
            warn_text1 = small_font.render("모든 데이터(광물, 스탯, 진행도)가 영구히 삭제됩니다.", True, (200, 200, 200))
            warn_text2 = font.render("정말 처음부터 다시 시작하시겠습니까?", True, (255, 255, 255))
            guide_y = font.render("[Y] 예 (지우기)", True, (255, 100, 100))
            guide_n = font.render("[N] 아니오 (돌아가기)", True, (100, 255, 100))
            display_surf.blit(warn_title, (360, 215))
            display_surf.blit(warn_text1, (140, 275))
            display_surf.blit(warn_text2, (170, 315))
            display_surf.blit(guide_y, (180, 370))
            display_surf.blit(guide_n, (440, 370))

        elif current_state == "SELECT_DUNGEON":
            game_title = title_font.render("목적지 선택", True, (150, 255, 150)) 
            sub_title = font.render("어디로 탐험을 떠나시겠습니까?", True, (150, 150, 150))
            display_surf.blit(game_title, (300, 50))
            display_surf.blit(sub_title, (250, 120))
            draw_panel(display_surf, 40, 180, 720, 350, border_color=(150, 255, 150))
            
            dun1_title = font.render("[1] 고요한 숲 (25분 집중)", True, (200, 255, 200))
            dun1_prob = small_font.render("- 10초당 30% 확률 획득 (철 60% | 미스릴 30% | 아다만 10%)", True, (150, 200, 150))
            
            dun2_title = font.render("[2] 심연의 동굴 (50분 딥워크)", True, (255, 150, 255))
            dun2_prob = small_font.render("- 10초당 30% 확률 획득 (철 45% | 미스릴 35% | 아다만 20%)", True, (200, 150, 200))
            
            cancel_txt = small_font.render("[Enter] 마을로 돌아가기", True, (150, 150, 150))
            
            display_surf.blit(dun1_title, (70, 210))
            display_surf.blit(dun1_prob, (100, 250))
            display_surf.blit(dun2_title, (70, 340))
            display_surf.blit(dun2_prob, (100, 380))
            display_surf.blit(cancel_txt, (550, 480))

        elif current_state == "TIMER":
            dungeon_name = "고요한 숲" if dungeon_type == 1 else "심연의 동굴"
            if dungeon_type == 1 and bg_forest:
                display_surf.blit(bg_forest, (0, 0))
            elif dungeon_type == 2 and bg_cave:
                display_surf.blit(bg_cave, (0, 0))
                
            draw_transparent_panel(display_surf, 40, 40, 720, 520, border_color=(0,0,0), alpha=160, border_width=0)
            
            minutes = time_left // 60
            seconds = time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            combo_txt = f"(연전 콤보 x{player.combo})" if player.combo > 0 else ""
            
            title_text = title_font.render(f"[{dungeon_name}] 탐험 중... {combo_txt}", True, (255, 255, 255))
            timer_text = timer_font.render(time_str, True, (100, 255, 100)) 
            
            temp_text = font.render(f"가방(임시): [{temp_ore_str}]", True, (255, 215, 0))
            warning_text = small_font.render("주의: 창을 벗어나면 캔 광물이 모두 증발합니다!", True, (255, 100, 100))
            bg_status = small_font.render(f"BGM 단축키: [M] ON/OFF  |  볼륨 [↑/↓] ({int(sm.bgm_volume * 100)}%)", True, (150, 200, 255))
            skip_hint = font.render("[Space] 스킵", True, (180, 180, 180))

            display_surf.blit(title_text, (60, 60))
            display_surf.blit(timer_text, (330, 160)) 
            display_surf.blit(temp_text, (60, 430))
            display_surf.blit(warning_text, (60, 470))
            display_surf.blit(bg_status, (60, 510))
            display_surf.blit(skip_hint, (620, 510))

            path_start_x = 120
            path_end_x = 680
            path_y = 350
            
            progress = 1.0 - (time_left / max(1, max_time))
            current_x = path_start_x + (path_end_x - path_start_x) * progress
            
            pygame.draw.line(display_surf, (80, 80, 90), (path_start_x, path_y), (path_end_x, path_y), 6)
            pygame.draw.line(display_surf, (150, 255, 150), (path_start_x, path_y), (current_x, path_y), 6)
            pygame.draw.circle(display_surf, (255, 215, 0), (path_end_x, path_y), 8)

            bounce_y = math.sin(pygame.time.get_ticks() / 150.0) * 5
            if player_img:
                display_surf.blit(player_img, (current_x - 30, path_y - 70 + bounce_y))

            for ft in floating_texts[:]:
                ft.update()
                ft.draw(display_surf)
                if ft.alpha <= 0:
                    floating_texts.remove(ft)

        elif current_state == "EXPLORATION_DONE":
            draw_panel(display_surf, 40, 140, 720, 350, border_color=(255, 215, 0))
            done_title = title_font.render("탐험 완료!", True, (255, 215, 0))
            bonus_rate = int(player.combo * 10)
            bonus_text = font.render(f"현재 획득 예정 자원 (콤보 보너스 +{bonus_rate}%)", True, (200, 255, 200))
            ore_text = font.render(f"[{temp_ore_str}]", True, (255, 255, 255))
            rest_min = 5 if dungeon_type == 1 else 10
            done_desc = font.render(f"- 스페이스바를 눌러 여관으로 이동 ({rest_min}분 휴식)", True, (160, 160, 255))
            display_surf.blit(done_title, (300, 170))
            display_surf.blit(bonus_text, (80, 240))
            display_surf.blit(ore_text, (80, 280))
            display_surf.blit(done_desc, (80, 380)) 

        elif current_state == "INN_TIMER":
            draw_panel(display_surf, 40, 140, 720, 350, border_color=(100, 255, 100))
            minutes = time_left // 60
            seconds = time_left % 60
            inn_title = title_font.render("여관에서 휴식 중", True, (255, 255, 255))
            time_render = title_font.render(f"{minutes:02d}:{seconds:02d}", True, (100, 255, 100))
            hp_text = small_font.render(f"체력 회복 중... {player.current_hp}/{player.max_hp}", True, (255, 150, 150))
            display_surf.blit(inn_title, (270, 170))
            display_surf.blit(time_render, (350, 240))
            display_surf.blit(hp_text, (70, 315))
            draw_hp_bar(display_surf, 70, 345, 660, 20, player.current_hp, player.max_hp)
            skip_hint = small_font.render("[Space] 휴식 스킵 (즉시 완회)", True, (100, 100, 100))
            display_surf.blit(skip_hint, (610, 420))
            
            for ft in floating_texts[:]:
                ft.update()
                ft.draw(display_surf)
                if ft.alpha <= 0: floating_texts.remove(ft)

        elif current_state == "INN_CHOICE":
            draw_panel(display_surf, 40, 170, 720, 280, border_color=(200, 200, 255))
            choice_title = title_font.render("휴식 완료!", True, (200, 200, 200))
            next_bonus = int((player.combo + 1) * 10)
            c1 = font.render(f"[1] 연전 돌입! (다음 던전 자원 보너스 +{next_bonus}%)", True, (255, 215, 0))
            c2 = font.render("[2] 마을로 돌아가기 (콤보 초기화 및 저장)", True, (160, 160, 160))
            display_surf.blit(choice_title, (320, 200))
            display_surf.blit(c1, (80, 280))
            display_surf.blit(c2, (80, 350))

        elif current_state == "UPGRADE":
            draw_panel(display_surf, 30, 40, 740, 150, border_color=(150, 200, 255))
            title_text = font.render(f"[ 대장간 ] 광물: {ore_str}", True, (255, 215, 0))
            stat_text = font.render(f"현재 스탯 -> HP: {player.max_hp} (Lv.{player.hp_level}) | ATK: {player.atk} (Lv.{player.atk_level})", True, (200, 220, 255))
            display_surf.blit(title_text, (50, 65))
            display_surf.blit(stat_text, (50, 120))
            draw_panel(display_surf, 30, 220, 740, 320, border_color=(100, 100, 150))
            hp_req_str = req_to_string(get_upgrade_req(player.hp_level))
            atk_req_str = req_to_string(get_upgrade_req(player.atk_level))
            hp_prob = player.get_success_rate(player.hp_level) * 100
            atk_prob = player.get_success_rate(player.atk_level) * 100
            hp_guide_str = "MAX" if player.hp_level >= 30 else f"비용: [{hp_req_str}] | 확률 {hp_prob:.1f}%"
            atk_guide_str = "MAX" if player.atk_level >= 30 else f"비용: [{atk_req_str}] | 확률 {atk_prob:.1f}%"
            guide1 = font.render(f"숫자키 [1]: 체력 +20 강화 ({hp_guide_str})", True, (220, 220, 220))
            guide2 = font.render(f"숫자키 [2]: 공격력 +5 강화 ({atk_guide_str})", True, (220, 220, 220))
            guide_next = font.render("Enter키 누르기: 메뉴로 돌아가기", True, (255, 100, 100))
            display_surf.blit(guide1, (50, 260))
            display_surf.blit(guide2, (50, 340))
            display_surf.blit(guide_next, (50, 450))
            
            for p in particles[:]:
                p.update()
                p.draw(display_surf)
                if p.life <= 0: particles.remove(p)

        elif current_state == "BATTLE":
            # 💡 [팀원 C 구현] 보스전 패널 UI 반투명 스타일(알파 180) 일괄 적용
            draw_transparent_panel(display_surf, 40, 40, 350, 200, border_color=(100, 200, 255), alpha=180)
            if player_img: display_surf.blit(player_img, (60, 60))
            else: pygame.draw.rect(display_surf, (100, 200, 255), (60, 60, 100, 100), 2) 
            p_title = font.render(f"플레이어 {get_player_title(stage)}", True, (100, 200, 255))
            p_stat = small_font.render(f"공격력: {player.atk}", True, (200, 200, 200))
            p_hp_text = small_font.render(f"HP {player.current_hp}/{player.max_hp}", True, (255, 255, 255))
            display_surf.blit(p_title, (180, 60))
            display_surf.blit(p_stat, (180, 100))
            display_surf.blit(p_hp_text, (180, 135))
            draw_hp_bar(display_surf, 60, 180, 310, 20, player.current_hp, player.max_hp)
            
            draw_transparent_panel(display_surf, 410, 40, 350, 200, border_color=(255, 100, 100), alpha=180)
            if boss_img: display_surf.blit(boss_img, (430, 60))
            else: pygame.draw.rect(display_surf, (255, 100, 100), (430, 60, 100, 100), 2)
            b_title = font.render(f"{boss.name}", True, (255, 100, 100))
            b_stat = small_font.render(f"공격력: {boss.atk}", True, (200, 200, 200))
            b_hp_text = small_font.render(f"HP {boss.current_hp}/{boss.max_hp}", True, (255, 255, 255))
            display_surf.blit(b_title, (550, 60))
            display_surf.blit(b_stat, (550, 100))
            display_surf.blit(b_hp_text, (550, 135))
            draw_hp_bar(display_surf, 430, 180, 310, 20, boss.current_hp, boss.max_hp)
            
            draw_transparent_panel(display_surf, 40, 260, 720, 290, border_color=(150, 150, 150), alpha=180)
            log_start_y = 280
            for i, log in enumerate(battle_log):
                color = (255, 215, 0) if i == len(battle_log) - 1 else (180, 180, 180)
                log_text = font.render(log, True, color)
                display_surf.blit(log_text, (60, log_start_y + (i * 35)))

            for ft in floating_texts[:]:
                ft.update()
                ft.draw(display_surf)
                if ft.alpha <= 0: floating_texts.remove(ft)

        if fade_dir == 1:
            fade_alpha += 25  
            if fade_alpha >= 255:
                fade_alpha = 255
                current_state = next_state
                fade_dir = -1
        elif fade_dir == -1:
            fade_alpha -= 25
            if fade_alpha <= 0:
                fade_alpha = 0
                fade_dir = 0
        if fade_alpha > 0:
            fade_surface.set_alpha(fade_alpha)
            display_surf.blit(fade_surface, (0, 0))

        shake_x, shake_y = 0, 0
        if shake_time > 0:
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)
            shake_time -= 1
        screen.fill((0, 0, 0)) 
        screen.blit(display_surf, (shake_x, shake_y))
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
