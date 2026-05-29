import pygame
import sys
import random

# 1. 플레이어 데이터 클래스 (전투용 체력 분리)
class Player:
    def __init__(self):
        self.max_hp = 100     # 최대 체력 (강화로 올라가는 수치)
        self.current_hp = 100 # 전투 중에 깎이는 실제 체력
        self.atk = 10
        self.hp_level = 0
        self.atk_level = 0
        self.resource = 0
        self.temp_resource = 0

    def get_success_rate(self, level):
        if level >= 30:
            return 0.0
        return 1.0 - (level / 29.0) * 0.9

# 2. 보스 몬스터 클래스 (스테이지 비례 스탯업 적용)
class Boss:
    def __init__(self, stage):
        self.max_hp = 50 + (stage * 50) # 스테이지마다 체력 50 증가
        self.current_hp = self.max_hp
        self.atk = 5 + (stage * 3)      # 스테이지마다 공격력 3 증가

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("던전모도로 - 집중의 시간")
    clock = pygame.time.Clock()

    player = Player()
    
    font = pygame.font.SysFont("malgun gothic", 36)
    small_font = pygame.font.SysFont("malgun gothic", 24)
    
    current_state = "TIMER"
    time_left = 1500 # 25분
    
    # ⏰ 기본 1초 타이머 (자원 파밍용)
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    
    # ⚔️ 전투 자동 진행용 타이머 (1초마다 턴 진행)
    BATTLE_EVENT = pygame.USEREVENT + 1
    
    # 게임 상태 및 전투 관련 변수들
    stage = 1
    boss = None
    battle_log = []
    turn = "PLAYER"
    battle_status = "ONGOING" # ONGOING(진행 중), VICTORY(승리), DEFEAT(패배)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # --- PHASE 1: 타이머 (집중과 파밍) ---
            if current_state == "TIMER":
                if event.type == pygame.WINDOWFOCUSLOST:
                    player.temp_resource = 0
                    print("🚨 딴짓 감지! 임시 자원이 모두 소멸되었습니다.")
                
                if event.type == pygame.USEREVENT:
                    if time_left > 0:
                        time_left -= 1
                        if time_left % 10 == 0:
                            player.temp_resource += 10 # 💡 테스트용 버프 (10개씩)
                    else:
                        player.resource += player.temp_resource
                        player.temp_resource = 0
                        current_state = "UPGRADE"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        time_left = 0

            # --- PHASE 2: 대장간 (확률형 스탯 강화) ---
            elif current_state == "UPGRADE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1 and player.resource >= 1:
                        if player.hp_level < 30:
                            player.resource -= 1
                            prob = player.get_success_rate(player.hp_level)
                            if random.random() < prob:
                                player.max_hp += 20
                                player.hp_level += 1
                                print(f"✨ 체력 강화 성공! (현재 Lv.{player.hp_level})")
                            else:
                                print("💥 체력 강화 실패...")
                    
                    elif event.key == pygame.K_2 and player.resource >= 1:
                        if player.atk_level < 30:
                            player.resource -= 1
                            prob = player.get_success_rate(player.atk_level)
                            if random.random() < prob:
                                player.atk += 5
                                player.atk_level += 1
                                print(f"✨ 공격력 강화 성공! (현재 Lv.{player.atk_level})")
                            else:
                                print("💥 공격력 강화 실패...")

                    # 엔터 키: 전투 셋업 및 페이즈 3 진입!
                    elif event.key == pygame.K_RETURN:
                        current_state = "BATTLE"
                        player.current_hp = player.max_hp # 꿀팁: 전투 시작 전 체력 풀회복!
                        boss = Boss(stage)
                        battle_log = [f"--- 스테이지 {stage} 보스 등장! ---"]
                        turn = "PLAYER"
                        battle_status = "ONGOING"
                        pygame.time.set_timer(BATTLE_EVENT, 1000) # 1초마다 자동 공격 시작

            # --- PHASE 3: 스테이지 보스전 (자동 턴제) ---
            elif current_state == "BATTLE":
                if event.type == BATTLE_EVENT and battle_status == "ONGOING":
                    # 내 턴
                    if turn == "PLAYER":
                        boss.current_hp -= player.atk
                        battle_log.append(f"▶ 플레이어의 공격! 보스에게 {player.atk} 피해.")
                        
                        # 보스가 죽었는지 체크
                        if boss.current_hp <= 0:
                            battle_log.append("🏆 보스 처치 성공! (스페이스바를 누르면 다음 스테이지로)")
                            battle_status = "VICTORY"
                            pygame.time.set_timer(BATTLE_EVENT, 0) # 전투 타이머 정지
                        else:
                            turn = "BOSS" # 턴 넘기기
                            
                    # 보스 턴
                    elif turn == "BOSS":
                        player.current_hp -= boss.atk
                        battle_log.append(f"▷ 보스의 공격! 플레이어에게 {boss.atk} 피해.")
                        
                        # 내가 죽었는지 체크
                        if player.current_hp <= 0:
                            battle_log.append("💀 플레이어 쓰러짐... (스페이스바를 누르면 부활 및 재도전)")
                            battle_status = "DEFEAT"
                            pygame.time.set_timer(BATTLE_EVENT, 0)
                        else:
                            turn = "PLAYER"
                            
                    # 전투 로그가 화면을 뚫고 나가지 않게 최근 5줄만 유지
                    if len(battle_log) > 5:
                        battle_log.pop(0)

                # 승리 또는 패배 후 스페이스바 누르면 다시 Phase 1(타이머)로 무한 루프
                if event.type == pygame.KEYDOWN and battle_status != "ONGOING":
                    if event.key == pygame.K_SPACE:
                        if battle_status == "VICTORY":
                            stage += 1 # 이겼을 때만 스테이지 1업!
                        time_left = 1500 # 25분 다시 세팅
                        current_state = "TIMER"

        # --- 화면 그리기 렌더링 파트 ---
        screen.fill((40, 40, 40))

        if current_state == "TIMER":
            minutes = time_left // 60
            seconds = time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"

            warning_text = font.render("경고: 창을 벗어나면 임시 자원이 소멸됩니다!", True, (255, 100, 100))
            title_text = font.render(f"[Phase 1: 집중과 파밍] - 현재 목표: 스테이지 {stage}", True, (255, 255, 255))
            timer_text = font.render(f"남은 시간: {time_str} (스페이스바: 스킵)", True, (100, 255, 100))
            info_text = font.render(f"보유 자원: {player.resource} | 임시 자원: {player.temp_resource}", True, (255, 215, 0))
            
            screen.blit(warning_text, (50, 20))
            screen.blit(title_text, (50, 70))
            screen.blit(timer_text, (50, 120))
            screen.blit(info_text, (50, 170))

        elif current_state == "UPGRADE":
            hp_prob = player.get_success_rate(player.hp_level) * 100
            atk_prob = player.get_success_rate(player.atk_level) * 100

            title_text = font.render(f"[Phase 2: 대장간 (스테이지 {stage} 준비)]", True, (255, 255, 255))
            info_text = font.render(f"보유 확정 자원: {player.resource}", True, (255, 215, 0))
            stat_text = font.render(f"HP: {player.max_hp} (Lv.{player.hp_level}) | ATK: {player.atk} (Lv.{player.atk_level})", True, (100, 200, 255))
            
            hp_guide_str = "MAX LEVEL" if player.hp_level >= 30 else f"성공률 {hp_prob:.1f}%"
            atk_guide_str = "MAX LEVEL" if player.atk_level >= 30 else f"성공률 {atk_prob:.1f}%"

            guide1 = small_font.render(f"숫자키 [1]: 체력 +20 강화 (비용 1, {hp_guide_str})", True, (200, 200, 200))
            guide2 = small_font.render(f"숫자키 [2]: 공격력 +5 강화 (비용 1, {atk_guide_str})", True, (200, 200, 200))
            guide_next = small_font.render("Enter키 누르기: 보스전 시작!", True, (255, 100, 100))

            screen.blit(title_text, (50, 50))
            screen.blit(info_text, (50, 100))
            screen.blit(stat_text, (50, 160))
            screen.blit(guide1, (50, 250))
            screen.blit(guide2, (50, 300))
            screen.blit(guide_next, (50, 400))

        elif current_state == "BATTLE":
            title_text = font.render(f"[Phase 3: 보스전 - 스테이지 {stage}]", True, (255, 50, 50))
            
            # 피통 현황 렌더링
            p_stat = font.render(f"플레이어 HP: {player.current_hp} / {player.max_hp}", True, (100, 200, 255))
            b_stat = font.render(f"보스 HP: {boss.current_hp} / {boss.max_hp}", True, (255, 100, 100))
            
            screen.blit(title_text, (50, 50))
            screen.blit(p_stat, (50, 120))
            screen.blit(b_stat, (400, 120))

            # 전투 로그 예쁘게 띄워주기
            log_start_y = 220
            for i, log in enumerate(battle_log):
                # 마지막 줄(최신 로그)은 노란색으로 강조해서 타격감 주기
                color = (255, 215, 0) if i == len(battle_log) - 1 else (200, 200, 200)
                log_text = small_font.render(log, True, color)
                screen.blit(log_text, (50, log_start_y + (i * 35)))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()