"""
Быстрая ручная проверка puzzle_engine — НЕ часть веб-сервера,
просто скрипт для эксперимента, чтобы своими глазами увидеть,
что rotate() и is_solved() работают правильно, прежде чем
подключать это к WebSocket.
"""

from app.puzzle_models import Level, Point, Shape, Line
from app.puzzle_engine import PuzzleState

# Простейший уровень: треугольник A-B-C.
# Линия — это сам треугольник целиком: сумма его вершин должна быть равна 6.
test_level = Level(
    id="test_triangle",
    name="Тестовый треугольник",
    points=[
        Point(id="A", value=1),
        Point(id="B", value=2),
        Point(id="C", value=3),
    ],
    shapes=[
        Shape(id="triangle_1", point_ids=["A", "B", "C"]),
    ],
    lines=[
        Line(id="line_1", point_ids=["A", "B", "C"], target=6),
    ],
)

state = PuzzleState(test_level)

print("Стартовые значения:", state.values)
print("Решено?", state.is_solved())  # Ожидаем True: 1+2+3=6

print("\nПоворачиваем triangle_1 на +1...")
state.rotate("triangle_1", direction=1)
print("Значения после поворота:", state.values)
print("Решено?", state.is_solved())  # Всё ещё True: сумма не меняется от сдвига!

print("\nПоворачиваем triangle_1 на -1 (обратно)...")
state.rotate("triangle_1", direction=-1)
print("Значения после обратного поворота:", state.values)
print("Решено?", state.is_solved())
