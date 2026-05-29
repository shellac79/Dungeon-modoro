import pygame
import sys

# 1. 플레이어 데이터 클래스 (직관적이고 심플하게 구조화)
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
    
    # 타이머 세팅 (25분 = 1500초)
    time_left = 1500
    
    # Pygame의 USEREVENT를 이용해 현실 시간으로 1초(1000ms)마다 이벤트 발생
    pygame.time.set_timer(pygame.USEREVENT, 1000)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 2. 타이머 1초씩 감소 및 자동 파밍 로직
            if event.type == pygame.USEREVENT and current_state == "TIMER":
                if time_left > 0:
                    time_left -= 1
                    
                    # 10초 버틸 때마다 임시 자원 1 획득 (파밍 테스트용)
                    if time_left % 10 == 0:
                        player.temp_resource += 1
                else:
                    # 타이머가 0이 되면 휴식/강화 타임으로 넘어갈 예정
                    pass

        # 배경색 칠하기
        screen.fill((40, 40, 40))

        # 3. 화면 렌더링
        if current_state == "TIMER":
            # 초를 분:초 형식(00:00)으로 예쁘게 변환
            minutes = time_left // 60
            seconds = time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"

            # 화면에 띄울 글씨들 렌더링
            title_text = font.render("[Phase 1: 집중과 파밍]", True, (255, 255, 255))
            timer_text = font.render(f"남은 시간: {time_str}", True, (100, 255, 100)) # 초록색
            info_text = font.render(f"보유 자원: {player.resource} | 임시 자원: {player.temp_resource}", True, (255, 215, 0)) # 노란색
            
            # 실제 화면에 글씨 그리기 (x, y 좌표)
            screen.blit(title_text, (50, 50))
            screen.blit(timer_text, (50, 100))
            screen.blit(info_text, (50, 150))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()