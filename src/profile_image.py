from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.image import AsyncImage
from kivy.lang import Builder

Builder.load_file('src/profile_image.kv')


class ProfileImage(AsyncImage):
    # The display variables are
    display_width = NumericProperty(0)
    display_height = NumericProperty(0)
    display_size = ReferenceListProperty(display_width, display_height)

    display_x = NumericProperty(0)
    display_y = NumericProperty(0)
    display_pos = ReferenceListProperty(display_x, display_y)

    def __init__(self, **kwargs):
        self.tw, self.th = 1, 1
        self.cw, self.ch = 100, 100
        self.cx, self.cy = 50, 50
        super().__init__(**kwargs)

    """
    @:param cw The width of the image to show.
    @:param ch The height of the image to show.
    @:param cx The center_x coordinate to use.
    @:param cy The center_y coordinate to use.

    Example, to show an entire image that is 100 x 100
    You would use the values, 100, 100, 50, 50
    to show the entire size and center on the center.
    """

    def update_crop_values(self, cw, ch, cx, cy):
        self.cw, self.ch = cw, ch
        self.cx, self.cy = cx, cy
        self.calculate_image_size()

    def on_texture(self, instance, value):
        if self.texture is None:
            return
        self.tw = self.texture.width
        self.th = self.texture.height
        self.calculate_image_size()

    def on_size(self, *args):
        self.calculate_image_size()

    def on_pos(self, *args):
        self.calculate_image_size()

    def calculate_image_size(self):
        scale = self.width / self.cw
        self.display_width = self.tw * scale
        self.display_height = self.th * scale
        self.display_x = self.x + -(self.cx - self.cw / 2) * scale
        self.display_y = self.y + -(self.cy - self.ch / 2) * scale