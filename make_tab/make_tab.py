import re
from PIL import Image, ImageDraw, ImageFont

def draw_mini_diagram(draw, x, y, fret_start, dots, mutes):
    """大判キャンバスの指定座標(x, y)に【拡大版】の指板図を描画する関数"""
    # ★視認性を上げるためにサイズを大きく調整 (12->16, 16->22)
    y_step = 16  # 弦の間隔
    x_step = 22  # フレットの間隔
    fingerboard_x = x + 45  # 左側の記号（X, O）用のマージン（広げました）

    # 1. 弦（横線6本）を描く
    for i in range(6):
        ly = y + i * y_step
        draw.line([(fingerboard_x, ly), (fingerboard_x + 4 * x_step, ly)], fill="black", width=2)

    # 2. フレット（縦線5本）を描く
    for i in range(5):
        lx = fingerboard_x + i * x_step
        width = 4 if (i == 0 and fret_start == 1) else 2
        draw.line([(lx, y), (lx, y + 5 * y_step)], fill="black", width=width)

    # 3. フレット番号を描く（文字を大きく: 14->18）
    if fret_start > 1:
        try:
            font = ImageFont.load_default(size=18)
        except TypeError:
            font = ImageFont.load_default()
        # 位置を微調整
        draw.text((x + 5, y + 5 * y_step - 18), str(fret_start), fill="black", font=font)

    # 4. バツ印(X)と開放弦(O)を左側に描く（サイズと位置を大きく微調整）
    for string, status in mutes.items():
        ly = y + (string - 1) * y_step
        if status == 'X':
            cs = 5  # バツのサイズを大きく
            draw.line([(x + 25 - cs, ly - cs), (x + 25 + cs, ly + cs)], fill="black", width=2)
            draw.line([(x + 25 - cs, ly + cs), (x + 25 + cs, ly - cs)], fill="black", width=2)
        elif status == 'O':
            r = 5   # 丸のサイズを大きく
            draw.ellipse([(x + 25 - r, ly - r), (x + 25 + r, ly + r)], outline="black", width=2)

    # 5. まるぽち（指を押さえる位置）を描く
    r_dot = 7  # ★まるぽち自体も大きく (5->7)
    for string, fret_pos in dots:
        ly = y + (string - 1) * y_step
        lx = fingerboard_x + (fret_pos - 0.5) * x_step
        draw.ellipse([(lx - r_dot, ly - r_dot), (lx + r_dot, ly + r_dot)], fill="black")


def generate_pdf_score(tab_text, pdf_filename="tab_score.pdf"):
    """テキストTAB譜からリズムと小節線を解析し、A4サイズのPDF楽譜を生成する関数"""
    lines = [line.strip() for line in tab_text.strip().split('\n') if line.strip()]
    if len(lines) < 6:
        return None

    max_len = max(len(line) for line in lines[:6])
    actions = []
    col = 0

    while col < max_len:
        is_bar = all(col < len(lines[i]) and lines[i][col] == '|' for i in range(6))
        is_hyphen = all(col < len(lines[i]) and lines[i][col] == '-' for i in range(6))

        has_digit = False
        digits_at_col = {}

        for i in range(6):
            if col < len(lines[i]):
                char = lines[i][col]
                if char.isdigit():
                    has_digit = True
                    if col + 1 < len(lines[i]) and lines[i][col+1].isdigit():
                        digits_at_col[i+1] = int(lines[i][col:col+2])
                    else:
                        if i+1 not in digits_at_col:
                            digits_at_col[i+1] = int(lines[i][col])

        if is_bar:
            actions.append(('bar',))
            col += 1
        elif has_digit:
            raw_frets = {s: 'X' for s in range(1, 7)}
            for s, f in digits_at_col.items():
                raw_frets[s] = f
            actions.append(('note', raw_frets))
            col += 2 if any(v >= 10 for v in digits_at_col.values()) else 1
        elif is_hyphen:
            actions.append(('space',))
            col += 1
        else:
            col += 1

    # 2. A4サイズキャンバスへの描画システムの設定 (サイズアップに伴い調整)
    page_width, page_height = 1200, 1600
    margin_left, margin_right = 80, 80
    margin_top, margin_bottom = 100, 100
    
    # ★図が大きくなったので、行の間隔（高さ）を広げました (160 -> 210)
    row_height = 210  

    pages = []

    def create_new_page():
        img = Image.new("RGB", (page_width, page_height), "white")
        return img, ImageDraw.Draw(img)

    current_img, current_draw = create_new_page()
    pages.append(current_img)

    x = margin_left
    y = margin_top

    for action in actions:
        if action[0] == 'bar':
            if x + 20 > page_width - margin_right:
                x = margin_left
                y += row_height
                if y + row_height > page_height - margin_bottom:
                    current_img, current_draw = create_new_page()
                    pages.append(current_img)
                    y = margin_top

            # 小節線も図の大きさに合わせて縦に長く引く (5*12 -> 5*16)
            current_draw.line([(x + 5, y), (x + 5, y + 5 * 16)], fill="gray", width=3)
            x += 20

        elif action[0] == 'space':
            if x + 16 > page_width - margin_right:
                x = margin_left
                y += row_height
                if y + row_height > page_height - margin_bottom:
                    current_img, current_draw = create_new_page()
                    pages.append(current_img)
                    y = margin_top

            # ガイドラインの間隔も調整 (12 -> 16)
            for i in range(6):
                ly = y + i * 16
                current_draw.line([(x, ly), (x + 16, ly)], fill="#f0f0f0", width=1)
            x += 16

        elif action[0] == 'note':
            # ★ミニ指板図の専有横幅を広げました (110 -> 155)
            diagram_width = 155  
            if x + diagram_width > page_width - margin_right:
                x = margin_left
                y += row_height
                if y + row_height > page_height - margin_bottom:
                    current_img, current_draw = create_new_page()
                    pages.append(current_img)
                    y = margin_top

            raw_frets = action[1]
            valid_frets = [v for v in raw_frets.values() if isinstance(v, int) and v > 0]
            fret_start = 1 if not valid_frets else (1 if min(valid_frets) <= 4 else min(valid_frets))

            dots = []
            mutes = {}
            for s, val in raw_frets.items():
                if val == 'X':
                    mutes[s] = 'X'
                elif val == 0:
                    mutes[s] = 'O'
                else:
                    dots.append((s, val - fret_start + 1))

            draw_mini_diagram(current_draw, x, y, fret_start, dots, mutes)
            x += diagram_width

    if pages:
        pages[0].save(pdf_filename, save_all=True, append_images=pages[1:])
        return pages, pdf_filename
    return None, None