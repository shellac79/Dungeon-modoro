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

# 💾 데이터 저장/불러오기 함수
def save_game(player, stage):
    data = {
        "max_hp": player.max_hp, "atk": player.atk,
        "hp_level": player.hp_level, "atk_level": player.atk_level,
        "resource": player.resource, "stage": stage
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
            player.resource = data.get("resource", 0)
            player.current_hp = player.max_hp
            return data.get("stage", 1)
    return 1 

# 🎨 [UI] 패널(상자) 그리기
def draw_panel(screen, x, y, w, h, border_color=(100, 100, 100)):
    pygame.draw.rect(screen, (25, 25, 30), (x, y, w, h), border_radius=8)
    pygame.draw.rect(screen, border_color, (x, y, w, h), 3, border_radius=8)

# 🎨 [UI] 체력 바(HP Bar) 그리기
def draw_hp_bar(screen, x, y, w, h, current_hp, max_hp):
    ratio = max(current_hp / max_hp, 0)
    pygame.draw.rect(screen, (80, 20, 20), (x, y, w, h)) 
    pygame.draw.rect(screen, (40, 180, 40), (x, y, int(w * ratio), h)) 
    pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h), 2) 

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("던전모도로 - 집중의 시간")
    clock = pygame.time.Clock()

    player = Player()
    stage = load_game(player)
    
    font = pygame.font.SysFont("malgun gothic", 26)
    small_font = pygame.font.SysFont("malgun gothic", 20)
    title_font = pygame.font.SysFont("malgun gothic", 46, bold=True)
    
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
                save_game(player, stage)
                pygame.quit()
                sys.exit()

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
            
            elif current_state == "TIMER":
                if event.type == pygame.WINDOWFOCUSLOST:
                    player.temp_resource = 0
                
                if event.type == pygame.USEREVENT:
                    if time_left > 0:
                        time_left -= 1
                        if time_left % 10 == 0:
                            player.temp_resource += 10 
                    else:
                        player.resource += player.temp_resource
                        player.temp_resource = 0
                        current_state = "MENU"
                        save_game(player, stage)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        time_left = 0

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
                        save_game(player, stage)

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
                            battle_log.append("💀 사망... (스페이스바: 메뉴로 복귀)")
                            battle_status = "DEFEAT"
                            pygame.time.set_timer(BATTLE_EVENT, 0)
                        else:
                            turn = "PLAYER"
                            
                    if len(battle_log) > 6:
                        battle_log.pop(0)

                if event.type == pygame.KEYDOWN and battle_status != "ONGOING":
                    if event.key == pygame.K_SPACE:
                        if battle_status == "VICTORY":
                            stage += 1
                        elif battle_status == "DEFEAT":
                            player = Player() 
                            stage = 1
                        current_state = "MENU"
                        save_game(player, stage)


        # --- 🎨 화면 렌더링 ---
        screen.fill((15, 15, 20)) 

        if current_state == "MENU":
            game_title = title_font.render("던전모도로", True, (220, 220, 220)) 
            sub_title = font.render(f"- 집중의 시간 | 스테이지 {stage} -", True, (150, 150, 150))
            
            screen.blit(game_title, (280, 60))
            screen.blit(sub_title, (230, 120))
            
            draw_panel(screen, 150, 200, 500, 320, border_color=(100, 150, 200))
            
            menu1 = font.render("[1] 탐험 시작 (25분 집중 파밍)", True, (150, 255, 150))
            menu2 = font.render(f"[2] 대장간 입장 (보유 자원: {player.resource})", True, (150, 200, 255))
            menu3 = font.render("[3] 보스전 도전", True, (255, 150, 150))
            
            screen.blit(menu1, (200, 250))
            screen.blit(menu2, (200, 330))
            screen.blit(menu3, (200, 410))

        elif current_state == "TIMER":
            draw_panel(screen, 120, 120, 560, 350, border_color=(100, 255, 100))
            
            minutes = time_left // 60
            seconds = time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"

            title_text = title_font.render(f"스테이지 {stage} 탐험 중", True, (255, 255, 255))
            timer_text = title_font.render(f"⏳ {time_str}", True, (100, 255, 100))
            info_text = font.render(f"확정 자원: {player.resource}  |  임시 자원: {player.temp_resource}", True, (255, 215, 0))
            warning_text = small_font.render("경고: 창을 벗어나면 임시 자원이 소멸됩니다!", True, (255, 100, 100))
            
            screen.blit(title_text, (220, 160))
            screen.blit(timer_text, (310, 240))
            screen.blit(info_text, (200, 330))
            screen.blit(warning_text, (200, 410))

            # 💡 [추가] 오른쪽 아래 스페이스바 스킵 힌트 (어두운 색으로 은은하게)
            skip_hint = small_font.render("[Space] 0초 스킵 (테스트용)", True, (100, 100, 100))
            screen.blit(skip_hint, (550, 560))

        elif current_state == "UPGRADE":
            draw_panel(screen, 50, 50, 700, 140, border_color=(150, 200, 255))
            title_text = font.render(f"[ 대장간 ]   보유 자원: {player.resource}", True, (255, 215, 0))
            stat_text = font.render(f"현재 스탯 ➡️ HP: {player.max_hp} (Lv.{player.hp_level}) | ATK: {player.atk} (Lv.{player.atk_level})", True, (200, 220, 255))
            screen.blit(title_text, (80, 75))
            screen.blit(stat_text, (80, 130))

            draw_panel(screen, 50, 220, 700, 320, border_color=(100, 100, 150))
            hp_prob = player.get_success_rate(player.hp_level) * 100
            atk_prob = player.get_success_rate(player.atk_level) * 100
            hp_guide_str = "MAX" if player.hp_level >= 30 else f"확률 {hp_prob:.1f}%"
            atk_guide_str = "MAX" if player.atk_level >= 30 else f"확률 {atk_prob:.1f}%"

            guide1 = font.render(f"숫자키 [1]: 체력 +20 강화 (비용 1, {hp_guide_str})", True, (220, 220, 220))
            guide2 = font.render(f"숫자키 [2]: 공격력 +5 강화 (비용 1, {atk_guide_str})", True, (220, 220, 220))
            guide_next = font.render("Enter키 누르기: 메뉴로 돌아가기", True, (255, 100, 100))

            screen.blit(guide1, (80, 270))
            screen.blit(guide2, (80, 350))
            screen.blit(guide_next, (80, 450))

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