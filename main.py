import math
from random import randint
import shelve

import pygame
from pygame import Vector2
from pygame.locals import *
import pygame.freetype
import sys


d = shelve.open("src/score")

pygame.init()

SCORE_FONT = pygame.freetype.Font('src/FB.ttf', 24)

BACKGROUND: tuple = (255, 255, 255)

FPS: int = 60
fpsClock = pygame.time.Clock()
WINDOW_WIDTH: int = 144
WINDOW_HEIGHT: int = 256

WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flappy Bird')

def textOutline(text, position, offset, thickness, font):
    imageOutline, RectOutline = SCORE_FONT.render(text, (0, 0, 0))
    image, rect = font.render(text, (255, 255, 255))
    output = [(imageOutline, (position.x - thickness, position.y - offset.y + thickness)), (imageOutline, (position.x + thickness, position.y - offset.y + thickness)), (imageOutline, (position.x - thickness, position.y - offset.y - thickness)), (imageOutline, (position.x + thickness, position.y - offset.y - thickness)), (image, (position.x, position.y - offset.y))]
    return output

def main():
    looping = False

    highScore = d["high"]
    score = 0

    passed = False

    tutorialImage = pygame.image.load("src/Tutorial.png")

    background = pygame.image.load("src/BG.png").convert()
    backgroundPosition = 0
    backgroundSpeed = 0.5

    pipes = [pygame.image.load("src/PT.png"), pygame.image.load("src/PB.png")]
    ground = pygame.image.load("src/Ground.png")
    groundPosition = 0

    pipeOffset = WINDOW_HEIGHT - pipes[1].get_height() + 128
    gap = 64
    pipeRange = 16
    pipePosition = Vector2(WINDOW_WIDTH, randint(-gap - pipeRange - 80, pipeRange - 80))
    foregroundSpeed = 1

    bird = [pygame.image.load("src/BB.png").convert_alpha(), pygame.image.load("src/BM.png").convert_alpha(), pygame.image.load("src/BT.png").convert_alpha()]
    birdSprite = 2.0

    colliding = False

    position = Vector2((WINDOW_WIDTH - bird[0].get_width()) / 2, (WINDOW_HEIGHT - bird[0].get_height()) / 2)

    gravity = 0.2
    jumpVelocity = -3.2
    velocity = jumpVelocity

    up = False

    while not looping:
        position.y = (WINDOW_HEIGHT - bird[0].get_height()) / 2 + math.sin(pygame.time.get_ticks() / 384) * 4
        if birdSprite < 2 and up:
            birdSprite += 0.1
        elif birdSprite >= 2 and up:
            up = False
        elif birdSprite >= 0 and not up:
            birdSprite -= 0.2
        elif birdSprite <= 0 and not up:
            up = True
        WINDOW.blit(background, (backgroundPosition, 0))
        WINDOW.blit(background, (backgroundPosition + background.get_width(), 0))

        backgroundPosition -= backgroundSpeed
        WINDOW.blit(ground, (groundPosition, 220))
        WINDOW.blit(ground, (groundPosition + ground.get_width(), 220))
        groundPosition -= foregroundSpeed
        if backgroundPosition == -background.get_width():
            backgroundPosition = 0
        if groundPosition == -ground.get_width():
            groundPosition = 0

        scoreImageOutline, scoreRectOutline = SCORE_FONT.render("HI " + str(highScore), (0, 0, 0))
        scoreImage, scoreRect = SCORE_FONT.render("HI " + str(highScore), (255, 255, 255))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 - 2, WINDOW_HEIGHT - 22))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 + 2, WINDOW_HEIGHT - 22))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 - 2, WINDOW_HEIGHT - 26))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 + 2, WINDOW_HEIGHT - 26))
        WINDOW.blit(scoreImage, (WINDOW_WIDTH / 2 - scoreRect.width / 2, WINDOW_HEIGHT - 24))

        WINDOW.blit(bird[birdSprite.__round__()], (position.x, position.y))

        WINDOW.blit(tutorialImage, (62, 152))

        pygame.display.update()
        fpsClock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE:
                    velocity = jumpVelocity
                    looping = True
            if event.type == MOUSEBUTTONDOWN:
                looping = True

    while looping:
        WINDOW.blit(background, (backgroundPosition, 0))
        WINDOW.blit(background, (backgroundPosition + background.get_width(), 0))

        backgroundPosition -= backgroundSpeed
        groundPosition -= foregroundSpeed

        if backgroundPosition <= -background.get_width():
            backgroundPosition = 0
        if groundPosition <= -ground.get_width():
            groundPosition = 0

        if pipePosition.x > -pipes[0].get_width():
            pipePosition.x -= foregroundSpeed
        else:
            passed = False
            pipePosition = Vector2(WINDOW_WIDTH, randint(-gap - pipeRange - 80, pipeRange - 80))
        WINDOW.blit(pipes[0], (pipePosition.x, pipePosition.y))
        WINDOW.blit(pipes[1], (pipePosition.x, pipePosition.y + pipeOffset + gap))

        WINDOW.blit(ground, (groundPosition, 220))
        WINDOW.blit(ground, (groundPosition + ground.get_width(), 220))

        velocity += gravity

        if birdSprite < 2:
            birdSprite += 0.2

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE:
                    velocity = jumpVelocity
                    birdSprite = 0
            if event.type == MOUSEBUTTONDOWN:
                velocity = jumpVelocity
                birdSprite = 0

        position.y += velocity

        if ((pipePosition.x + pipes[0].get_width() / 2 > position.x - bird[0].get_width() / 2 and pipePosition.x + pipes[0].get_width() / 2 < position.x + bird[0].get_width()) and (position.y - (pipePosition.y + pipeOffset) < 1 or position.y - (pipePosition.y + pipeOffset + gap) > 1)) or position.y > 220 - bird[0].get_height() or position.y < 0:
            colliding = True
            looping = False
            if score > d["high"]:
                d["high"] = score
                highScore = score
        elif pipePosition.x + pipes[0].get_width() / 2 < position.x - bird[0].get_width() / 2 and not passed:
            score += 1
            passed = True
            if score > highScore:
                highScore = score
        else:
            colliding = False
        if not colliding:
            WINDOW.blit(pygame.transform.rotate(bird[birdSprite.__round__()], -velocity * 4), (position.x, position.y))
        else:
            WINDOW.blit(pygame.transform.rotate(bird[birdSprite.__round__()], -velocity * 4), (position.x, position.y))


        textImages = textOutline(str(score), Vector2(WINDOW_WIDTH / 2, 16), Vector2(0, 0), 2, SCORE_FONT)
        for i in range(textImages.__len__()):
            WINDOW.blit(textImages[i][0], textImages[i][1])

        textImages = textOutline("HI " + str(highScore), Vector2(WINDOW_WIDTH / 2 - scoreRect.width / 2, WINDOW_HEIGHT), Vector2(0, -24), 2, SCORE_FONT)
        for i in range(textImages.__len__()):
            WINDOW.blit(textImages[i][0], textImages[i][1])

        pygame.display.update()
        fpsClock.tick(FPS)
    while ((pipePosition.x + pipes[0].get_width() / 2 > position.x - bird[0].get_width() / 2 and pipePosition.x + pipes[0].get_width() / 2 < position.x + bird[0].get_width()) and position.y - (pipePosition.y + pipeOffset + gap) <= 1) or (not (pipePosition.x + pipes[0].get_width() / 2 > position.x - bird[0].get_width() / 2 and pipePosition.x + pipes[0].get_width() / 2 < position.x + bird[0].get_width()) and position.y < 220):
        WINDOW.blit(background, (backgroundPosition, 0))
        WINDOW.blit(background, (backgroundPosition + background.get_width(), 0))
        velocity += gravity
        position.y += velocity

        WINDOW.blit(pipes[0], (pipePosition.x, pipePosition.y))
        WINDOW.blit(pipes[1], (pipePosition.x, pipePosition.y + pipeOffset + gap))

        WINDOW.blit(ground, (groundPosition, 220))
        WINDOW.blit(ground, (groundPosition + ground.get_width(), 220))

        WINDOW.blit(pygame.transform.rotate(bird[birdSprite.__round__()], -velocity * 4), (position.x, position.y))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        scoreImageOutline, scoreRectOutline = SCORE_FONT.render(str(score), (0, 0, 0))
        scoreImage, scoreRect = SCORE_FONT.render(str(score), (255, 255, 255))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 - 2, 14))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 + 2, 14))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 - 2, 18))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 + 2, 18))
        WINDOW.blit(scoreImage, (WINDOW_WIDTH / 2 - scoreRect.width / 2, 16))

        scoreImageOutline, scoreRectOutline = SCORE_FONT.render("HI " + str(highScore), (0, 0, 0))
        scoreImage, scoreRect = SCORE_FONT.render("HI " + str(highScore), (255, 255, 255))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 - 2, WINDOW_HEIGHT - 22))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 + 2, WINDOW_HEIGHT - 22))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 - 2, WINDOW_HEIGHT - 26))
        WINDOW.blit(scoreImageOutline, (WINDOW_WIDTH / 2 - scoreRect.width / 2 + 2, WINDOW_HEIGHT - 26))
        WINDOW.blit(scoreImage, (WINDOW_WIDTH / 2 - scoreRect.width / 2, WINDOW_HEIGHT - 24))

        pygame.display.update()
        fpsClock.tick(FPS)
    pygame.time.delay(500)
    main()
main()