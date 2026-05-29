import pygame
import sys

# 1. 플레이어 데이터 클래스
class Player:
    def __init__(self):
        self.hp = 100
        self.atk = 10
        self.resource = 0       # 확정 자원
        self.temp_resource = 0  # 딴짓하면 날아갈 임시 자원

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("던전모도로 - 집중의 시간")
    clock = pygame.time.Clock()

    player = Player()
    
    # 폰트 설정 (맑은 고딕)
    font = pygame.font.SysFont("malgun gothic", 36)
    
    current_state = "TIMER"
    time_left = 1500 # 25분
    
    pygame.time.set_timer(pygame.USEREVENT, 1000)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # [핵심 추가] 🚨 화면 포커스를 잃었을 때 (Alt+Tab 등 딴짓 감지)
            if event.type == pygame.WINDOWFOCUSLOST and current_state == "TIMER":
                player.temp_resource = 0
                print("🚨 딴짓 감지! 임시 자원이 모두 소멸되었습니다.")
            
            # 타이머 1초씩 감소 및 자동 파밍 로직
            if event.type == pygame.USEREVENT and current_state == "TIMER":
                if time_left > 0:
                    time_left -= 1
                    
                    if time_left % 10 == 0:
                        player.temp_resource += 1
                else:
                    pass

        screen.fill((40, 40, 40))

        if current_state == "TIMER":
            minutes = time_left // 60
            seconds = time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"

            # 딴짓 경고 문구 추가 렌더링
            warning_text = font.render("경고: 창을 벗어나면 임시 자원이 소멸됩니다!", True, (255, 100, 100)) # 빨간색

            title_text = font.render("[Phase 1: 집중과 파밍]", True, (255, 255, 255))
            timer_text = font.render(f"남은 시간: {time_str}", True, (100, 255, 100))
            info_text = font.render(f"보유 자원: {player.resource} | 임시 자원: {player.temp_resource}", True, (255, 215, 0))
            
            screen.blit(warning_text, (50, 20)) # 맨 위에 빨간색 경고 추가
            screen.blit(title_text, (50, 70))
            screen.blit(timer_text, (50, 120))
            screen.blit(info_text, (50, 170))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()