# Importación de librerías
import pygame
import sys
import random

# Inicialización de Pygame
pygame.init()

# Agregando música de fondo y efectos de sonido
pygame.mixer.music.load("musicaFondo.mp3")
pygame.mixer.music.play(-1)
sonido_power = pygame.mixer.Sound("musicaPower.mp3")
sonido_meta = pygame.mixer.Sound("musicaGanar.mp3")
sonido_perder = pygame.mixer.Sound("musicaPerder.mp3")

# Configuración inicial de pantalla y colores
ANCHO, ALTO = 900, 700
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("juego_laberinto")

# Colores
COLOR_FONDO = (82, 190, 128)
COLOR_JUGADOR = (244, 208, 63)
COLOR_PARED = (200, 50, 50)
COLOR_META = (50, 50, 200)
COLOR_ENEMIGO = (200, 0, 0)
COLOR_POWER = (12, 100, 25)

# Configuración del jugador
tamaño_jugador = 40
posicion_jugadorx, posicion_jugadory = 0, 0  # Comienza en la esquina superior izquierda
velocidad = 5
velocidad_normal = 5

# Tamaño de celdas para el laberinto
CELL = 40

# Configuración de tañamo de meta
meta = pygame.Rect(ANCHO - CELL, ALTO - CELL, CELL, CELL)

# Generar laberinto
def generar_laberinto():
    columnas = ANCHO // CELL
    filas = ALTO // CELL
    grid = [[1 for _ in range(columnas)] for _ in range(filas)]

    def vecinos_validos(x, y):
        vecinos = []
        if x > 1: vecinos.append((x - 2, y))
        if x < columnas - 2: vecinos.append((x + 2, y))
        if y > 1: vecinos.append((x, y - 2))
        if y < filas - 2: vecinos.append((x, y + 2))
        random.shuffle(vecinos)
        return vecinos

    def dfs(x, y):
        grid[y][x] = 0
        for nx, ny in vecinos_validos(x, y):
            if grid[ny][nx] == 1:
                grid[(y + ny) // 2][(x + nx) // 2] = 0
                dfs(nx, ny)

    dfs(0, 0)

    jugador_cx = posicion_jugadorx // CELL
    jugador_cy = posicion_jugadory // CELL
    grid[jugador_cy][jugador_cx] = 0

    meta_cx = meta.x // CELL
    meta_cy = meta.y // CELL
    grid[meta_cy][meta_cx] = 0

    paredes_generadas = []
    for fila in range(filas):
        for col in range(columnas):
            if grid[fila][col] == 1:
                x = col * CELL
                y = fila * CELL
                paredes_generadas.append(pygame.Rect(x, y, CELL, CELL))

    return paredes_generadas, grid, columnas, filas


def cell_to_px(cx, cy, w, h):
    return cx * CELL + (CELL - w) // 2, cy * CELL + (CELL - h) // 2


def vecinos_libres(grid, cx, cy):
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    libres = []
    filas = len(grid)
    cols = len(grid[0])
    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < cols and 0 <= ny < filas and grid[ny][nx] == 0:
            libres.append((nx, ny))
    return libres


# Crear laberinto
paredes, grid, COLS, ROWS = generar_laberinto()


# Configuración de enemigos
enemigos = []
velocidad_enemigo = 1.2
ultimo_update_enemigos = 0
for _ in range(1):
    libres = [(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == 0]
    ex, ey = random.choice(libres)
    px, py = cell_to_px(ex, ey, 40, 40)
    enemigos.append({
        "rect": pygame.Rect(px, py, 40, 40),
        "cx": ex,
        "cy": ey,
        "objetivo": (ex, ey)
    })

# Configuración del Power
power = pygame.Rect(random.randint(50, ANCHO - 50), random.randint(50, ALTO -50), 30, 30)
while any(power.colliderect(pared) for pared in paredes):
    power.x = random.randint(50, ANCHO - 50)
    power.y = random.randint(50, ALTO - 50)
power_activo = False
duracion_power = 3000
tiempo_power = 0

# Reloj
reloj = pygame.time.Clock()


# --- FUNCIONES ---
def mostrar_texto(texto):
    ventana.fill(COLOR_FONDO)
    fuente = pygame.font.SysFont(None, 64)
    mensaje = fuente.render(texto, True, (255, 255, 255))
    ventana.blit(mensaje, (ANCHO // 2 - mensaje.get_width() // 2, ALTO // 2 - mensaje.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)


def pantalla_inicio():
    mostrar_texto("Presiona ENTER para empezar a jugar")
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando = False


# --- Lógica principal ---
pantalla_inicio()
jugar = True

# Bucle principal
while jugar:
    tiempo_actual = pygame.time.get_ticks()
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugar = False

    jugador_rect = pygame.Rect(posicion_jugadorx, posicion_jugadory, tamaño_jugador, tamaño_jugador)
    teclas = pygame.key.get_pressed()

    # Power
    if power_activo and tiempo_actual - tiempo_power > duracion_power:
        velocidad = velocidad_normal
        power_activo = False

    # Movimiento del jugador
    if teclas[pygame.K_LEFT] and posicion_jugadorx > 0:
        jugador_rect.x -= velocidad
        if not any(jugador_rect.colliderect(p) for p in paredes):
            posicion_jugadorx -= velocidad

    if teclas[pygame.K_RIGHT] and posicion_jugadorx < ANCHO - tamaño_jugador:
        jugador_rect.x += velocidad
        if not any(jugador_rect.colliderect(p) for p in paredes):
            posicion_jugadorx += velocidad

    if teclas[pygame.K_UP] and posicion_jugadory > 0:
        jugador_rect.y -= velocidad
        if not any(jugador_rect.colliderect(p) for p in paredes):
            posicion_jugadory -= velocidad

    if teclas[pygame.K_DOWN] and posicion_jugadory < ALTO - tamaño_jugador:
        jugador_rect.y += velocidad
        if not any(jugador_rect.colliderect(p) for p in paredes):
            posicion_jugadory += velocidad

    # Movimiento de los enemigos 
    if tiempo_actual - ultimo_update_enemigos > 500:  # 0.5 s
        for i, enemigo in enumerate(enemigos):
            # Enemigo 0 persigue al jugador
            if i == 0:
                objetivo_cx = posicion_jugadorx // CELL
                objetivo_cy = posicion_jugadory // CELL
                enemigo["objetivo"] = (objetivo_cx, objetivo_cy)
            else:
                # Los otros van a una celda libre aleatoria del laberinto
                libres = [(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == 0]
                if libres:
                    nuevo = random.choice(libres)
                    enemigo["cx"], enemigo["cy"] = nuevo
                    enemigo["objetivo"] = nuevo
        ultimo_update_enemigos = tiempo_actual

    # Movimiento suave hacia su objetivo actual
    for enemigo in enemigos:
        objetivo_px, objetivo_py = cell_to_px(
            enemigo["objetivo"][0],
            enemigo["objetivo"][1],
            enemigo["rect"].width,
            enemigo["rect"].height
        )
        dx = objetivo_px - enemigo["rect"].x
        dy = objetivo_py - enemigo["rect"].y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        step_x = int(velocidad_enemigo * dx / dist)
        step_y = int(velocidad_enemigo * dy / dist)
        enemigo["rect"].x += step_x
        enemigo["rect"].y += step_y

        # Colisión con jugador
        if jugador_rect.colliderect(enemigo["rect"]):
            sonido_perder.play()
            mostrar_texto("Has perdido")
            jugar = False

    # Colisión con la meta
    if jugador_rect.colliderect(meta):
        sonido_meta.play()
        mostrar_texto("¡Felicidades, ganaste!")
        jugar = False

    # Colisión con power
    if jugador_rect.colliderect(power):
        sonido_power.play()
        power_activo = True
        tiempo_power = tiempo_actual
        velocidad = 10
        power.x, power.y = random.randint(50, ANCHO - 50), random.randint(50, ALTO - 50)

    # Dibujar los objetos en pantalla
    ventana.fill(COLOR_FONDO)
    pygame.draw.rect(ventana, COLOR_JUGADOR, jugador_rect)

    for pared in paredes:
        pygame.draw.rect(ventana, COLOR_PARED, pared)

    pygame.draw.rect(ventana, COLOR_META, meta)

    for enemigo in enemigos:
        pygame.draw.rect(ventana, COLOR_ENEMIGO, enemigo["rect"])

    if not power_activo:
        pygame.draw.rect(ventana, COLOR_POWER, power)

    pygame.display.flip()
    reloj.tick(60)

# Salida del juego
pygame.quit()
sys.exit()
