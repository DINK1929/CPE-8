import requests
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
Window.size = (360, 640)
API_BASE_URL = "http://dirk.x10.mx/Malin_EASE/api.php"
# --- Section Check Function ---
def section_exists(section):
    try:
        response = requests.get(
            f"{API_BASE_URL}/verify_section",
            params={'section': section}
        )
        data = response.json()
        return data.get('exists', False)
    except Exception as e:
        print(f"Error checking section: {e}")
        return False

def get_student_info(student_id):
    try:
        response = requests.get(
            f"{API_BASE_URL}/get_student",
            params={'id': student_id}
        )
        data = response.json()
        if 'error' not in data:
            return (data['name'], data['section'], data['rating'])
        return None
    except Exception as e:
        print(f"Error fetching student info: {e}")
        return None

def get_teacher_info(teacher_id):
    try:
        response = requests.get(
            f"{API_BASE_URL}/get_teacher",
            params={'id': teacher_id}
        )
        data = response.json()
        if 'error' not in data:
            return (data['name'], data['section'])
        return None
    except Exception as e:
        print(f"Error fetching teacher info: {e}")
        return None

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

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(150)
            padding: dp(10)

            FitImage:
                source: app.logo_path
                size_hint: (0.8, 0.8)
                pos_hint: {'center_x': 0.5}

        MDLabel:
            text: 'Malin-EASE'
            halign: 'center'
            font_style: 'H4'

        MDTextField:
            id: section_input
            hint_text: 'Enter your section (ex: BSCPE 2b)'
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

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(150)
            padding: dp(10)

            FitImage:
                source: app.logo_path
                size_hint: (0.8, 0.8)
                pos_hint: {'center_x': 0.5}

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.05}
            on_release: app.root.current = 'login'

        MDLabel:
            id: choice_label
            halign: 'center'
            font_style: 'H4'

        MDLabel:
            text: 'Are you a teacher or a student?'
            halign: 'center'

        MDRaisedButton:
            text: 'Teacher'
            on_press: root.signin('Teacher')

        MDRaisedButton:
            text: 'Student'
            on_press: root.signin('Student')

<SignInPage>:
    name: 'signin'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(150)
            padding: dp(10)

            FitImage:
                source: app.logo_path
                size_hint: (0.8, 0.8)
                pos_hint: {'center_x': 0.5}

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.05}
            on_release: app.root.current = 'choice'

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
            if section_exists(section):
                app = MDApp.get_running_app()
                app.section = section
                self.manager.get_screen('choice').ids.choice_label.text = f'You are in {section}'
                self.manager.current = 'choice'
            else:
                self.show_error("Section not found.")
        else:
            self.show_error("Please enter your section.")

    def show_error(self, message):
        if not hasattr(self, 'dialog') or not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
        else:
            self.dialog.text = message
        self.dialog.open()

class ChoicePage(Screen):
    def signin(self, role):
        self.manager.get_screen('signin').ids.signin_label.text = f'Sign In as {role}'
        self.manager.get_screen('signin').role = role
        self.manager.current = 'signin'

class SignInPage(Screen):
    role = StringProperty("")

    def signin(self):
        id_number = self.ids.id_input.text.strip()
        if not id_number:
            self.show_dialog("Please enter your ID number.")
            return

        app = MDApp.get_running_app()

        if self.role == "Student":
            student = get_student_info(id_number)
            if student:
                name, section, rating = student
                app.root.get_screen('student_home').ids.student_info.text = f"{name} | Section: {section}"
                app.root.get_screen('student_home').ids.student_ratings.text = f"Ratings: {rating}"
                app.current_student_id = id_number
                app.root.current = 'student_home'
            else:
                self.show_dialog("Student not found.")

        elif self.role == "Teacher":
            teacher = get_teacher_info(id_number)
            if teacher:
                name, section = teacher
                app.root.get_screen('teacher_home').ids.teacher_info.text = f"{name} | Section: {section}"
                app.root.current = 'teacher_home'
            else:
                self.show_dialog("Teacher not found.")

    def show_dialog(self, text):
        if not hasattr(self, 'dialog') or not self.dialog:
            self.dialog = MDDialog(
                text=text,
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
        else:
            self.dialog.text = text
        self.dialog.open()

class MalinEASEApp(MDApp):
    section = StringProperty("")
    current_student_id = StringProperty("")
    logo_path = StringProperty("Malin_EASE_logo.png")

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def confirm_logout(self):
        self.dialog = MDDialog(
            text="Are you sure you want to logout?",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Logout", on_release=self.logout)
            ]
        )
        self.dialog.open()

    def logout(self, *args):
        self.dialog.dismiss()
        self.root.current = 'login'

    def change_screen(self, screen_name):
        self.root.current = screen_name


if __name__ == '__main__':
    MalinEASEApp().run()
