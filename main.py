import pygame
import sys
import random 

# 1. 플레이어 데이터 클래스 (레벨 변수 및 확률 계산 기능 추가)
class Player:
    def __init__(self):
        self.hp = 100
        self.atk = 10
        self.hp_level = 0    # 체력 강화 레벨 (최대 30)
        self.atk_level = 0   # 공격력 강화 레벨 (최대 30)
        self.resource = 0       # 확정 자원
        self.temp_resource = 0  # 딴짓하면 날아갈 임시 자원

    # 레벨에 따른 성공 확률 계산 함수 (0레벨: 100% -> 29레벨: 10%)
    def get_success_rate(self, level):
        if level >= 30:
            return 0.0 # 이미 만렙이면 확률 0%
        # 1.0(100%)에서 시작해서, 레벨이 1 오를 때마다 일정하게 감소
        return 1.0 - (level / 29.0) * 0.9

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
                            player.temp_resource += 10 # 💡 테스트 편하게 자원 수급량을 10으로 설정!
                    else:
                        player.resource += player.temp_resource
                        player.temp_resource = 0
                        current_state = "UPGRADE"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        time_left = 0

            # --- PHASE 2: 대장간 강화 화면 이벤트 ---
            elif current_state == "UPGRADE":
                if event.type == pygame.KEYDOWN:
                    # 1번 키: 체력 강화 (비용 1, 만렙 30)
                    if event.key == pygame.K_1 and player.resource >= 1:
                        if player.hp_level < 30:
                            player.resource -= 1
                            prob = player.get_success_rate(player.hp_level)
                            if random.random() < prob:
                                player.hp += 20
                                player.hp_level += 1
                                print(f"✨ 체력 강화 성공! (현재 Lv.{player.hp_level})")
                            else:
                                print(f"💥 체력 강화 실패... (확률: {prob*100:.1f}%)")
                        else:
                            print("체력이 이미 최대 레벨(30)입니다.")
                    
                    # 2번 키: 공격력 강화 (비용 1, 만렙 30)
                    elif event.key == pygame.K_2 and player.resource >= 1:
                        if player.atk_level < 30:
                            player.resource -= 1
                            prob = player.get_success_rate(player.atk_level)
                            if random.random() < prob:
                                player.atk += 5
                                player.atk_level += 1
                                print(f"✨ 공격력 강화 성공! (현재 Lv.{player.atk_level})")
                            else:
                                print(f"💥 공격력 강화 실패... (확률: {prob*100:.1f}%)")
                        else:
                            print("공격력이 이미 최대 레벨(30)입니다.")

                    # 엔터 키: 보스전으로 이동
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
            # 실시간 확률 계산 (소수점 첫째 자리까지 표시)
            hp_prob = player.get_success_rate(player.hp_level) * 100
            atk_prob = player.get_success_rate(player.atk_level) * 100

            title_text = font.render("[Phase 2: 대장간 (확률형 스탯 강화)]", True, (255, 255, 255))
            info_text = font.render(f"보유 확정 자원: {player.resource}", True, (255, 215, 0))
            
            # 레벨과 스탯을 한눈에 보이게 수정
            stat_text = font.render(f"HP: {player.hp} (Lv.{player.hp_level}) | ATK: {player.atk} (Lv.{player.atk_level})", True, (100, 200, 255))
            
            # 레벨 30 도달 시 MAX 문구 띄우기
            hp_guide_str = "MAX LEVEL" if player.hp_level >= 30 else f"성공률 {hp_prob:.1f}%"
            atk_guide_str = "MAX LEVEL" if player.atk_level >= 30 else f"성공률 {atk_prob:.1f}%"

            guide1 = small_font.render(f"숫자키 [1]: 체력 +20 강화 (비용 1, {hp_guide_str})", True, (200, 200, 200))
            guide2 = small_font.render(f"숫자키 [2]: 공격력 +5 강화 (비용 1, {atk_guide_str})", True, (200, 200, 200))
            guide_next = small_font.render("Enter키 누르기: 전투하러 가기", True, (255, 100, 100))

            screen.blit(title_text, (50, 50))
            screen.blit(info_text, (50, 100))
            screen.blit(stat_text, (50, 160))
            screen.blit(guide1, (50, 250))
            screen.blit(guide2, (50, 300))
            screen.blit(guide_next, (50, 400))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()