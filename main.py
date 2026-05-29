import pygame
import sys
import random
import json
import os

# 🎵 [신규] 사운드 매니저 클래스 (파일이 없어도 에러 안 나게 안전 처리!)
class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        # 사용할 효과음 이름과 파일명 매칭
        self.load_sound("click", "click.wav")       # 메뉴 이동, 버튼 클릭
        self.load_sound("hit", "hit.wav")           # 전투 타격음
        self.load_sound("upgrade", "upgrade.wav")   # 강화 성공
        self.load_sound("error", "error.wav")       # 자원 부족 등 에러음

    def load_sound(self, name, filename):
        if os.path.exists(filename):
            self.sounds[name] = pygame.mixer.Sound(filename)
        else:
            self.sounds[name] = None # 파일이 없으면 None으로 안전하게 보관

    def play(self, name):
        if name in self.sounds and self.sounds[name] is not None:
            self.sounds[name].play()

class Player:
    def __init__(self):
        self.max_hp = 100     
        self.current_hp = 100 
        self.atk = 10
        self.hp_level = 0
        self.atk_level = 0
        self.ores = [0, 0, 0] 
        self.temp_ores = [0, 0, 0] 

    def get_success_rate(self, level):
        if level >= 30:
            return 0.0
        return 1.0 - (level / 29.0) * 0.9

class Boss:
    def __init__(self, stage):
        self.max_hp = 50 + (stage * 50) 
        self.current_hp = self.max_hp
        self.atk = 5 + (stage * 3)      

def save_game(player, stage):
    data = {
        "max_hp": player.max_hp, "atk": player.atk,
        "hp_level": player.hp_level, "atk_level": player.atk_level,
        "ores": player.ores, "stage": stage
    }
    with open("save_data.json", "w") as f:
        json.dump(data, f)

def load_game(player):
    if os.path.exists("save_data.json"):
        with open("save_data.json", "r") as f:
            data = json.load(f)
            player.max_hp = data.get("max_hp", 100)
            player.atk = data.get("atk", 10)
            player.hp_level = data.get("hp_level", 0)
            player.atk_level = data.get("atk_level", 0)
            player.ores = data.get("ores", [0, 0, 0])
            player.current_hp = player.max_hp
            return data.get("stage", 1)
    return 1 

def draw_panel(screen, x, y, w, h, border_color=(100, 100, 100)):
    pygame.draw.rect(screen, (25, 25, 30), (x, y, w, h), border_radius=8)
    pygame.draw.rect(screen, border_color, (x, y, w, h), 3, border_radius=8)

def draw_hp_bar(screen, x, y, w, h, current_hp, max_hp):
    ratio = max(current_hp / max_hp, 0)
    pygame.draw.rect(screen, (80, 20, 20), (x, y, w, h)) 
    pygame.draw.rect(screen, (40, 180, 40), (x, y, int(w * ratio), h)) 
    pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h), 2) 

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("던전모도로 - 집중의 시간")
    clock = pygame.time.Clock()

    # 🎵 사운드 매니저 가동!
    sm = SoundManager()

    player = Player()
    stage = load_game(player)
    
    font = pygame.font.SysFont("malgun gothic", 26)
    small_font = pygame.font.SysFont("malgun gothic", 20)
    title_font = pygame.font.SysFont("malgun gothic", 46, bold=True)
    
    current_state = "MENU"
    time_left = 0 
    dungeon_type = 1 
    
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    BATTLE_EVENT = pygame.USEREVENT + 1
    
    boss = None
    battle_log = []
    turn = "PLAYER"
    battle_status = "ONGOING" 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(player, stage)
                pygame.quit()
                sys.exit()

            # --- 메뉴 화면 ---
            if current_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        sm.play("click") # 🎵 메뉴 이동 소리
                    
                    if event.key == pygame.K_1:
                        current_state = "SELECT_DUNGEON" 
                    elif event.key == pygame.K_2:
                        current_state = "UPGRADE"
                    elif event.key == pygame.K_3:
                        current_state = "BATTLE"
                        player.current_hp = player.max_hp
                        boss = Boss(stage)
                        battle_log = [f"--- 스테이지 {stage} 보스전 시작! ---"]
                        turn = "PLAYER"
                        battle_status = "ONGOING"
                        pygame.time.set_timer(BATTLE_EVENT, 1000)

            # --- 던전 선택 화면 ---
            elif current_state == "SELECT_DUNGEON":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_ESCAPE, pygame.K_RETURN]:
                        sm.play("click") # 🎵 클릭 소리
                        
                    if event.key == pygame.K_1:
                        time_left = 1500 
                        dungeon_type = 1
                        current_state = "TIMER"
                    elif event.key == pygame.K_2:
                        time_left = 3000 
                        dungeon_type = 2
                        current_state = "TIMER"
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        current_state = "MENU" 
            
            # --- 타이머 (탐험) 화면 ---
            elif current_state == "TIMER":
                if event.type == pygame.WINDOWFOCUSLOST:
                    if sum(player.temp_ores) > 0:
                        sm.play("error") # 🎵 딴짓해서 광물 날아갈 때 에러 소리!
                    player.temp_ores = [0, 0, 0] 
                
                if event.type == pygame.USEREVENT:
                    if time_left > 0:
                        time_left -= 1
                        if time_left % 10 == 0:
                            for _ in range(5):
                                roll = random.randint(1, 100)
                                if dungeon_type == 1:
                                    if roll <= 60: player.temp_ores[0] += 1 
                                    elif roll <= 90: player.temp_ores[1] += 1 
                                    else: player.temp_ores[2] += 1 
                                elif dungeon_type == 2:
                                    if roll <= 45: player.temp_ores[0] += 1 
                                    elif roll <= 80: player.temp_ores[1] += 1 
                                    else: player.temp_ores[2] += 1 
                    else:
                        for i in range(3):
                            player.ores[i] += player.temp_ores[i]
                        player.temp_ores = [0, 0, 0]
                        current_state = "MENU"
                        save_game(player, stage)
                        sm.play("upgrade") # 🎵 탐험 무사 완료 시 빰빠밤 소리!

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        sm.play("click")
                        time_left = 0

            # --- 대장간 화면 ---
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
                                sm.play("upgrade") # 🎵 강화 성공!
                            else:
                                sm.play("hit") # 🎵 강화 실패 깡!
                        else:
                            sm.play("error") # 🎵 자원 부족
                    
                    elif event.key == pygame.K_2 and player.atk_level < 30:
                        reqs = get_upgrade_req(player.atk_level)
                        if player.ores[0] >= reqs[0] and player.ores[1] >= reqs[1] and player.ores[2] >= reqs[2]:
                            player.ores[0] -= reqs[0]
                            player.ores[1] -= reqs[1]
                            player.ores[2] -= reqs[2]
                            if random.random() < player.get_success_rate(player.atk_level):
                                player.atk += 5
                                player.atk_level += 1
                                sm.play("upgrade") # 🎵 강화 성공!
                            else:
                                sm.play("hit") # 🎵 강화 실패 깡!
                        else:
                            sm.play("error") # 🎵 자원 부족

                    elif event.key == pygame.K_RETURN:
                        sm.play("click")
                        current_state = "MENU"
                        save_game(player, stage)

            # --- 보스전 화면 ---
            elif current_state == "BATTLE":
                if event.type == BATTLE_EVENT and battle_status == "ONGOING":
                    if turn == "PLAYER":
                        boss.current_hp -= player.atk
                        battle_log.append(f"▶ 플레이어의 공격! 보스에게 {player.atk} 피해.")
                        sm.play("hit") # 🎵 플레이어 공격 소리
                        
                        if boss.current_hp <= 0:
                            battle_log.append("🏆 보스 처치! (스페이스바: 메뉴로 복귀)")
                            battle_status = "VICTORY"
                            sm.play("upgrade") # 🎵 승리 팡파레!
                            pygame.time.set_timer(BATTLE_EVENT, 0) 
                        else:
                            turn = "BOSS" 
                            
                    elif turn == "BOSS":
                        player.current_hp -= boss.atk
                        battle_log.append(f"▷ 보스의 공격! 플레이어에게 {boss.atk} 피해.")
                        sm.play("hit") # 🎵 보스 공격 소리
                        
                        if player.current_hp <= 0:
                            battle_log.append("💀 사망... (스페이스바: 스탯 리셋 후 메뉴 복귀)")
                            battle_status = "DEFEAT"
                            sm.play("error") # 🎵 패배 소리
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
                        elif battle_status == "DEFEAT":
                            player = Player() 
                            stage = 1
                        current_state = "MENU"
                        save_game(player, stage)

        # --- 🎨 화면 렌더링 ---
        screen.fill((15, 15, 20)) 
        
        ore_str = f"철 {player.ores[0]} | 미스릴 {player.ores[1]} | 아다만 {player.ores[2]}"
        temp_ore_str = f"철 {player.temp_ores[0]} | 미스릴 {player.temp_ores[1]} | 아다만 {player.temp_ores[2]}"

        if current_state == "MENU":
            game_title = title_font.render("던전모도로", True, (220, 220, 220)) 
            sub_title = font.render(f"- 집중의 시간 | 스테이지 {stage} -", True, (150, 150, 150))
            screen.blit(game_title, (280, 60))
            screen.blit(sub_title, (230, 120))
            
            draw_panel(screen, 150, 200, 500, 320, border_color=(100, 150, 200))
            
            menu1 = font.render("[1] 던전 입장 (탐험 지역 선택)", True, (150, 255, 150))
            menu2 = font.render("[2] 대장간 입장", True, (150, 200, 255))
            inventory = small_font.render(f"보유 광물: [{ore_str}]", True, (255, 215, 0))
            menu3 = font.render("[3] 보스전 도전", True, (255, 150, 150))
            
            screen.blit(menu1, (200, 230))
            screen.blit(menu2, (200, 300))
            screen.blit(inventory, (240, 340)) 
            screen.blit(menu3, (200, 410))

        elif current_state == "SELECT_DUNGEON":
            game_title = title_font.render("목적지 선택", True, (150, 255, 150)) 
            sub_title = font.render("어디로 탐험을 떠나시겠습니까?", True, (150, 150, 150))
            screen.blit(game_title, (270, 60))
            screen.blit(sub_title, (220, 130))
            
            draw_panel(screen, 100, 200, 600, 320, border_color=(150, 255, 150))
            
            dun1_title = font.render("[1] 얕은 숲 (25분 집중)", True, (200, 255, 200))
            dun1_desc = small_font.render("기본적인 철광석 위주로 안전하게 파밍합니다.", True, (150, 150, 150))
            
            dun2_title = font.render("[2] 심연의 동굴 (50분 딥워크)", True, (255, 150, 255))
            dun2_desc = small_font.render("희귀한 미스릴과 아다만티움의 발견 확률이 증가합니다.", True, (200, 150, 200))
            
            cancel_txt = small_font.render("[Enter] 마을로 돌아가기", True, (150, 150, 150))
            
            screen.blit(dun1_title, (140, 230))
            screen.blit(dun1_desc, (170, 270))
            
            screen.blit(dun2_title, (140, 340))
            screen.blit(dun2_desc, (170, 380))
            
            screen.blit(cancel_txt, (500, 470))

        elif current_state == "TIMER":
            dungeon_name = "얕은 숲" if dungeon_type == 1 else "심연의 동굴"
            border_col = (100, 255, 100) if dungeon_type == 1 else (200, 100, 255)
            
            draw_panel(screen, 120, 120, 560, 350, border_color=border_col)
            
            minutes = time_left // 60
            seconds = time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"

            title_text = title_font.render(f"[{dungeon_name}] 탐험 중...", True, (255, 255, 255))
            timer_text = title_font.render(f"⏳ {time_str}", True, (100, 255, 100))
            
            info_text = small_font.render(f"창고: [{ore_str}]", True, (200, 200, 200))
            temp_text = font.render(f"가방(임시): [{temp_ore_str}]", True, (255, 215, 0))
            warning_text = small_font.render("경고: 창을 벗어나면 가방 안의 광물이 모두 증발합니다!", True, (255, 100, 100))
            
            screen.blit(title_text, (200, 150))
            screen.blit(timer_text, (310, 220))
            screen.blit(info_text, (180, 300))
            screen.blit(temp_text, (180, 340))
            screen.blit(warning_text, (160, 420))

            skip_hint = small_font.render("[Space] 0초 스킵 (테스트용)", True, (100, 100, 100))
            screen.blit(skip_hint, (550, 560))

        elif current_state == "UPGRADE":
            draw_panel(screen, 30, 50, 740, 140, border_color=(150, 200, 255))
            title_text = font.render(f"[ 대장간 ] 광물: {ore_str}", True, (255, 215, 0))
            stat_text = font.render(f"현재 스탯 ➡️ HP: {player.max_hp} (Lv.{player.hp_level}) | ATK: {player.atk} (Lv.{player.atk_level})", True, (200, 220, 255))
            screen.blit(title_text, (60, 75))
            screen.blit(stat_text, (60, 130))

            draw_panel(screen, 30, 220, 740, 320, border_color=(100, 100, 150))
            
            hp_req_str = req_to_string(get_upgrade_req(player.hp_level))
            atk_req_str = req_to_string(get_upgrade_req(player.atk_level))
            
            hp_prob = player.get_success_rate(player.hp_level) * 100
            atk_prob = player.get_success_rate(player.atk_level) * 100
            
            hp_guide_str = "MAX" if player.hp_level >= 30 else f"비용: [{hp_req_str}] | 확률 {hp_prob:.1f}%"
            atk_guide_str = "MAX" if player.atk_level >= 30 else f"비용: [{atk_req_str}] | 확률 {atk_prob:.1f}%"

            guide1 = font.render(f"숫자키 [1]: 체력 +20 강화 ({hp_guide_str})", True, (220, 220, 220))
            guide2 = font.render(f"숫자키 [2]: 공격력 +5 강화 ({atk_guide_str})", True, (220, 220, 220))
            guide_next = font.render("Enter키 누르기: 메뉴로 돌아가기", True, (255, 100, 100))

            screen.blit(guide1, (50, 270))
            screen.blit(guide2, (50, 350))
            screen.blit(guide_next, (50, 450))

        elif current_state == "BATTLE":
            draw_panel(screen, 40, 40, 340, 180, border_color=(100, 200, 255))
            p_title = font.render("플레이어", True, (100, 200, 255))
            p_stat = small_font.render(f"공격력: {player.atk}", True, (200, 200, 200))
            p_hp_text = small_font.render(f"HP {player.current_hp}/{player.max_hp}", True, (255, 255, 255))
            screen.blit(p_title, (60, 55))
            screen.blit(p_stat, (60, 95))
            screen.blit(p_hp_text, (60, 130))
            draw_hp_bar(screen, 60, 160, 300, 20, player.current_hp, player.max_hp)

            draw_panel(screen, 420, 40, 340, 180, border_color=(255, 100, 100))
            b_title = font.render(f"보스 (스테이지 {stage})", True, (255, 100, 100))
            b_stat = small_font.render(f"공격력: {boss.atk}", True, (200, 200, 200))
            b_hp_text = small_font.render(f"HP {boss.current_hp}/{boss.max_hp}", True, (255, 255, 255))
            screen.blit(b_title, (440, 55))
            screen.blit(b_stat, (440, 95))
            screen.blit(b_hp_text, (440, 130))
            draw_hp_bar(screen, 440, 160, 300, 20, boss.current_hp, boss.max_hp)

            draw_panel(screen, 40, 250, 720, 300, border_color=(150, 150, 150))
            log_start_y = 270
            for i, log in enumerate(battle_log):
                color = (255, 215, 0) if i == len(battle_log) - 1 else (180, 180, 180)
                log_text = font.render(log, True, color)
                screen.blit(log_text, (60, log_start_y + (i * 35)))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()