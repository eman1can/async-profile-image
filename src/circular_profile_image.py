from kivy.lang import Builder

from src.profile_image import ProfileImage

Builder.load_file('src/circular_profile_image.kv')


class CircularProfileImage(ProfileImage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
