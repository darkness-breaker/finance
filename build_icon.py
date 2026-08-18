"""生成应用图标 icon.ico（绿底白圆 + ¥ 记账符号）。运行 python build_icon.py 即可。"""

from PIL import Image, ImageDraw, ImageFont

SIZE = 256
BG_COLOR = "#0E9F6E"  # 深绿，记账/钱的含义
COIN_COLOR = "#FFFFFF"


def main():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 圆角方块背景
    draw.rounded_rectangle((8, 8, SIZE - 8, SIZE - 8), radius=56, fill=BG_COLOR)

    # 中央白色圆形（硬币造型）
    draw.ellipse((48, 48, SIZE - 48, SIZE - 48), fill=COIN_COLOR)

    # ¥ 符号：优先用带 ¥ 的粗体字体
    font = None
    for path in (
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        try:
            font = ImageFont.truetype(path, 150)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    draw.text((SIZE / 2, SIZE / 2), "¥", font=font, fill=BG_COLOR, anchor="mm")

    # 存成多尺寸 ico，保证资源管理器里各种缩放都清晰
    img.save(
        "icon.ico",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print("icon.ico 已生成")


if __name__ == "__main__":
    main()
