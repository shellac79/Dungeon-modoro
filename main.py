# main.py - 던전모도로 메인 실행 파일
import pygame
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("던전모도로 - 집중의 시간")
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        screen.fill((50, 50, 50)) # 어두운 회색 배경
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()