import pygame
import sys
import random
import json
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_sound("click", "click.wav")       
        self.load_sound("hit", "hit.wav")           
        self.load_sound("upgrade", "upgrade.wav")   
        self.load_sound("error", "error.wav")       

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

class Player:
    def __init__(self):
        self.max_hp = 100     
        self.current_hp = 100 
        self.atk = 10
        self.hp_level = 0
        self.atk_level = 0
        self.ores = [0, 0, 0] 
        self.temp_ores = [0, 0, 0] 
        self.combo = 0 # 💡 [신규] 연전 콤보 횟수!

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
        "max_hp": player.max_hp, "current_hp": player.current_hp, "atk": player.atk,
        "hp_level": player.hp_level, "atk_level": player.atk_level,
        "ores": player.ores, "stage": stage, "combo": player.combo
    }
    with open("save_data.json", "w") as f:
        json.dump(data, f)

def load_game(player):
    if os.path.exists("save_data.json"):
        with open("save_data.json", "r") as f:
            data = json.load(f)
            player.max_hp = data.get("max_hp", 100)
            player.current_hp = data.get("current_hp", player.max_hp) # 💡 체력도 저장/불러오기
            player.atk = data.get("atk", 10)
            player.hp_level = data.get("hp_level", 0)
            player.atk_level = data.get("atk_level", 0)
            player.ores = data.get("ores", [0, 0, 0])
            player.combo = data.get("combo", 0)
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
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        sm.play("click") 
                    
                    if event.key == pygame.K_1:
                        current_state = "SELECT_DUNGEON" 
                    elif event.key == pygame.K_2:
                        current_state = "UPGRADE"
                    elif event.key == pygame.K_3:
                        current_state = "BATTLE"
                        # 💡 [삭제됨] 보스전에 들어가도 더 이상 체력이 자동 회복되지 않음!
                        boss = Boss(stage)
                        battle_log = [f"--- 스테이지 {stage} 보스전 시작! ---"]
                        turn = "PLAYER"
                        battle_status = "ONGOING"
                        pygame.time.set_timer(BATTLE_EVENT, 1000)
                    elif event.key == pygame.K_4:
                        current_state = "CONFIRM_RESET"

            elif current_state == "CONFIRM_RESET":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        player = Player() 
                        stage = 1
                        save_game(player, stage)
                        sm.play("upgrade") 
                        current_state = "MENU"
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        sm.play("click")
                        current_state = "MENU"

            # --- 던전 선택 화면 ---
            elif current_state == "SELECT_DUNGEON":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_ESCAPE, pygame.K_RETURN]:
                        sm.play("click")
                        
                    if event.key == pygame.K_1:
                        time_left = 1500 
                        dungeon_type = 1
                        current_state = "TIMER"
                    elif event.key == pygame.K_2:
                        time_left = 3000 
                        dungeon_type = 2
                        current_state = "TIMER"
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        player.combo = 0 # 💡 던전 입장을 포기하면 콤보 초기화
                        current_state = "MENU" 
            
            # --- 타이머 (탐험) 화면 ---
            elif current_state == "TIMER":
                if event.type == pygame.WINDOWFOCUSLOST:
                    if sum(player.temp_ores) > 0:
                        sm.play("error") 
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
                        # 💡 [수정] 0초가 되면 메뉴로 튕기지 않고 대기 상태로 전환
                        sm.play("upgrade")
                        current_state = "EXPLORATION_DONE"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        sm.play("upgrade")
                        current_state = "EXPLORATION_DONE" # 테스트용 스킵

            # --- 💡 [신규] 탐험 완료 대기 화면 ---
            elif current_state == "EXPLORATION_DONE":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    sm.play("click")
                    # 💡 콤보 보너스 계산 및 최종 획득
                    bonus_mult = 1.0 + (player.combo * 0.1)
                    for i in range(3):
                        earned = int(player.temp_ores[i] * bonus_mult)
                        player.ores[i] += earned
                    player.temp_ores = [0, 0, 0]
                    
                    time_left = 300 # 5분 휴식 타이머 세팅
                    current_state = "INN_TIMER"

            # --- 💡 [신규] 여관(휴식) 타이머 화면 ---
            elif current_state == "INN_TIMER":
                if event.type == pygame.USEREVENT:
                    if time_left > 0:
                        time_left -= 1
                        # 💡 1초마다 체력을 조금씩 회복 (5분 동안 풀피가 되도록 설계)
                        heal_amount = max(1, player.max_hp // 300)
                        if player.current_hp < player.max_hp:
                            player.current_hp = min(player.max_hp, player.current_hp + heal_amount)
                    else:
                        sm.play("upgrade")
                        current_state = "INN_CHOICE"

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    sm.play("click")
                    player.current_hp = player.max_hp # 스킵하면 즉시 풀피
                    current_state = "INN_CHOICE"

            # --- 💡 [신규] 여관 휴식 종료 후 선택 화면 ---
            elif current_state == "INN_CHOICE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        sm.play("click")
                        player.combo += 1 # 콤보 증가!
                        current_state = "SELECT_DUNGEON" # 바로 다음 던전 선택으로 이동
                    elif event.key == pygame.K_2:
                        sm.play("click")
                        player.combo = 0 # 마을로 가면 콤보 끊김
                        save_game(player, stage)
                        current_state = "MENU"

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
                                # 업글 시 현재 체력도 비율에 맞게 올려주기
                                player.current_hp += 20 
                                sm.play("upgrade") 
                            else:
                                sm.play("hit") 
                        else:
                            sm.play("error") 
                    
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
                            else:
                                sm.play("hit") 
                        else:
                            sm.play("error") 

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
                        sm.play("hit") 
                        
                        if boss.current_hp <= 0:
                            battle_log.append("🏆 보스 처치! (스페이스바: 메뉴로 복귀)")
                            battle_status = "VICTORY"
                            sm.play("upgrade") 
                            pygame.time.set_timer(BATTLE_EVENT, 0) 
                        else:
                            turn = "BOSS" 
                            
                    elif turn == "BOSS":
                        player.current_hp -= boss.atk
                        battle_log.append(f"▷ 보스의 공격! 플레이어에게 {boss.atk} 피해.")
                        sm.play("hit") 
                        
                        if player.current_hp <= 0:
                            battle_log.append("💀 사망... (스페이스바: 스탯 리셋 후 메뉴 복귀)")
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
            
            draw_panel(screen, 130, 170, 540, 390, border_color=(100, 150, 200))
            
            menu1 = font.render("[1] 던전 입장 (탐험 지역 선택)", True, (150, 255, 150))
            menu2 = font.render("[2] 대장간 입장", True, (150, 200, 255))
            inventory = small_font.render(f"보유 광물: [{ore_str}]", True, (255, 215, 0))
            
            # 💡 [신규] 체력은 휴식으로만 찹니다!
            hp_info = small_font.render(f"현재 체력: {player.current_hp}/{player.max_hp} (휴식으로만 회복!)", True, (255, 100, 100))
            
            menu3 = font.render("[3] 보스전 도전", True, (255, 150, 150))
            menu4 = font.render("[4] 데이터 초기화 (새로 시작)", True, (150, 150, 150))
            
            screen.blit(menu1, (180, 190))
            screen.blit(menu2, (180, 250))
            screen.blit(inventory, (220, 290)) 
            screen.blit(hp_info, (220, 320))
            screen.blit(menu3, (180, 390))
            screen.blit(menu4, (180, 460))

        elif current_state == "CONFIRM_RESET":
            draw_panel(screen, 150, 200, 500, 220, border_color=(255, 50, 50))
            
            warn_title = title_font.render("⚠️ 경고", True, (255, 100, 100))
            warn_text1 = small_font.render("모든 데이터(광물, 스탯, 진행도)가 영구히 삭제됩니다.", True, (200, 200, 200))
            warn_text2 = font.render("정말 처음부터 다시 시작하시겠습니까?", True, (255, 255, 255))
            
            guide_y = font.render("[Y] 예 (지우기)", True, (255, 100, 100))
            guide_n = font.render("[N] 아니오 (돌아가기)", True, (100, 255, 100))

            screen.blit(warn_title, (320, 220))
            screen.blit(warn_text1, (165, 280))
            screen.blit(warn_text2, (190, 320))
            screen.blit(guide_y, (180, 380))
            screen.blit(guide_n, (380, 380))

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

            # 💡 연전 시 콤보 문구 출력
            combo_txt = f"(연전 콤보 x{player.combo})" if player.combo > 0 else ""
            title_text = title_font.render(f"[{dungeon_name}] 탐험 중... {combo_txt}", True, (255, 255, 255))
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

        # 💡 [신규 UI] 탐험 완료 대기 
        elif current_state == "EXPLORATION_DONE":
            draw_panel(screen, 150, 150, 500, 300, border_color=(255, 215, 0))
            done_title = title_font.render("🎉 탐험 완료!", True, (255, 215, 0))
            
            bonus_rate = int(player.combo * 10)
            bonus_text = font.render(f"현재 획득 예정 자원 (콤보 보너스 +{bonus_rate}%)", True, (200, 255, 200))
            ore_text = font.render(f"[{temp_ore_str}]", True, (255, 255, 255))
            
            done_desc = small_font.render("▶ 스페이스바를 눌러 여관으로 이동 (5분 휴식)", True, (150, 150, 150))
            
            screen.blit(done_title, (280, 180))
            screen.blit(bonus_text, (190, 250))
            screen.blit(ore_text, (190, 290))
            screen.blit(done_desc, (190, 380))

        # 💡 [신규 UI] 여관 휴식 중 (체력 회복 묘사)
        elif current_state == "INN_TIMER":
            draw_panel(screen, 150, 150, 500, 300, border_color=(100, 255, 100))
            minutes = time_left // 60
            seconds = time_left % 60
            inn_title = title_font.render("☕ 여관에서 휴식 중", True, (255, 255, 255))
            time_render = title_font.render(f"⏳ {minutes:02d}:{seconds:02d}", True, (100, 255, 100))
            
            hp_text = small_font.render(f"체력 회복 중... {player.current_hp}/{player.max_hp}", True, (255, 150, 150))
            
            screen.blit(inn_title, (230, 180))
            screen.blit(time_render, (330, 250))
            screen.blit(hp_text, (260, 320))
            draw_hp_bar(screen, 250, 350, 300, 20, player.current_hp, player.max_hp)

            skip_hint = small_font.render("[Space] 휴식 0초 스킵", True, (100, 100, 100))
            screen.blit(skip_hint, (530, 420))

        # 💡 [신규 UI] 휴식 종료 후 선택
        elif current_state == "INN_CHOICE":
            draw_panel(screen, 100, 180, 600, 260, border_color=(200, 200, 255))
            choice_title = title_font.render("휴식 완료!", True, (200, 200, 255))
            
            next_bonus = int((player.combo + 1) * 10)
            c1 = font.render(f"[1] 연전 돌입! (다음 던전 자원 보너스 +{next_bonus}%)", True, (255, 215, 0))
            c2 = font.render("[2] 마을로 돌아가기 (콤보 초기화 및 저장)", True, (150, 150, 150))
            
            screen.blit(choice_title, (310, 210))
            screen.blit(c1, (130, 290))
            screen.blit(c2, (130, 360))

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