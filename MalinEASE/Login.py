from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton

Window.size = (360, 640)

KV = '''
ScreenManager:
    LoginPage:
    ChoicePage:
    SignInPage:

<LoginPage>:
    name: 'login'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDLabel:
            text: 'Malin-EASE'
            halign: 'center'
            font_style: 'H4'

        MDTextField:
            id: section_input
            hint_text: 'Enter your section'
            mode: 'rectangle'

        MDRaisedButton:
            text: 'Submit'
            halign: 'center'
            on_press: root.submit()
            

<ChoicePage>:
    name: 'choice'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDLabel:
            id: choice_label
            halign: 'center'
            font_style: 'H4'

        MDLabel:
            text: 'Are you a teacher or a student?'
            halign: 'center'

        MDRaisedButton:
            text: 'Teacher'
            halign: 'center'
            on_press: root.signin('Teacher')

        MDRaisedButton:
            text: 'Student'
            halign: 'center'
            on_press: root.signin('Student')


<SignInPage>:
    name: 'signin'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDLabel:
            id: signin_label
            halign: 'center'
            font_style: 'H4'

        MDTextField:
            id: id_input
            hint_text: 'Enter your ID number'
            mode: 'rectangle'

        MDRaisedButton:
            text: 'Sign In'
            on_press: root.signin()
'''

class LoginPage(Screen):
    def submit(self):
        section = self.ids.section_input.text.strip()
        if section:
            self.manager.get_screen('choice').ids.choice_label.text = f'Your are in {section}'
            self.manager.current = 'choice'

class ChoicePage(Screen):
    def signin(self, role):
        self.manager.get_screen('signin').ids.signin_label.text = f'Sign In as {role}'
        self.manager.current = 'signin'

class SignInPage(Screen):
    def signin(self):
        id_number = self.ids.id_input.text.strip()
        if id_number:
            self.show_popup(id_number)

    def show_popup(self, id_number):
        dialog = MDDialog(
            title="Sign In Successful",
            text=f"You have signed in with ID: {id_number}",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )
        dialog.open()

class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginPage(name='login'))
        sm.add_widget(ChoicePage(name='choice'))
        sm.add_widget(SignInPage(name='signin'))
        return Builder.load_string(KV)

if __name__ == '__main__':
    MyApp().run()
