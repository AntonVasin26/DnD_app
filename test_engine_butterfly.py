"""
Тест на два треугольника с ОБЩЕЙ вершиной C ("бабочка").

Геометрия:
    A-------B
     \\     /
      \\ C /      <- C общая для обоих треугольников
      /   \\
     /     \\
    D-------E

Треугольник 1 (верхний): A, B, C
Треугольник 2 (нижний):  D, E, C

Диагонали "прямоугольника" A-B-E-D:
    line_diag_1: A и E
    line_diag_2: B и D

Обрати внимание: диагонали НЕ включают точку C напрямую — но C всё равно
играет роль, потому что она общая вершина обеих фигур: когда мы поворачиваем
треугольник 1, число из C "уходит" в A или B, то есть в точку, которая
УЖЕ участвует в диагонали. Так фигуры оказываются связаны друг с другом.
"""

from app.puzzle_models import Level, Point, Shape, Line
from app.puzzle_engine import PuzzleState

level = Level(
    id="butterfly",
    name="Бабочка из двух треугольников",
    points=[
        Point(id="A", value=1),
        Point(id="B", value=2),
        Point(id="C", value=3),
        Point(id="D", value=4),
        Point(id="E", value=5),
    ],
    shapes=[
        # Порядок обхода по кругу: A -> B -> C -> (снова A)
        Shape(id="triangle_top", point_ids=["A", "B", "C"]),
        # Порядок обхода: D -> E -> C -> (снова D)
        Shape(id="triangle_bottom", point_ids=["D", "E", "C"]),
    ],
    lines=[
        Line(id="diag_1", point_ids=["A", "E"], target=6),   # 1 + 5 = 6 ✓ на старте
        Line(id="diag_2", point_ids=["B", "D"], target=6),   # 2 + 4 = 6 ✓ на старте
    ],
)

state = PuzzleState(level)

print("=== Старт ===")
print("Значения:", state.values)
print("Решено?", state.is_solved())

print("\n=== Поворачиваем ТОЛЬКО верхний треугольник (+1) ===")
state.rotate("triangle_top", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())
print("(диагональ A-E должна была измениться, т.к. значение A сменилось)")

print("\n=== Дополнительно поворачиваем нижний треугольник (+1) ===")
state.rotate("triangle_bottom", direction=1)
print("Значения:", state.values)
print("Решено?", state.is_solved())
