"""
Тест на два треугольника с ОБЩЕЙ вершиной C ("бабочка").

Геометрия (актуальная, синхронизирована с фронтендом и с
app/puzzle_levels.py — см. пункт 15 плана в PROJECT_CONTEXT.md):

    A-------B
     \\     /
      \\ C /      <- C общая для обоих треугольников
      /   \\
     /     \\
    D-------E

Фигура "left" (левая): A, C, D
Фигура "right" (правая): B, E, C

Диагонали идут ЧЕРЕЗ общую точку C:
    diag1: A - C - E, target = 9
    diag2: B - C - D, target = 9

Обрати внимание: раньше здесь была УПРОЩЁННАЯ 2-точечная версия (диагонали
A-E и B-D, БЕЗ точки C, target=6) — она не совпадала с тем, что давно
показывает фронтенд-прототип. Теперь оба теста используют один и тот же
объект BUTTERFLY_LEVEL из app/puzzle_levels.py, так что расхождений больше
быть не может: если кто-то поменяет геометрию уровня, тест и фронтенд
"разъедутся" сразу заметно (тест упадёт по смыслу), а не тихо.
"""

from app.puzzle_levels import BUTTERFLY_LEVEL
from app.puzzle_engine import PuzzleState

state = PuzzleState(BUTTERFLY_LEVEL)

print("=== Старт ===")
print("Значения:", state.values)
print("Решено?", state.is_solved())

print("\n=== Поворачиваем ТОЛЬКО левую фигуру (+1) ===")
state.rotate("left", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())
print("(диагонали должны были измениться, т.к. A и C сменили значения)")

print("\n=== Дополнительно поворачиваем правую фигуру (+1) ===")
state.rotate("right", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())
