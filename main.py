import asyncio
import pygame
from config import FPS
from ui import UI
from controller import GameController


async def main():
    ui = UI()
    controller = GameController(ui)

    running = True
    while running:
        dt = ui.clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                controller.handle_event(event)

        controller.update(dt)
        ui.draw_ui(controller.view_model())

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
