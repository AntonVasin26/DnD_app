"""
Ручной тест для второго уровня — "Пятиугольник с двумя треугольниками"
(см. app/puzzle_levels.py: PENTAGON_LEVEL, и раздел про этот уровень
в PROJECT_CONTEXT.md).

Геометрия:
    Пятиугольник A-B-C-D-E (по часовой стрелке от верхней вершины A).
    Треугольник "top_wedge" приклеен РЕБРОМ A-B (сторона 1), апекс F.
    Треугольник "bottom_wedge" приклеен РЕБРОМ C-D (сторона 3), апекс G.

Линии (условия суммы):
    line1: F-B-C-G, target=18
    line2: F-A-E,   target=12
    line3: G-D-E,   target=16

В отличие от BUTTERFLY_LEVEL, здесь фигуры делят с пятиугольником ПО ДВЕ
точки каждая (саму грань), а не одну — и одна из фигур (сам пятиугольник)
5-точечная, а не 3-точечная, так что заодно проверяем, что PuzzleState
корректно работает и с 5-циклом.
"""

from app.puzzle_levels import PENTAGON_LEVEL
from app.puzzle_engine import PuzzleState

state = PuzzleState(PENTAGON_LEVEL)

print("=== Старт (по умолчанию — решено, значения по алфавиту) ===")
print("Значения:", state.values)
print("Решено?", state.is_solved())

print("\n=== Поворачиваем пятиугольник (+1) ===")
state.rotate("pentagon", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())
print("(A,B,C,D,E сдвинулись по кругу; F и G не тронуты пятиугольником напрямую,")
print(" но line2/line3 всё равно могли разъехаться — они используют A/E и D/E)")

print("\n=== Дополнительно поворачиваем top_wedge (+1) ===")
state.rotate("top_wedge", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())
print("(A и B — общие с пятиугольником — снова изменились; F тоже)")

print("\n=== Дополнительно поворачиваем bottom_wedge (+1) ===")
state.rotate("bottom_wedge", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())

print("\n=== Проверка: 5 поворотов пятиугольника подряд возвращают его на место ===")
for _ in range(5):
    state.rotate("pentagon", direction=1)
print("Значения:", state.values)
print("(должны совпасть с состоянием ПЕРЕД этим блоком — 5-цикл вернулся в себя)")
