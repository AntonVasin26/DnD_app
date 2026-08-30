"""
Ручной тест для третьего уровня — "Квадрат с двумя треугольниками"
(см. app/puzzle_levels.py: SQUARE_LEVEL, и раздел про этот уровень в
PROJECT_CONTEXT.md).

Геометрия:
    Квадрат A-B-C-D (по часовой стрелке от верхней-левой вершины A).
    Треугольник "wedge_left" касается квадрата ТОЛЬКО в вершине A, своя
        вершина F, и делит с "wedge_right" общую вершину E.
    Треугольник "wedge_right" касается квадрата ТОЛЬКО в вершине B, своя
        вершина G, и делит с "wedge_left" ТУ ЖЕ общую вершину E.

В отличие от PENTAGON_LEVEL (где фигуры делили с пятиугольником ПО ДВЕ
точки — саму грань), здесь квадрат и каждый треугольник делят РОВНО ОДНУ
точку — как в самой первой BUTTERFLY_LEVEL. Но в отличие от BUTTERFLY_LEVEL,
здесь ТРИ фигуры вместо двух, и одна из них (сам квадрат) — 4-точечная, а
не 3-точечная, так что заодно проверяем, что PuzzleState корректно работает
и с 4-циклом (пятиугольник уже проверил 5-цикл).

Линии (условия суммы):
    line1: F-A-D, target=11
    line2: G-B-C, target=12
Точка E ни в одну линию не входит — сознательное решение пользователя (см.
PROJECT_CONTEXT.md), но она всё равно двигается при повороте любого из
треугольников (входит в обе фигуры).
"""

from app.puzzle_levels import SQUARE_LEVEL
from app.puzzle_engine import PuzzleState

state = PuzzleState(SQUARE_LEVEL)

print("=== Старт (по умолчанию — решено, значения по алфавиту) ===")
print("Значения:", state.values)
print("Решено?", state.is_solved())

print("\n=== Поворачиваем квадрат (+1) ===")
state.rotate("quadrilateral", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())
print("(A,B,C,D сдвинулись по кругу; F и G не тронуты квадратом напрямую,")
print(" но line1/line2 всё равно могли разъехаться — они используют A/D и B/C)")

print("\n=== Дополнительно поворачиваем wedge_left (+1) ===")
state.rotate("wedge_left", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())
print("(A и E — общие с другими фигурами — снова изменились; F тоже)")

print("\n=== Дополнительно поворачиваем wedge_right (+1) ===")
state.rotate("wedge_right", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())

print("\n=== Проверка: 4 поворота квадрата подряд возвращают его на место ===")
for _ in range(4):
    state.rotate("quadrilateral", direction=1)
print("Значения:", state.values)
print("(должны совпасть с состоянием ПЕРЕД этим блоком — 4-цикл вернулся в себя)")

print("\n=== Проверка: точка E двигается при повороте wedge_left/wedge_right,")
print("    но ни разу не встречается ни в одной линии (свободная точка) ===")
line_points = {pid for line in SQUARE_LEVEL.lines for pid in line.point_ids}
print("Точки во всех линиях:", sorted(line_points))
print("E входит в условия суммы?", "E" in line_points)
