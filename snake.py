#!/usr/bin/env python3
"""
Snake Game - Terminal Version
Para Cinthya ❤️

Ejecuta con: python snake.py

Controles:
  Flechas o WASD  -> Mover
  P               -> Pausa
  R               -> Reiniciar (en game over)
  Q o ESC         -> Salir

Funciona mejor en Windows con PowerShell / CMD.
En Linux/macOS usa las flechas también.
"""

import os
import sys
import time
import random
import threading

# ====================== CONFIG ======================
WIDTH = 24
HEIGHT = 18
INITIAL_SPEED = 0.18   # segundos por movimiento (más bajo = más rápido)
SPEED_INCREMENT = 0.012
MIN_SPEED = 0.06

# Colores ANSI (funcionan en la mayoría de terminales modernas)
RESET = "\033[0m"
GREEN = "\033[92m"
BRIGHT_GREEN = "\033[1;92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GRAY = "\033[90m"
BOLD = "\033[1m"

# ====================== INPUT (Cross platform) ======================
if os.name == "nt":
    import msvcrt

    def get_key():
        """Lee una tecla de forma no bloqueante en Windows."""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b"\xe0":  # tecla especial (flechas)
                key = msvcrt.getch()
                if key == b"H":
                    return "UP"
                elif key == b"P":
                    return "DOWN"
                elif key == b"K":
                    return "LEFT"
                elif key == b"M":
                    return "RIGHT"
            else:
                try:
                    ch = key.decode("utf-8").upper()
                except:
                    ch = ""
                if ch == "W":
                    return "UP"
                elif ch == "S":
                    return "DOWN"
                elif ch == "A":
                    return "LEFT"
                elif ch == "D":
                    return "RIGHT"
                elif ch == "P":
                    return "PAUSE"
                elif ch == "R":
                    return "RESTART"
                elif ch in ("Q", "\x1b"):  # ESC
                    return "QUIT"
        return None

    def clear_screen():
        os.system("cls")

else:
    import select
    import tty
    import termios

    # Guardamos el estado original del terminal
    _orig_settings = None

    def _enable_raw_mode():
        global _orig_settings
        if _orig_settings is None:
            _orig_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def _restore_terminal():
        global _orig_settings
        if _orig_settings is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _orig_settings)

    def get_key():
        """Lee una tecla de forma no bloqueante en Unix."""
        if select.select([sys.stdin], [], [], 0.0)[0]:
            ch = sys.stdin.read(1)
            if ch == "\x1b":  # ESC sequence
                # Intentamos leer flechas
                ch2 = sys.stdin.read(1) if select.select([sys.stdin], [], [], 0.1)[0] else ""
                ch3 = sys.stdin.read(1) if select.select([sys.stdin], [], [], 0.1)[0] else ""
                seq = ch + ch2 + ch3
                if seq == "\x1b[A":
                    return "UP"
                elif seq == "\x1b[B":
                    return "DOWN"
                elif seq == "\x1b[D":
                    return "LEFT"
                elif seq == "\x1b[C":
                    return "RIGHT"
                else:
                    return "QUIT"  # ESC solo
            ch = ch.upper()
            if ch == "W":
                return "UP"
            elif ch == "S":
                return "DOWN"
            elif ch == "A":
                return "LEFT"
            elif ch == "D":
                return "RIGHT"
            elif ch == "P":
                return "PAUSE"
            elif ch == "R":
                return "RESTART"
            elif ch == "Q":
                return "QUIT"
        return None

    def clear_screen():
        os.system("clear")

# ====================== JUEGO ======================
class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [(WIDTH // 3, HEIGHT // 2),
                      (WIDTH // 3 - 1, HEIGHT // 2),
                      (WIDTH // 3 - 2, HEIGHT // 2)]
        self.direction = (1, 0)       # (dx, dy)
        self.next_direction = (1, 0)
        self.food = self._place_food()
        self.score = 0
        self.speed = INITIAL_SPEED
        self.alive = True
        self.paused = False
        self.game_over = False

    def _place_food(self):
        while True:
            pos = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
            if pos not in self.snake:
                return pos

    def change_direction(self, new_dir):
        # Evitar 180 grados
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.next_direction = new_dir

    def move(self):
        if self.paused or not self.alive:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Colisión con paredes
        if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
            self.alive = False
            self.game_over = True
            return

        # Colisión con uno mismo
        if new_head in self.snake:
            self.alive = False
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Comer
        if new_head == self.food:
            self.score += 10
            self.food = self._place_food()
            # Aumentar velocidad cada 5 manzanas
            if self.score % 50 == 0 and self.speed > MIN_SPEED:
                self.speed = max(MIN_SPEED, self.speed - SPEED_INCREMENT)
        else:
            self.snake.pop()

    def toggle_pause(self):
        if self.alive:
            self.paused = not self.paused

    def draw(self):
        clear_screen()

        # Título
        print(f"{MAGENTA}{BOLD}  🐍 SNAKE  —  PARA CINTHYA ❤️{RESET}")
        print(f"{GRAY}{'─' * (WIDTH * 2 + 2)}{RESET}")

        # Tablero
        for y in range(HEIGHT):
            row = "│ "
            for x in range(WIDTH):
                if (x, y) == self.snake[0]:
                    # Cabeza
                    row += f"{BRIGHT_GREEN}██{RESET}"
                elif (x, y) in self.snake:
                    # Cuerpo
                    row += f"{GREEN}▓▓{RESET}"
                elif (x, y) == self.food:
                    # Comida (corazón / manzana)
                    row += f"{RED}♥♥{RESET}"
                else:
                    row += f"{GRAY}··{RESET}"
            row += " │"
            print(row)

        print(f"{GRAY}{'─' * (WIDTH * 2 + 2)}{RESET}")

        # Estadísticas
        speed_level = max(1, int((INITIAL_SPEED - self.speed) / SPEED_INCREMENT) + 1)
        print(f"  {CYAN}PUNTOS:{RESET} {BOLD}{self.score:03d}{RESET}   "
              f"{CYAN}VELOCIDAD:{RESET} {BOLD}{speed_level:02d}{RESET}   "
              f"{CYAN}HIGH:{RESET} {self._get_high_score():03d}")

        # Instrucciones
        print()
        if self.game_over:
            print(f"  {RED}{BOLD}GAME OVER{RESET}")
            print(f"  {YELLOW}Presiona R para reiniciar o Q para salir{RESET}")
        elif self.paused:
            print(f"  {YELLOW}{BOLD}PAUSA{RESET}  —  Presiona P para continuar")
        else:
            print(f"  {GRAY}Flechas/WASD = mover   |   P = pausa   |   Q = salir{RESET}")

        print(f"\n  {GRAY}❤️  miamor{RESET}")

    def _get_high_score(self):
        try:
            if os.path.exists(".snake_highscore"):
                with open(".snake_highscore", "r", encoding="utf-8") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_high_score(self):
        current_high = self._get_high_score()
        if self.score > current_high:
            try:
                with open(".snake_highscore", "w", encoding="utf-8") as f:
                    f.write(str(self.score))
            except:
                pass
            return True
        return False

    def run(self):
        if os.name != "nt":
            _enable_raw_mode()

        try:
            self.draw()

            while True:
                # Leer input
                key = get_key()

                if key == "QUIT":
                    break

                if self.game_over:
                    if key == "RESTART":
                        self.reset()
                        self.draw()
                        continue
                    elif key == "QUIT":
                        break
                    time.sleep(0.05)
                    continue

                if key == "PAUSE":
                    self.toggle_pause()
                    self.draw()
                    continue

                if key == "RESTART" and self.alive:
                    self.reset()
                    self.draw()
                    continue

                if key in ("UP", "DOWN", "LEFT", "RIGHT"):
                    dirs = {
                        "UP": (0, -1),
                        "DOWN": (0, 1),
                        "LEFT": (-1, 0),
                        "RIGHT": (1, 0),
                    }
                    self.change_direction(dirs[key])

                # Mover serpiente
                if not self.paused and not self.game_over:
                    self.move()

                # Dibujar
                self.draw()

                # Game over handling
                if self.game_over:
                    self.save_high_score()
                    self.draw()
                    continue

                # Esperar (velocidad del juego)
                time.sleep(self.speed if not self.paused else 0.1)

        except KeyboardInterrupt:
            pass
        finally:
            if os.name != "nt":
                _restore_terminal()
            clear_screen()
            print(f"{MAGENTA}Gracias por jugar ❤️{RESET}")
            print(f"Tu puntuación final: {BOLD}{self.score}{RESET}\n")


if __name__ == "__main__":
    print("Iniciando Snake... (presiona Ctrl+C para salir en cualquier momento)")
    time.sleep(0.6)
    game = SnakeGame()
    game.run()
