import random
from PIL import Image, ImageDraw, ImageFilter

class RandomInkEffect:
    
    def __init__(self, p=0.5, int_size_range=(15,60)):
        self.p = p
        self.int_size_range = int_size_range
        
        self.ink_color = [
            (15, 15, 15),
            (35, 40, 70),
            (85, 40, 35),
            (110, 30, 35),
            (130, 95, 30),
        ]

    @staticmethod
    def _clamp(value, low, high):
        return max(low, min(high, value))

    @staticmethod
    def _linspace_int(start, end, count):
        if count <= 1:
            return [int(start)]
        step = (end - start) / (count - 1)
        return [int(start + i * step) for i in range(count)]

    def __call__(self, img):
        if random.random() > self.p:
            return img
        
        w, h = img.size
        ink_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ink_layer)
        
        base_color = random.choice(self.ink_color)
        alpha = random.randint(130, 205)
        ink_rgba = (*base_color, alpha)
        
        edge = random.choice([0, 1, 2, 3])
        max_allowed = max(2, int(min(w, h) * 0.22))
        requested_min, requested_max = self.int_size_range
        requested_min = max(1, int(requested_min))
        requested_max = max(requested_min, int(requested_max))
        size_max = min(requested_max, max_allowed)
        size_min = min(requested_min, size_max)
        base_size = random.randint(size_min, size_max)
        
        points = []
        num_points = random.randint(6, 14)

        if edge in (0, 2):
            axis_len = w
        else:
            axis_len = h

        span_len = random.randint(max(8, int(axis_len * 0.35)), max(8, int(axis_len * 0.85)))
        span_len = min(span_len, axis_len)
        start = random.randint(0, max(0, axis_len - span_len))
        end = start + span_len
        coords = self._linspace_int(start, end, num_points)

        def depth_with_jitter():
            jitter = random.randint(-max(1, base_size // 3), max(1, base_size // 3))
            return self._clamp(base_size + jitter, 1, max_allowed)
        
        if edge == 0:  # Top edge
            points.append((start, 0))
            points.append((end, 0))
            for x in reversed(coords):
                points.append((x, depth_with_jitter()))
        elif edge == 1:  # Right edge
            points.append((w, start))
            points.append((w, end))
            for y in reversed(coords):
                points.append((w - depth_with_jitter(), y))
            
        elif edge == 2:  # Bottom edge
            points.append((end, h))
            points.append((start, h))
            for x in coords:
                points.append((x, h - depth_with_jitter()))
        else:  # Left edge
            points.append((0, end))
            points.append((0, start))
            for y in coords:
                points.append((depth_with_jitter(), y))
            
        draw.polygon(points, fill=ink_rgba)
        
        splatter_count = random.randint(1, 6)
        for _ in range(splatter_count):
            if edge in (0, 2):
                sp_x = random.randint(start, end)
                if edge == 0:
                    sp_y = random.randint(0, min(h - 1, base_size * 2))
                else:
                    sp_y = random.randint(max(0, h - base_size * 2), h - 1)
            else:
                sp_y = random.randint(start, end)
                if edge == 1:
                    sp_x = random.randint(max(0, w - base_size * 2), w - 1)
                else:
                    sp_x = random.randint(0, min(w - 1, base_size * 2))
            sp_r = random.randint(1, 3)
            draw.ellipse((sp_x - sp_r, sp_y - sp_r, sp_x + sp_r, sp_y + sp_r), fill=ink_rgba)
                
        ink_layer = ink_layer.filter(ImageFilter.GaussianBlur(radius=1.1))
        
        result = img.convert('RGBA')
        result = Image.alpha_composite(result, ink_layer)
        return result.convert('RGB')
    
    def __repr__(self):
        return f"{self.__class__.__name__}(p={self.p})"