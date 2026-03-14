import random
from PIL import Image, ImageDraw, ImageFilter


class RandomMarkerEffect:
    def __init__(
        self,
        p=0.5,
        thickness_range=(5, 15),
        alpha_range=(80, 160),
        marker_size_range=None,
    ):
        self.p = p
        if marker_size_range is not None:
            thickness_range = marker_size_range
        self.thickness_range = thickness_range
        self.alpha_range = alpha_range

        self.colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
        ]

    def __call__(self, img):
        if random.random() > self.p:
            return img
        w, h = img.size

        marker_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(marker_layer)

        base_color = random.choice(self.colors)
        alpha = random.randint(*self.alpha_range)
        marker_color = (*base_color, alpha)

        thickness = random.randint(*self.thickness_range)

        cx = random.randint(-w // 2, w + w // 2)
        cy = random.randint(-h // 2, h + h // 2)
        rx = random.randint(w // 2, w * 2)
        ry = random.randint(h // 2, h * 2)

        start_angle = random.randint(0, 360)
        end_angle = start_angle + random.randint(30, 120)

        bbox = [cx - rx, cy - ry, cx + rx, cy + ry]
        draw.arc(bbox, start=start_angle, end=end_angle, fill=marker_color, width=thickness)

        marker_layer = marker_layer.filter(ImageFilter.GaussianBlur(radius=1.5))

        result = img.convert('RGBA')
        result = Image.alpha_composite(result, marker_layer)
        return result.convert('RGB')

    def __repr__(self):
        return f"{self.__class__.__name__}(p={self.p})"