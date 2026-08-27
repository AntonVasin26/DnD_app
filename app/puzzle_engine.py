"""
Игровой движок: хранит ТЕКУЩЕЕ состояние (какие числа сейчас на точках)
и умеет поворачивать фигуры / проверять победу.

Level (из puzzle_models.py) — это неизменный шаблон уровня.
PuzzleState — это состояние конкретной игровой сессии, которое меняется
по ходу игры и должно быть общим для всех подключённых игроков.
"""

from app.puzzle_models import Level


class PuzzleState:
    def __init__(self, level: Level):
        self.level = level
        # Словарь id точки -> текущее значение. Берём стартовые значения
        # прямо из уровня (level.points), но дальше именно ЭТОТ словарь
        # будет меняться при поворотах, а не level.points.
        self.values: dict[str, int] = {
            point.id: point.value for point in level.points
        }
        # Быстрый доступ к фигуре/линии по id, чтобы не искать перебором
        # каждый раз в списке.
        self.shapes_by_id = {shape.id: shape for shape in level.shapes}

    def rotate(self, shape_id: str, direction: int) -> None:
        """
        Поворачивает фигуру на один шаг.
        direction: +1 — по часовой стрелке (в порядке point_ids),
                   -1 — против часовой стрелки.
        """
        shape = self.shapes_by_id[shape_id]
        point_ids = shape.point_ids
        n = len(point_ids)

        # Снимаем текущие значения именно этой фигуры (в её порядке)
        current_values = [self.values[pid] for pid in point_ids]

        # Циклический сдвиг: значение с позиции i переезжает на позицию
        # (i + direction) % n. Знак direction управляет направлением.
        new_values = [None] * n
        for i in range(n):
            new_position = (i + direction) % n
            new_values[new_position] = current_values[i]

        # Записываем сдвинутые значения обратно в общий словарь по точкам
        for pid, value in zip(point_ids, new_values):
            self.values[pid] = value

    def is_solved(self) -> bool:
        """Проверяет, что ВСЕ линии уровня одновременно выполняют своё условие."""
        for line in self.level.lines:
            values = [self.values[pid] for pid in line.point_ids]
            if line.operation == "sum":
                if sum(values) != line.target:
                    return False
            else:
                raise ValueError(f"Неизвестная операция: {line.operation}")
        return True
