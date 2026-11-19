"""Создание PNG из связей графа без внешнего исполняемого файла."""

from collections import defaultdict
from math import atan2, cos, pi, sin

from PIL import Image, ImageDraw, ImageFont


MARGIN = 40
NODE_HEIGHT = 43
ROW_GAP = 28
COLUMN_GAP = 76
TEXT_PADDING = 34
FONT_SIZE = 17
ARROW_SIZE = 9
PORT_OFFSET = 8
EDGE_COLOR = "#52677e"
BACK_EDGE_COLOR = "#a85436"


def graph_columns(graph):
    """Разместить каждый узел в колонке кратчайшего пути от корня."""
    root = next(iter(graph))
    depths = {root: 0}
    columns = defaultdict(list)
    for node, children in graph.items():
        depth = depths[node]
        columns[depth].append(node)
        for child in children:
            depths.setdefault(child, depth + 1)
    return list(columns.values())


def layout(graph, font):
    """Рассчитать прямоугольники узлов и полный размер рисунка."""
    columns = graph_columns(graph)
    rows = max(map(len, columns))
    row_step = NODE_HEIGHT + ROW_GAP
    height = rows * row_step - ROW_GAP + 2 * MARGIN
    boxes = {}
    x = MARGIN
    for column in columns:
        width = max(int(font.getlength(str(node))) for node in column)
        width += TEXT_PADDING
        y = MARGIN + (rows - len(column)) * row_step // 2
        for node in column:
            boxes[node] = (x, y, x + width, y + NODE_HEIGHT)
            y += row_step
        x += width + COLUMN_GAP
    return boxes, (x - COLUMN_GAP + MARGIN, height)


def draw_arrow(draw, points, color):
    """Нарисовать линию и треугольный наконечник."""
    draw.line(points, fill=color, width=2, joint="curve")
    x, y = points[-1]
    px, py = points[-2]
    angle = atan2(y - py, x - px)
    spread = pi / 6
    sides = [
        (x - ARROW_SIZE * cos(angle + offset),
         y - ARROW_SIZE * sin(angle + offset))
        for offset in (-spread, spread)
    ]
    draw.polygon([(x, y), *sides], fill=color)


def draw_edge(draw, source, target):
    """Соединить колонки, выводя обратные рёбра через боковой отступ."""
    sx, sy, sx2, sy2 = source
    tx, ty, tx2, ty2 = target
    start = (sx2, (sy + sy2) // 2)
    if tx > sx:
        finish = (tx, (ty + ty2) // 2)
        turn = (sx2 + tx) // 2
        points = [start, (turn, start[1]), (turn, finish[1]), finish]
        draw_arrow(draw, points, EDGE_COLOR)
        return
    if tx == sx and ty != sy:
        start = (sx2, start[1] + PORT_OFFSET)
        finish = (tx2, (ty + ty2) // 2 + PORT_OFFSET)
        offset = COLUMN_GAP // (3 if ty > sy else 5)
        turn = sx2 + offset
        points = [start, (turn, start[1]), (turn, finish[1]), finish]
        draw_arrow(draw, points, BACK_EDGE_COLOR)
        return
    step = COLUMN_GAP // 4
    finish = ((tx + tx2) // 2, ty)
    turn = sx2 + step
    top = min(sy, ty) - ROW_GAP // 2
    points = [
        start, (turn, start[1]), (turn, top), (finish[0], top), finish,
    ]
    draw_arrow(draw, points, BACK_EDGE_COLOR)


def save_png(graph, path):
    """Сохранить PNG со всеми узлами и направленными рёбрами."""
    font = ImageFont.load_default(size=FONT_SIZE)
    boxes, size = layout(graph, font)
    with Image.new("RGB", size, "#f5f8fc") as image:
        draw = ImageDraw.Draw(image)
        for node, children in graph.items():
            for child in children:
                draw_edge(draw, boxes[node], boxes[child])
        for index, (node, box) in enumerate(boxes.items()):
            x1, y1, x2, y2 = box
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            fill = "#d7ebff" if index == 0 else "#ffffff"
            draw.rounded_rectangle(box, radius=8, fill=fill,
                                   outline="#39618b", width=2)
            draw.text(center, str(node), font=font, fill="#183153", anchor="mm")
        image.save(path, format="PNG")
