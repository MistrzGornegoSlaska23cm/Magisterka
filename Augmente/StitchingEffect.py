import random
from PIL import Image, ImageDraw

class RandomStitchingEffect:
    def __init__(
        self,
        p=0.5,
        max_shift=24,
        max_gap=10,
        min_gap=4,
        seam_line_prob=1.0,
        seam_line_width_range=(2, 4),
        split_ratio_range=(0.4, 0.6),
        gap_color_range=(175, 225),
        seam_dark_range=(70, 125),
        seam_light_range=(190, 235),
    ):
        self.p = p
        self.max_shift = max_shift
        self.max_gap = max_gap
        self.min_gap = min_gap
        self.seam_line_prob = seam_line_prob
        self.seam_line_width_range = seam_line_width_range
        self.split_ratio_range = split_ratio_range
        self.gap_color_range = gap_color_range
        self.seam_dark_range = seam_dark_range
        self.seam_light_range = seam_light_range
        
    def __call__(self, img):
        if random.random() > self.p:
            return img
        
        w, h = img.size
        result = Image.new('RGB', (w, h), (235, 235, 235))
        draw = ImageDraw.Draw(result)
        
        is_vertical = random.choice([True, False])
        if is_vertical:
            split_x = random.randint(int(w * self.split_ratio_range[0]), int(w * self.split_ratio_range[1]))
            split_y = random.randint(-self.max_shift, self.max_shift)
            gap = random.randint(self.min_gap, max(self.min_gap, self.max_gap))
            
            left_part = img.crop((0, 0, split_x, h))
            right_part = img.crop((split_x, 0, w, h))
            
            result.paste(left_part, (0, 0))
            result.paste(right_part, (split_x + gap, split_y))

            gap_color = random.randint(*self.gap_color_range)
            draw.rectangle([split_x, 0, min(w - 1, split_x + gap), h - 1], fill=(gap_color, gap_color, gap_color))

            if random.random() < self.seam_line_prob:
                line_w = random.randint(*self.seam_line_width_range)
                dark = random.randint(*self.seam_dark_range)
                light = random.randint(*self.seam_light_range)
                draw.rectangle([max(0, split_x - line_w), 0, split_x, h - 1], fill=(dark, dark, dark))
                draw.rectangle([min(w - 1, split_x + gap), 0, min(w - 1, split_x + gap + line_w), h - 1], fill=(light, light, light))
        else:
            split_y = random.randint(int(h * self.split_ratio_range[0]), int(h * self.split_ratio_range[1]))
            split_x = random.randint(-self.max_shift, self.max_shift)
            gap = random.randint(self.min_gap, max(self.min_gap, self.max_gap))
            
            top_part = img.crop((0, 0, w, split_y))
            bottom_part = img.crop((0, split_y, w, h))
            
            result.paste(top_part, (0, 0))
            result.paste(bottom_part, (split_x, split_y + gap))

            gap_color = random.randint(*self.gap_color_range)
            draw.rectangle([0, split_y, w - 1, min(h - 1, split_y + gap)], fill=(gap_color, gap_color, gap_color))

            if random.random() < self.seam_line_prob:
                line_w = random.randint(*self.seam_line_width_range)
                dark = random.randint(*self.seam_dark_range)
                light = random.randint(*self.seam_light_range)
                draw.rectangle([0, max(0, split_y - line_w), w - 1, split_y], fill=(dark, dark, dark))
                draw.rectangle([0, min(h - 1, split_y + gap), w - 1, min(h - 1, split_y + gap + line_w)], fill=(light, light, light))
        
        return result
    def __repr__(self):
        return f"{self.__class__.__name__}(p={self.p}, max_shift={self.max_shift}, max_gap={self.max_gap})"