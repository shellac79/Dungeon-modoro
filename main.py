import pygame
import sys
import random
import json
import os

# 1. 플레이어 데이터 클래스 
class Player:
    def __init__(self):
        self.max_hp = 100     
        self.current_hp = 100 
        self.atk = 10
        self.hp_level = 0
        self.atk_level = 0
        self.resource = 0
        self.temp_resource = 0

    def get_success_rate(self, level):
        if level >= 30:
            return 0.0
        return 1.0 - (level / 29.0) * 0.9

# 2. 보스 몬스터 클래스
class Boss:
    def __init__(self, stage):
        self.max_hp = 50 + (stage * 50) 
        self.current_hp = self.max_hp
        self.atk = 5 + (stage * 3)      

# 💾 [추가 기능] 데이터 저장 함수
def save_game(player, stage):
    data = {
        "max_hp": player.max_hp,
        "atk": player.atk,
        "hp_level": player.hp_level,
        "atk_level": player.atk_level,
        "resource": player.resource,
        "stage": stage
    }
    with open("save_data.json", "w") as f:
        json.dump(data, f)
    print("💾 자동 저장 완료!")

# 💾 [추가 기능] 데이터 불러오기 함수
def load_game(player):
    if os.path.exists("save_data.json"):
        with open("save_data.json", "r") as f:
            data = json.load(f)
            player.max_hp = data.get("max_hp", 100)
            player.atk = data.get("atk", 10)
            player.hp_level = data.get("hp_level", 0)
            player.atk_level = data.get("atk_level", 0)
            player.resource = data.get("resource", 0)
            player.current_hp = player.max_hp
            print("💾 저장된 데이터를 불러왔습니다!")
            return data.get("stage", 1)
    return 1 # 세이브 파일이 없으면 1스테이지부터 시작

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("던전모도로 - 집중의 시간")
    clock = pygame.time.Clock()

    player = Player()
    
    # 💡 게임 시작 시 자동으로 데이터 불러오기
    stage = load_game(player)
    
    font = pygame.font.SysFont("malgun gothic", 36)
    small_font = pygame.font.SysFont("malgun gothic", 24)
    title_font = pygame.font.SysFont("malgun gothic", 60, bold=True)
    
    current_state = "MENU"
    time_left = 1500 
    
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    BATTLE_EVENT = pygame.USEREVENT + 1
    
    boss = None
    battle_log = []
    turn = "PLAYER"
    battle_status = "ONGOING" 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 💡 끌 때도 무조건 한 번 저장!
                save_game(player, stage)
                pygame.quit()
                sys.exit()

            # --- PHASE 0: 시작 메뉴 화면 (마을) ---
            if current_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        time_left = 1500
                        current_state = "TIMER"
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
            
            # --- PHASE 1: 탐험 (타이머) ---
            elif current_state == "TIMER":
                if event.type == pygame.WINDOWFOCUSLOST:
                    player.temp_resource = 0
                    print("🚨 딴짓 감지! 임시 자원이 소멸되었습니다.")
                
                if event.type == pygame.USEREVENT:
                    if time_left > 0:
                        time_left -= 1
                        if time_left % 10 == 0:
                            player.temp_resource += 10 
                    else:
                        player.resource += player.temp_resource
                        player.temp_resource = 0
                        current_state = "MENU"
                        save_game(player, stage) # 💾 마을 복귀 시 자동 저장

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        time_left = 0

            # --- PHASE 2: 대장간 ---
            elif current_state == "UPGRADE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1 and player.resource >= 1:
                        if player.hp_level < 30:
                            player.resource -= 1
                            if random.random() < player.get_success_rate(player.hp_level):
                                player.max_hp += 20
                                player.hp_level += 1
                    
                    elif event.key == pygame.K_2 and player.resource >= 1:
                        if player.atk_level < 30:
                            player.resource -= 1
                            if random.random() < player.get_success_rate(player.atk_level):
                                player.atk += 5
                                player.atk_level += 1

                    elif event.key == pygame.K_RETURN:
                        current_state = "MENU"
                        save_game(player, stage) # 💾 마을 복귀 시 자동 저장

            # --- PHASE 3: 보스전 ---
            elif current_state == "BATTLE":
                if event.type == BATTLE_EVENT and battle_status == "ONGOING":
                    if turn == "PLAYER":
                        boss.current_hp -= player.atk
                        battle_log.append(f"▶ 플레이어의 공격! 보스에게 {player.atk} 피해.")
                        if boss.current_hp <= 0:
                            battle_log.append("🏆 보스 처치! (스페이스바: 메뉴로 복귀)")
                            battle_status = "VICTORY"
                            pygame.time.set_timer(BATTLE_EVENT, 0) 
                        else:
                            turn = "BOSS" 
                            
                    elif turn == "BOSS":
                        player.current_hp -= boss.atk
                        battle_log.append(f"▷ 보스의 공격! 플레이어에게 {boss.atk} 피해.")
                        if player.current_hp <= 0:
                            battle_log.append("💀 사망... (스페이스바: 스탯 초기화 후 메뉴로 복귀)")
                            battle_status = "DEFEAT"
                            pygame.time.set_timer(BATTLE_EVENT, 0)
                        else:
                            turn = "PLAYER"
                            
                    if len(battle_log) > 5:
                        battle_log.pop(0)

                if event.type == pygame.KEYDOWN and battle_status != "ONGOING":
                    if event.key == pygame.K_SPACE:
                        if battle_status == "VICTORY":
                            stage += 1
                        elif battle_status == "DEFEAT":
                            player = Player() # 패배 시 초기화 (혹은 자원만 유지하게 바꿀 수도 있음!)
                            stage = 1
                        current_state = "MENU"
                        save_game(player, stage) # 💾 마을 복귀 시 자동 저장


        # --- 화면 그리기 렌더링 파트 ---
        screen.fill((40, 40, 40))

        if current_state == "MENU":
            game_title = title_font.render("던전모도로", True, (255, 215, 0))
            sub_title = font.render(f"- 집중의 시간 | 현재 스테이지: {stage} -", True, (200, 200, 200))
            
            menu1 = font.render("[1] 탐험 시작 (25분 집중 파밍)", True, (100, 255, 100))
            menu2 = font.render(f"[2] 대장간 입장 (보유 자원: {player.resource})", True, (100, 200, 255))
            menu3 = font.render("[3] 보스전 도전! (준비 완료 시)", True, (255, 100, 100))
            
            screen.blit(game_title, (250, 80))
            screen.blit(sub_title, (180, 160))
            screen.blit(menu1, (150, 300))
            screen.blit(menu2, (150, 370))
            screen.blit(menu3, (150, 440))

        elif current_state == "TIMER":
            minutes = time_left // 60
            seconds = time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"

            warning_text = font.render("경고: 창을 벗어나면 임시 자원이 소멸됩니다!", True, (255, 100, 100))
            title_text = font.render("[탐험 중] - 집중해서 자원을 모으세요!", True, (255, 255, 255))
            timer_text = font.render(f"남은 시간: {time_str} (스페이스바: 0초 스킵)", True, (100, 255, 100))
            info_text = font.render(f"확정 자원: {player.resource} | 임시 자원: {player.temp_resource}", True, (255, 215, 0))
            
            screen.blit(warning_text, (50, 20))
            screen.blit(title_text, (50, 70))
            screen.blit(timer_text, (50, 120))
            screen.blit(info_text, (50, 170))

        elif current_state == "UPGRADE":
            hp_prob = player.get_success_rate(player.hp_level) * 100
            atk_prob = player.get_success_rate(player.atk_level) * 100

            title_text = font.render(f"[대장간] - 보유 자원: {player.resource}", True, (255, 215, 0))
            stat_text = font.render(f"HP: {player.max_hp} (Lv.{player.hp_level}) | ATK: {player.atk} (Lv.{player.atk_level})", True, (100, 200, 255))
            
            hp_guide_str = "MAX LEVEL" if player.hp_level >= 30 else f"성공률 {hp_prob:.1f}%"
            atk_guide_str = "MAX LEVEL" if player.atk_level >= 30 else f"성공률 {atk_prob:.1f}%"

            guide1 = small_font.render(f"숫자키 [1]: 체력 +20 강화 (비용 1, {hp_guide_str})", True, (200, 200, 200))
            guide2 = small_font.render(f"숫자키 [2]: 공격력 +5 강화 (비용 1, {atk_guide_str})", True, (200, 200, 200))
            guide_next = small_font.render("Enter키 누르기: 메뉴로 돌아가기", True, (255, 100, 100))

            screen.blit(title_text, (50, 50))
            screen.blit(stat_text, (50, 120))
            screen.blit(guide1, (50, 220))
            screen.blit(guide2, (50, 270))
            screen.blit(guide_next, (50, 370))

        elif current_state == "BATTLE":
            title_text = font.render(f"[보스전 - 스테이지 {stage}]", True, (255, 50, 50))
            
            p_stat = font.render(f"플레이어 HP: {player.current_hp} / {player.max_hp}", True, (100, 200, 255))
            b_stat = font.render(f"보스 HP: {boss.current_hp} / {boss.max_hp}", True, (255, 100, 100))
            
            screen.blit(title_text, (50, 50))
            screen.blit(p_stat, (50, 120))
            screen.blit(b_stat, (400, 120))

            log_start_y = 220
            for i, log in enumerate(battle_log):
                color = (255, 215, 0) if i == len(battle_log) - 1 else (200, 200, 200)
                log_text = small_font.render(log, True, color)
                screen.blit(log_text, (50, log_start_y + (i * 35)))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()