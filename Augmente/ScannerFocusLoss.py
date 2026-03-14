import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

class RandomScannerFocusLoss:
    """
    Zaawansowana symulacja utraty ostrości skanera (WSI).
    - Mniejsze, rotowane elipsy dla bardziej organicznych kształtów.
    - Zmienna intensywność maski (rozmycie jest nierównomierne).
    - Oddzielny feathering (2-8px).
    - Opcjonalny, lekki spadek ostrości całego tła.
    """
    def __init__(
        self,
        p=0.5,
        local_blur_range=(2.5, 6.0),
        blur_radius_range=None,
        global_blur_p=0.3,
        global_blur_range=(0.3, 1.0),
        min_mask_coverage=0.12,
        mask_generation_tries=5,
        blob_intensity_range=(140, 255),
        feather_range=(1.5, 5.0),
        coverage_alpha_threshold=32,
        blur_strength_multiplier=1.6,
    ):
        self.p = p
        # Backward compatibility with older notebook parameter name.
        if blur_radius_range is not None:
            local_blur_range = blur_radius_range
        self.local_blur_range = local_blur_range
        self.global_blur_p = global_blur_p           # Szansa na lekki globalny defocus
        self.global_blur_range = global_blur_range
        self.min_mask_coverage = min_mask_coverage
        self.mask_generation_tries = mask_generation_tries
        self.blob_intensity_range = blob_intensity_range
        self.feather_range = feather_range
        self.coverage_alpha_threshold = coverage_alpha_threshold
        self.blur_strength_multiplier = blur_strength_multiplier
        
    def __call__(self, img):
        if random.random() > self.p:
            return img
            
        w, h = img.size
        
        # 1. Opcjonalny lekki globalny blur (np. delikatnie nieostre całe szkiełko)
        base_img = img
        if random.random() < self.global_blur_p:
            g_blur = random.uniform(*self.global_blur_range)
            base_img = base_img.filter(ImageFilter.GaussianBlur(radius=g_blur))
            
        # 2. Mocno rozmyta wersja do wypełnienia naszej organicznej maski
        l_blur = random.uniform(*self.local_blur_range) * self.blur_strength_multiplier
        heavily_blurred_img = base_img.filter(ImageFilter.GaussianBlur(radius=l_blur))
        
        # 3-5. Generujemy maskę i ponawiamy jeśli efekt jest zbyt słaby.
        total_pixels = float(w * h)
        mask = None

        for _ in range(max(1, self.mask_generation_tries)):
            mask = Image.new('L', (w, h), 0)

            # 4. Generowanie organicznej plamy z rotowanych elips o różnej szarości
            num_blobs = random.randint(4, 9)
            base_x = random.randint(w // 6, max(w // 6, (5 * w) // 6 - 1))
            base_y = random.randint(h // 6, max(h // 6, (5 * h) // 6 - 1))

            for _ in range(num_blobs):
                blob_w = random.randint(max(2, w // 7), max(3, w // 2))
                blob_h = random.randint(max(2, h // 7), max(3, h // 2))

                intensity = random.randint(*self.blob_intensity_range)

                temp_size = max(blob_w, blob_h) * 2
                temp_mask = Image.new('L', (temp_size, temp_size), 0)
                temp_draw = ImageDraw.Draw(temp_mask)

                ex1 = temp_size // 2 - blob_w // 2
                ey1 = temp_size // 2 - blob_h // 2
                temp_draw.ellipse([ex1, ey1, ex1 + blob_w, ey1 + blob_h], fill=intensity)

                angle = random.randint(0, 360)
                temp_mask = temp_mask.rotate(angle, expand=False, fillcolor=0)

                offset_x = random.randint(-w // 3, w // 3)
                offset_y = random.randint(-h // 3, h // 3)
                paste_x = base_x + offset_x - temp_size // 2
                paste_y = base_y + offset_y - temp_size // 2

                layer = Image.new('L', (w, h), 0)
                layer.paste(temp_mask, (paste_x, paste_y))
                mask = ImageChops.lighter(mask, layer)

            feather_radius = random.uniform(*self.feather_range)
            mask = mask.filter(ImageFilter.GaussianBlur(radius=feather_radius))

            # Usuwamy bardzo slabe alpha i podbijamy kontrast maski,
            # zeby blur byl lokalny i wyrazny.
            mask = mask.point(
                lambda x: 0
                if x < 24
                else min(255, int((x - 24) * 2.4))
            )

            hist = mask.histogram()
            strong_pixels = sum(hist[self.coverage_alpha_threshold:])
            coverage = strong_pixels / total_pixels
            if coverage >= self.min_mask_coverage:
                break
        
        # 6. Kompozycja całości
        result = Image.composite(heavily_blurred_img, base_img, mask)
        
        return result

    def __repr__(self):
        return f"{self.__class__.__name__}(p={self.p})"