import pygame
import sys
import random # 확률 강화를 위해 추가

class Player:
    def __init__(self):
        self.hp = 100
        self.atk = 10
        self.resource = 0       
        self.temp_resource = 0  

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
    
    pygame.time.set_timer(pygame.USEREVENT, 1000)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # --- PHASE 1: 타이머 화면 이벤트 ---
            if current_state == "TIMER":
                if event.type == pygame.WINDOWFOCUSLOST:
                    player.temp_resource = 0
                    print("🚨 딴짓 감지! 임시 자원이 모두 소멸되었습니다.")
                
                if event.type == pygame.USEREVENT:
                    if time_left > 0:
                        time_left -= 1
                        if time_left % 10 == 0:
                            player.temp_resource += 1
                    else:
                        # 0초가 되면 임시 자원을 확정 자원으로 옮기고 대장간으로 이동!
                        player.resource += player.temp_resource
                        player.temp_resource = 0
                        current_state = "UPGRADE"

                # 💡 개발자용 치트키: 스페이스바 누르면 즉시 타이머 종료
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        time_left = 0

            # --- PHASE 2: 대장간 강화 화면 이벤트 ---
            elif current_state == "UPGRADE":
                if event.type == pygame.KEYDOWN:
                    # 1번 키: 체력 강화 (비용 1, 성공률 70%)
                    if event.key == pygame.K_1 and player.resource >= 1:
                        player.resource -= 1
                        if random.random() < 0.7:
                            player.hp += 20
                            print("✨ 체력 강화 성공!")
                        else:
                            print("💥 체력 강화 실패...")
                    
                    # 2번 키: 공격력 강화 (비용 1, 성공률 70%)
                    elif event.key == pygame.K_2 and player.resource >= 1:
                        player.resource -= 1
                        if random.random() < 0.7:
                            player.atk += 5
                            print("✨ 공격력 강화 성공!")
                        else:
                            print("💥 공격력 강화 실패...")

                    # 엔터 키: 보스전으로 이동 (다음 기능)
                    elif event.key == pygame.K_RETURN:
                        print("⚔️ 보스전으로 이동합니다! (다음 단계에서 구현 예정)")

        screen.fill((40, 40, 40))

        # --- 화면 렌더링 분기 ---
        if current_state == "TIMER":
            minutes = time_left // 60
            seconds = time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"

            warning_text = font.render("경고: 창을 벗어나면 임시 자원이 소멸됩니다!", True, (255, 100, 100))
            title_text = font.render("[Phase 1: 집중과 파밍]", True, (255, 255, 255))
            timer_text = font.render(f"남은 시간: {time_str} (스페이스바: 스킵)", True, (100, 255, 100))
            info_text = font.render(f"보유 자원: {player.resource} | 임시 자원: {player.temp_resource}", True, (255, 215, 0))
            
            screen.blit(warning_text, (50, 20))
            screen.blit(title_text, (50, 70))
            screen.blit(timer_text, (50, 120))
            screen.blit(info_text, (50, 170))

        elif current_state == "UPGRADE":
            title_text = font.render("[Phase 2: 대장간 (스탯 강화)]", True, (255, 255, 255))
            info_text = font.render(f"보유 확정 자원: {player.resource}", True, (255, 215, 0))
            stat_text = font.render(f"현재 스탯 -> HP: {player.hp} | ATK: {player.atk}", True, (100, 200, 255))
            
            guide1 = small_font.render("숫자키 [1] 누르기: 체력 +20 강화 (비용 1, 성공률 70%)", True, (200, 200, 200))
            guide2 = small_font.render("숫자키 [2] 누르기: 공격력 +5 강화 (비용 1, 성공률 70%)", True, (200, 200, 200))
            guide_next = small_font.render("Enter키 누르기: 전투하러 가기 (현재 콘솔 출력만)", True, (255, 100, 100))

            screen.blit(title_text, (50, 50))
            screen.blit(info_text, (50, 100))
            screen.blit(stat_text, (50, 150))
            screen.blit(guide1, (50, 250))
            screen.blit(guide2, (50, 300))
            screen.blit(guide_next, (50, 400))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()