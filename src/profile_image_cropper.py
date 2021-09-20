from math import radians

from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.vector import Vector
from kivy.graphics.transformation import Matrix
from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty, StringProperty

Builder.load_file('src/profile_image_cropper.kv')


class ProfileImageCropper(RelativeLayout):
    # The minimum zoom
    zoom_min = NumericProperty(1)
    # The maximum zoom
    zoom_max = NumericProperty(2)
    # The source of the image
    source = StringProperty('')
    # How quickly to zoom in / out on a scroll
    zoom_delta = NumericProperty(0.05)

    def on_zoom_min(self, instance, zoom):
        self.ids.scatter.scale_min = self.zoom_min

    def on_zoom_max(self, instance, zoom):
        self.ids.scatter.scale_max = self.zoom_max

    def on_source(self, instance, source):
        self.ids.scatter.source = self.source

    def on_zoom_delta(self, instance, delta):
        self.ids.scatter.zoom_delta = self.zoom_delta

    # def on_touch_down(self, touch):
    #     if not self.collide_point(*touch.pos):
    #         return
    #     return super().on_touch_down(touch)

    def reset(self):
        self.ids.scatter.reset()

    def get_image_crop(self):
        return self.ids.scatter.get_image_crop()


class CircularProfileImageCropper(ProfileImageCropper):
    pass


# This is a internal class used by the ProfileImageCropper. It will not
# Function correctly independently, so please do not do so.
class ScatterCrop(ScatterLayout):
    image_width = NumericProperty(1)
    image_height = NumericProperty(1)
    image_size = ReferenceListProperty(image_width, image_height)
    image_x = NumericProperty(0)
    image_y = NumericProperty(0)
    image_pos = ReferenceListProperty(image_x, image_y)

    crop_width = NumericProperty(0)
    crop_height = NumericProperty(0)
    crop_size = ReferenceListProperty(crop_width, crop_height)
    crop_x = NumericProperty(0)
    crop_y = NumericProperty(0)
    crop_pos = ReferenceListProperty(crop_x, crop_y)
    frame_width = NumericProperty(0)
    frame_height = NumericProperty(0)
    frame_size = ReferenceListProperty(frame_width, frame_height)

    texture = ObjectProperty(None)
    source = StringProperty(None)

    zoom_delta = NumericProperty(0.05)

    def on_touch_down(self, touch):
        result = super().on_touch_down(touch)
        if result:
            if touch.button == 'scrollup':
                self.apply_image_transform(scale=self.clamp_scale(1 - self.zoom_delta), anchor=(touch.x, touch.y))
            elif touch.button == 'scrolldown':
                self.apply_image_transform(scale=self.clamp_scale(1 + self.zoom_delta), anchor=(touch.x, touch.y))
        return result

    def clamp_scale(self, scale):
        new_scale = scale * self.scale
        if new_scale < self.scale_min:
            scale = self.scale_min / self.scale
        elif new_scale > self.scale_max:
            scale = self.scale_max / self.scale
        return scale

    def transform_with_touch(self, touch):
        # just do a simple one finger drag
        changed = False
        if len(self._touches) == self.translation_touches:
            # _last_touch_pos has last pos in correct parent space,
            # just like incoming touch
            dx = (touch.x - self._last_touch_pos[touch][0]) * self.do_translation_x
            dy = (touch.y - self._last_touch_pos[touch][1]) * self.do_translation_y
            dx = dx / self.translation_touches
            dy = dy / self.translation_touches
            self.apply_image_transform(x=dx, y=dy)
            changed = True

        if len(self._touches) == 1:
            # If we only have one touch, we want to scale on a scroll
            return changed

        # we have more than one touch... list of last known pos
        points = [Vector(self._last_touch_pos[t]) for t in self._touches if t is not touch]
        # add current touch last
        points.append(Vector(touch.pos))

        # we only want to transform if the touch is part of the two touches
        # farthest apart! So first we find anchor, the point to transform
        # around as another touch farthest away from current touch's pos
        anchor = max(points[:-1], key=lambda p: p.distance(touch.pos))

        # now we find the touch farthest away from anchor, if its not the
        # same as touch. Touch is not one of the two touches used to transform
        farthest = max(points, key=anchor.distance)
        if farthest is not points[-1]:
            return changed

        # ok, so we have touch, and anchor, so we can actually compute the
        # transformation
        old_line = Vector(*touch.ppos) - anchor
        new_line = Vector(*touch.pos) - anchor
        if not old_line.length():  # div by zero
            return changed

        angle = radians(new_line.angle(old_line)) * self.do_rotation
        if angle:
            changed = True

        if self.do_scale:
            scale = new_line.length() / old_line.length()
            self.apply_image_transform(scale=self.clamp_scale(scale), anchor=anchor)
            changed = True
        return changed

    def apply_image_transform(self, x=0, y=0, scale=1, post_multiply=False, anchor=(0, 0)):
        # Test if the x move is valid
        t = Matrix()
        t = t.translate(x, 0, 0)

        if not self.test_valid(t.multiply(self.transform)):
            x = 0

        # Test if the y move is valid
        t = Matrix()
        t = t.translate(0, y, 0)

        if not self.test_valid(t.multiply(self.transform)):
            y = 0

        # Test if the scale is valid
        t = Matrix().translate(anchor[0], anchor[1], 0)
        t = t.scale(scale, scale, scale)
        t = t.multiply(Matrix().translate(-anchor[0], -anchor[1], 0))

        if not self.test_valid(t.multiply(self.transform)):
            scale = 1

        # Compile final matrix
        t = Matrix().translate(anchor[0], anchor[1], 0)
        t = t.translate(x, y, 0)
        t = t.scale(scale, scale, scale)
        t = t.multiply(Matrix().translate(-anchor[0], -anchor[1], 0))

        if post_multiply:
            self.transform = self.transform.multiply(t)
        else:
            self.transform = t.multiply(self.transform)

    def test_valid(self, matrix):
        crop_x, crop_y = (self.width - self.crop_width) / 2, (self.height - self.crop_height) / 2
        x, y, z = matrix.transform_point(self.image_x, self.image_y, 0)
        mx, my, mz = matrix.transform_point(self.image_x + self.image_width, self.image_y + self.image_height, 0)

        if x > crop_x:
            return False
        if y > crop_y:
            return False
        if mx < crop_x + self.crop_width:
            return False
        if my < crop_y + self.crop_height:
            return False
        return True

    def on_texture(self, instance, value):
        self.calculate()
        self.reset()

    def on_size(self, *args):
        self.calculate()

    def reset(self):
        self.matrix = Matrix()

    def calculate(self):
        if 'image' not in self.ids or self.ids.image.texture is None:
            return
        width, height = self.ids.image.texture.size
        frame_width, frame_height = self.width, self.height
        if width > height:
            self.image_width = frame_width
            self.image_height = height / width * frame_height
            self.crop_size = self.image_height, self.image_height
            self.frame_size = frame_width, frame_width
            self.image_y = (self.height - self.image_height) / 2
        else:
            self.image_width = width / height * frame_width
            self.image_height = frame_height
            self.frame_size = frame_height, frame_height
            self.crop_size = self.image_width, self.image_width
            self.image_x = (self.width - self.image_width) / 2

    def get_image_crop(self):
        x, y, z = self.transform.transform_point(self.image_x, self.image_y, 0)
        mx, my, mz = self.transform.transform_point(self.image_x + self.image_width, self.image_y + self.image_height, 0)
        ccenx, cceny = (self.width - self.crop_width) / 2 + self.crop_width / 2, (self.height - self.crop_height) / 2 + self.crop_height / 2

        cx, cy = (self.width - self.crop_width) / 2, (self.height - self.crop_height) / 2
        cmx, cmy = cx + self.crop_width, cy + self.crop_height

        cw = int(round(self.texture.width * ((cmx - cx) / (mx - x))))
        ch = int(round(self.texture.height * ((cmy - cy) / (my - y))))
        cenx, ceny = int(round((ccenx - x) * (self.texture.width / (mx - x)))), int(round((cceny - y) * (self.texture.height / (my - y))))

        return cw, ch, cenx, ceny


class CircularScatterCrop(ScatterLayout):
    image_width = NumericProperty(1)
    image_height = NumericProperty(1)
    image_size = ReferenceListProperty(image_width, image_height)
    image_x = NumericProperty(0)
    image_y = NumericProperty(0)
    image_pos = ReferenceListProperty(image_x, image_y)

    crop_width = NumericProperty(0)
    crop_height = NumericProperty(0)
    crop_size = ReferenceListProperty(crop_width, crop_height)
    crop_x = NumericProperty(0)
    crop_y = NumericProperty(0)
    crop_pos = ReferenceListProperty(crop_x, crop_y)
    frame_width = NumericProperty(0)
    frame_height = NumericProperty(0)
    frame_size = ReferenceListProperty(frame_width, frame_height)

    texture = ObjectProperty(None)
    source = StringProperty(None)

    zoom_delta = NumericProperty(0.05)

    def on_touch_down(self, touch):
        result = super().on_touch_down(touch)
        if result:
            if touch.button == 'scrollup':
                self.apply_image_transform(scale=self.clamp_scale(1 - self.zoom_delta), anchor=(touch.x, touch.y))
            elif touch.button == 'scrolldown':
                self.apply_image_transform(scale=self.clamp_scale(1 + self.zoom_delta), anchor=(touch.x, touch.y))
        return result

    def clamp_scale(self, scale):
        new_scale = scale * self.scale
        if new_scale < self.scale_min:
            scale = self.scale_min / self.scale
        elif new_scale > self.scale_max:
            scale = self.scale_max / self.scale
        return scale

    def transform_with_touch(self, touch):
        # just do a simple one finger drag
        changed = False
        if len(self._touches) == self.translation_touches:
            # _last_touch_pos has last pos in correct parent space,
            # just like incoming touch
            dx = (touch.x - self._last_touch_pos[touch][0]) * self.do_translation_x
            dy = (touch.y - self._last_touch_pos[touch][1]) * self.do_translation_y
            dx = dx / self.translation_touches
            dy = dy / self.translation_touches
            self.apply_image_transform(x=dx, y=dy)
            changed = True

        if len(self._touches) == 1:
            # If we only have one touch, we want to scale on a scroll
            return changed

        # we have more than one touch... list of last known pos
        points = [Vector(self._last_touch_pos[t]) for t in self._touches if t is not touch]
        # add current touch last
        points.append(Vector(touch.pos))

        # we only want to transform if the touch is part of the two touches
        # farthest apart! So first we find anchor, the point to transform
        # around as another touch farthest away from current touch's pos
        anchor = max(points[:-1], key=lambda p: p.distance(touch.pos))

        # now we find the touch farthest away from anchor, if its not the
        # same as touch. Touch is not one of the two touches used to transform
        farthest = max(points, key=anchor.distance)
        if farthest is not points[-1]:
            return changed

        # ok, so we have touch, and anchor, so we can actually compute the
        # transformation
        old_line = Vector(*touch.ppos) - anchor
        new_line = Vector(*touch.pos) - anchor
        if not old_line.length():  # div by zero
            return changed

        angle = radians(new_line.angle(old_line)) * self.do_rotation
        if angle:
            changed = True

        if self.do_scale:
            scale = new_line.length() / old_line.length()
            self.apply_image_transform(scale=self.clamp_scale(scale), anchor=anchor)
            changed = True
        return changed

    def apply_image_transform(self, x=0, y=0, scale=1, post_multiply=False, anchor=(0, 0)):
        # Test if the x move is valid
        t = Matrix()
        t = t.translate(x, 0, 0)

        if not self.test_valid(t.multiply(self.transform)):
            x = 0

        # Test if the y move is valid
        t = Matrix()
        t = t.translate(0, y, 0)

        if not self.test_valid(t.multiply(self.transform)):
            y = 0

        # Test if the scale is valid
        t = Matrix().translate(anchor[0], anchor[1], 0)
        t = t.scale(scale, scale, scale)
        t = t.multiply(Matrix().translate(-anchor[0], -anchor[1], 0))

        if not self.test_valid(t.multiply(self.transform)):
            scale = 1

        # Compile final matrix
        t = Matrix().translate(anchor[0], anchor[1], 0)
        t = t.translate(x, y, 0)
        t = t.scale(scale, scale, scale)
        t = t.multiply(Matrix().translate(-anchor[0], -anchor[1], 0))

        if post_multiply:
            self.transform = self.transform.multiply(t)
        else:
            self.transform = t.multiply(self.transform)

    def test_valid(self, matrix):
        crop_x, crop_y = (self.width - self.crop_width) / 2, (self.height - self.crop_height) / 2
        x, y, z = matrix.transform_point(self.image_x, self.image_y, 0)
        mx, my, mz = matrix.transform_point(self.image_x + self.image_width, self.image_y + self.image_height, 0)

        if x > crop_x:
            return False
        if y > crop_y:
            return False
        if mx < crop_x + self.crop_width:
            return False
        if my < crop_y + self.crop_height:
            return False
        return True

    def on_texture(self, instance, value):
        self.calculate()
        self.reset()

    def on_size(self, *args):
        self.calculate()

    def reset(self):
        self.matrix = Matrix()

    def calculate(self):
        if 'image' not in self.ids or self.ids.image.texture is None:
            return
        width, height = self.ids.image.texture.size
        frame_width, frame_height = self.width, self.height
        if width > height:
            self.image_width = frame_width
            self.image_height = height / width * frame_height
            self.crop_size = self.image_height, self.image_height
            self.frame_size = frame_width, frame_width
            self.image_y = (self.height - self.image_height) / 2
        else:
            self.image_width = width / height * frame_width
            self.image_height = frame_height
            self.frame_size = frame_height, frame_height
            self.crop_size = self.image_width, self.image_width
            self.image_x = (self.width - self.image_width) / 2

    def get_image_crop(self):
        x, y, z = self.transform.transform_point(self.image_x, self.image_y, 0)
        mx, my, mz = self.transform.transform_point(self.image_x + self.image_width, self.image_y + self.image_height, 0)
        ccenx, cceny = (self.width - self.crop_width) / 2 + self.crop_width / 2, (self.height - self.crop_height) / 2 + self.crop_height / 2

        cx, cy = (self.width - self.crop_width) / 2, (self.height - self.crop_height) / 2
        cmx, cmy = cx + self.crop_width, cy + self.crop_height

        cw = int(round(self.texture.width * ((cmx - cx) / (mx - x))))
        ch = int(round(self.texture.height * ((cmy - cy) / (my - y))))
        cenx, ceny = int(round((ccenx - x) * (self.texture.width / (mx - x)))), int(round((cceny - y) * (self.texture.height / (my - y))))

        return cw, ch, cenx, ceny
