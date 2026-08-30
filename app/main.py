import time
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.puzzle_engine import PuzzleState
from app.puzzle_levels import BUTTERFLY_LEVEL, PENTAGON_LEVEL, SQUARE_LEVEL

app = FastAPI()

# Пользователь решил: ВСЕ уровни показываются на ОДНОЙ странице одновременно
# (а не выбор одного уровня из списка) — значит на сервере теперь ОДНОВРЕМЕННО
# живут НЕСКОЛЬКО независимых игровых сессий, по одной на каждый уровень.
# Раньше был единственный global `puzzle_state` — теперь это словарь
# level_id -> PuzzleState, и в протоколе WebSocket у каждого сообщения
# появилось поле "level_id", чтобы было понятно, какой из уровней оно
# касается (см. build_state_message / puzzle_ws ниже).
LEVELS = {
    "butterfly": BUTTERFLY_LEVEL,
    "pentagon": PENTAGON_LEVEL,
    "square": SQUARE_LEVEL,
}

puzzle_states: dict[str, PuzzleState] = {}
for _level_id, _level in LEVELS.items():
    _state = PuzzleState(_level)
    # Каждый уровень в исходном виде УЖЕ решён (иначе не с чем было бы
    # сверяться при разработке) — перемешиваем ПРИ СТАРТЕ СЕРВЕРА теми же
    # ходами, что доступны игроку, поэтому результат всегда решаем (см.
    # puzzle_engine.scramble). Подстраховка на случай, если перемешивание
    # случайно вернуло уровень в решённое состояние — крутим ещё раз.
    _state.scramble()
    while _state.is_solved():
        _state.scramble()
    puzzle_states[_level_id] = _state

# Должно совпадать с суммарной длительностью анимации на фронтенде:
# FADE_DURATION_MS*2 + ROTATE_DURATION_MS = 250+250+1600 = 2100мс
# (см. index.html). Пока фигура "физически крутится" у ВСЕХ игроков,
# сервер игнорирует новые клики ПО ТОМУ ЖЕ уровню — иначе два поворота
# могли бы наложиться друг на друга и состояние на экранах разошлось бы.
ANIMATION_LOCK_SECONDS = 2.1

# Блокировка — ОТДЕЛЬНО НА КАЖДЫЙ УРОВЕНЬ: пока крутится пятиугольник,
# бабочку крутить можно как ни в чём не бывало — это два независимых
# состояния, у них нет причин мешать друг другу.
busy_until: dict[str, float] = {level_id: 0.0 for level_id in LEVELS}

# Цвета для курсоров игроков (presence) — выдаются по кругу в порядке
# подключения, стараясь не повторять цвет, который прямо сейчас занят
# кем-то ещё активным (см. ConnectionManager.connect). Один и тот же цвет
# игрока используется на ОБОИХ уровнях сразу — это же один и тот же
# человек, просто может водить мышью то над одной головоломкой, то над
# другой.
PLAYER_COLORS = [
    "#ff6b6b",  # красный
    "#4dabf7",  # синий
    "#69db7c",  # зелёный
    "#ffd43b",  # жёлтый
    "#da77f2",  # фиолетовый
    "#ff922b",  # оранжевый
]


class ConnectionManager:
    """Хранит список всех сейчас открытых WebSocket-соединений и умеет
    разослать одно и то же сообщение всем сразу.

    Дополнительно хранит per-connection "личность" игрока (id + цвет) —
    нужна для presence (курсоры других игроков): без стабильного id клиент
    не смог бы понять, что два подряд пришедших сообщения о курсоре — это
    один и тот же человек продолжает водить мышью, а не два разных."""

    def __init__(self) -> None:
        self.active: list[WebSocket] = []
        self.players: dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket) -> dict:
        await websocket.accept()
        self.active.append(websocket)

        used_colors = {info["color"] for info in self.players.values()}
        color = next(
            (c for c in PLAYER_COLORS if c not in used_colors),
            PLAYER_COLORS[len(self.players) % len(PLAYER_COLORS)],
        )
        player = {"id": uuid.uuid4().hex[:8], "color": color}
        self.players[websocket] = player
        return player

    def disconnect(self, websocket: WebSocket) -> dict | None:
        if websocket in self.active:
            self.active.remove(websocket)
        return self.players.pop(websocket, None)

    async def broadcast(self, message: dict, exclude: WebSocket | None = None) -> None:
        # Если у кого-то соединение уже "протухло" (например, закрыл вкладку
        # без штатного disconnect) — не роняем рассылку остальным из-за него,
        # а тихо убираем его из списка после цикла.
        dead: list[WebSocket] = []
        for connection in self.active:
            if connection is exclude:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)


manager = ConnectionManager()


def build_state_message(level_id: str, last_move: dict | None) -> dict:
    """Собирает ПОЛНОЕ состояние ОДНОГО уровня в виде словаря, готового
    к отправке как JSON. last_move=None — это "снимок" для только что
    подключившегося игрока (без анимации, просто нарисовать как есть).
    last_move={"shape_id": ..., "direction": ...} — результат чьего-то
    реального поворота, все клиенты должны проиграть анимацию ИМЕННО на
    уровне level_id (остальные уровни это сообщение не касается).
    """
    state = puzzle_states[level_id]

    lines_payload = {}
    for line in state.level.lines:
        current_values = [state.values[pid] for pid in line.point_ids]
        current_sum = sum(current_values)
        lines_payload[line.id] = {
            "point_ids": line.point_ids,
            "sum": current_sum,
            "target": line.target,
            "ok": current_sum == line.target,
        }

    return {
        "type": "state",
        "level_id": level_id,
        "values": state.values,
        "is_solved": state.is_solved(),
        "lines": lines_payload,
        "shapes": {shape.id: shape.point_ids for shape in state.level.shapes},
        "last_move": last_move,
    }


@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")


@app.get("/api/status")
def status():
    return {"message": "Сервер работает!"}


@app.websocket("/ws")
async def puzzle_ws(websocket: WebSocket):
    player = await manager.connect(websocket)
    # "welcome" — разовое сообщение ТОЛЬКО этому клиенту: его id и цвет.
    # Отдельное от снимка состояния, потому что это персональная информация
    # (у каждого игрока свой id/цвет), а не общее состояние головоломки.
    await websocket.send_json({"type": "welcome", "id": player["id"], "color": player["color"]})
    # Снимок состояния КАЖДОГО уровня — раз все они на одной странице,
    # новому игроку нужно сразу увидеть все головоломки как есть (включая
    # уже частично решённые кем-то другим), а не только первую.
    for level_id in LEVELS:
        await websocket.send_json(build_state_message(level_id, last_move=None))

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            level_id = data.get("level_id")

            if message_type == "cursor":
                # Presence: просто пересылаем позицию курсора и признак
                # "нажато" ВСЕМ остальным игрокам, добавив id/цвет отправителя
                # и level_id (чтобы остальные знали, НАД КАКИМ ИМЕННО уровнем
                # сейчас курсор — на странице их теперь несколько). Игнорируем
                # сообщение про уровень, которого не существует.
                if level_id not in LEVELS:
                    continue
                await manager.broadcast(
                    {
                        "type": "cursor",
                        "level_id": level_id,
                        "id": player["id"],
                        "color": player["color"],
                        "x": data.get("x"),
                        "y": data.get("y"),
                        "clicking": bool(data.get("clicking")),
                        "visible": bool(data.get("visible", True)),
                    },
                    exclude=websocket,
                )
                continue

            # Иначе считаем, что это запрос на поворот фигуры НА КОНКРЕТНОМ
            # уровне level_id.
            if level_id not in puzzle_states:
                continue
            state = puzzle_states[level_id]

            shape_id = data.get("shape_id")
            direction = data.get("direction")

            # Защита от некорректных/чужеродных сообщений (например, если
            # кто-то откроет консоль браузера и пошлёт мусор в сокет).
            if shape_id not in state.shapes_by_id or direction not in (1, -1):
                continue

            now = time.monotonic()
            if now < busy_until[level_id]:
                # Кто-то другой уже крутит фигуру НА ЭТОМ ЖЕ уровне — клик
                # просто теряется. Другой уровень эта блокировка не касается.
                continue

            state.rotate(shape_id, direction)
            busy_until[level_id] = now + ANIMATION_LOCK_SECONDS

            state_message = build_state_message(
                level_id, last_move={"shape_id": shape_id, "direction": direction}
            )
            await manager.broadcast(state_message)
    except WebSocketDisconnect:
        left_player = manager.disconnect(websocket)
        if left_player is not None:
            # Сообщаем всем остальным, что курсор этого игрока нужно убрать
            # с экрана — сразу с ОБОИХ уровней (level_id тут не нужен: клиент
            # сам знает, на каком из уровней у него был виден этот id, и
            # просто уберёт его отовсюду, где найдёт).
            await manager.broadcast({"type": "cursor_leave", "id": left_player["id"]})


# Важно: этот mount должен быть ПОСЛЕ всех @app.get(...) / @app.websocket(...)
# выше. FastAPI сначала проверяет отдельные маршруты ("/", "/api/status",
# "/ws"), и только если ни один из них не подошёл — отдаёт запрос сюда,
# пытаясь найти файл внутри app/static по такому же относительному пути.
app.mount("/", StaticFiles(directory="app/static"), name="static")
