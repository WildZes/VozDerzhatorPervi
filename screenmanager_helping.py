from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivymd.uix.pickers import MDDatePicker


Builder.load_file('main.kv')
Builder.load_file('vd.kv')


class MainScreen(Screen):
    btn = ObjectProperty(None)


class VDScreen(Screen):
    btn = ObjectProperty(None)

    def select_date(self):
        picker = MDDatePicker(mode="range")
        picker.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        picker.open()


    def on_save(self, instance, value, date_range):
        # print(instance, value, date_range)
        # self.root.ids.date_label.text = str(value)
        self.ids.c_date.text = f'{str(date_range[0])} - {str(date_range[-1])}'


    def on_cancel(self, instance, value):
        print(instance, value)
        # self.root.ids.c_date.text = "You Clicked Cancel"


class ScreenManagerApp(MDApp):
    def build(self):
        root = ScreenManager()
        root.add_widget(MainScreen(name='main'))
        root.add_widget(VDScreen(name='vd'))
        return root


if __name__ == '__main__':
    ScreenManagerApp().run()