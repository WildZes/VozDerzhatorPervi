from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.lang import Builder


Builder.load_file('main.kv')
Builder.load_file('vd.kv')


class MainScreen(Screen):
    btn = ObjectProperty(None)


class VDScreen(Screen):
    btn = ObjectProperty(None)


class ScreenManagerApp(App):

    def build(self):
        root = ScreenManager()
        root.add_widget(MainScreen(name='main'))
        root.add_widget(VDScreen(name='vd'))
        return root


if __name__ == '__main__':
    ScreenManagerApp().run()