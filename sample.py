from os.path import expanduser

from kivy.config import Config
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')
Config.set('graphics', 'left', '256')
Config.set('graphics', 'top', '256')


from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.relativelayout import RelativeLayout


class SampleWindow(RelativeLayout):
    image_source = StringProperty('')

    def on_kv_post(self, base_widget):
        # What path can the user not go up from?
        self.ids.file_chooser.rootpath = expanduser('~')
        # What starting path do you want to display the user?
        self.ids.file_chooser.path = expanduser('~\\Pictures')

    def crop_image(self, selections):
        self.image_source = selections[0]
        self.ids.cropper.reset()
        self.ids.cropper.source = self.image_source
        self.ids.circle_cropper.reset()
        self.ids.circle_cropper.source = self.image_source

    def update_image(self, cw, ch, cx, cy):
        self.ids.preview.update_crop_values(cw, ch, cx, cy)
        self.ids.preview.source = self.image_source

    def update_circle_image(self, cw, ch, cx, cy):
        self.ids.circle_preview.update_crop_values(cw, ch, cx, cy)
        self.ids.circle_preview.source = self.image_source


class SampleApp(App):
    def build(self):
        return SampleWindow()


if __name__ == "__main__":
    SampleApp().run()
