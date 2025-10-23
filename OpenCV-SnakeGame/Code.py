import cv2
import mediapipe as mp
import pygame
import random
import numpy as np

# Setup for camera and Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)

# Snake game setup using pygame
pygame.init()
window_size = (640, 480)
game_display = pygame.display.set_mode(window_size)
pygame.display.set_caption("Gesture-Controlled Snake Game")

clock = pygame.time.Clock()
snake_pos = [320, 240]
snake_body = [[320, 240]]
snake_direction = 'RIGHT'
change_to = snake_direction
score = 0

food_pos = [random.randrange(1, (window_size[0]//10)) * 10, 
            random.randrange(1, (window_size[1]//10)) * 10]
food_spawn = True

def game_over():
    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()
    quit()

# Main loop
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over()

        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                finger_x = int(index_finger_tip.x * window_size[0])
                finger_y = int(index_finger_tip.y * window_size[1])

                # Map hand position to snake direction
                if abs(finger_x - snake_pos[0]) > abs(finger_y - snake_pos[1]):
                    if finger_x < snake_pos[0]:
                        change_to = 'LEFT'
                    elif finger_x > snake_pos[0]:
                        change_to = 'RIGHT'
                else:
                    if finger_y < snake_pos[1]:
                        change_to = 'UP'
                    elif finger_y > snake_pos[1]:
                        change_to = 'DOWN'
        
        # Change direction
        if change_to == 'RIGHT' and not snake_direction == 'LEFT':
            snake_direction = 'RIGHT'
        if change_to == 'LEFT' and not snake_direction == 'RIGHT':
            snake_direction = 'LEFT'
        if change_to == 'UP' and not snake_direction == 'DOWN':
            snake_direction = 'UP'
        if change_to == 'DOWN' and not snake_direction == 'UP':
            snake_direction = 'DOWN'

        # Move snake
        if snake_direction == 'RIGHT':
            snake_pos[0] += 10
        if snake_direction == 'LEFT':
            snake_pos[0] -= 10
        if snake_direction == 'UP':
            snake_pos[1] -= 10
        if snake_direction == 'DOWN':
            snake_pos[1] += 10

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))
        if snake_pos == food_pos:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [random.randrange(1, (window_size[0]//10)) * 10,
                        random.randrange(1, (window_size[1]//10)) * 10]
        food_spawn = True

        # Game Over conditions
        if snake_pos[0] < 0 or snake_pos[0] > window_size[0]-10:
            game_over()
        if snake_pos[1] < 0 or snake_pos[1] > window_size[1]-10:
            game_over()
        for block in snake_body[1:]:
            if snake_pos == block:
                game_over()

        game_display.fill((0, 0, 0))
        for pos in snake_body:
            pygame.draw.rect(game_display, (0, 255, 0), pygame.Rect(pos[0], pos[1], 10, 10))
        pygame.draw.rect(game_display, (255, 0, 0), pygame.Rect(food_pos[0], food_pos[1], 10, 10))

        font = pygame.font.SysFont('arial', 20)
        score_text = font.render('Score: {}'.format(score), True, (255, 255, 255))
        game_display.blit(score_text, [0, 0])
        pygame.display.update()
        clock.tick(15)
