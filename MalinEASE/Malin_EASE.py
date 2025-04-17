from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from database import get_student_info, get_teacher_info, section_exists  # Import the new function

Window.size = (360, 640)

KV = '''
ScreenManager:
    LoginPage:
    ChoicePage:
    SignInPage:
    StudentHomePage:
    TeacherHomePage:
    CleanerListPage:
    VoucherShopPage:
    RatingFormPage:
    VoucherApprovalPage:
    StudentPointsPage:

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

<StudentHomePage>:
    name: 'student_home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDLabel:
            id: student_info
            halign: 'center'
            font_style: 'H5'

        MDLabel:
            id: student_points
            halign: 'center'
            font_style: 'H6'

        MDRaisedButton:
            text: 'Cleaner List'
            on_press: app.root.current = 'cleaner_list'

        MDRaisedButton:
            text: 'Voucher Shop'
            on_press: app.root.current = 'voucher_shop'

        MDRaisedButton:
            text: 'Rate Cleaners'
            on_press: app.root.current = 'rating_form'

<TeacherHomePage>:
    name: 'teacher_home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDLabel:
            id: teacher_info
            halign: 'center'
            font_style: 'H5'

        MDRaisedButton:
            text: 'Cleaner List'
            on_press: app.root.current = 'cleaner_list'

        MDRaisedButton:
            text: 'Voucher Approval'
            on_press: app.root.current = 'voucher_approval'

        MDRaisedButton:
            text: 'Student Points'
            on_press: app.root.current = 'student_points'

<CleanerListPage>:
    name: 'cleaner_list'
    BoxLayout:
        orientation: 'vertical'
        MDLabel:
            text: 'Cleaner List (Placeholder)'
            halign: 'center'

<VoucherShopPage>:
    name: 'voucher_shop'
    BoxLayout:
        orientation: 'vertical'
        MDLabel:
            text: 'Voucher Shop (Placeholder)'
            halign: 'center'

<RatingFormPage>:
    name: 'rating_form'
    BoxLayout:
        orientation: 'vertical'
        MDLabel:
            text: 'Rate Cleaners (Placeholder)'
            halign: 'center'

<VoucherApprovalPage>:
    name: 'voucher_approval'
    BoxLayout:
        orientation: 'vertical'
        MDLabel:
            text: 'Voucher Approval (Placeholder)'
            halign: 'center'

<StudentPointsPage>:
    name: 'student_points'
    BoxLayout:
        orientation: 'vertical'
        MDLabel:
            text: 'Student Points (Placeholder)'
            halign: 'center'
'''


# --- Screens ---
class LoginPage(Screen):
    def submit(self):
        section = self.ids.section_input.text.strip()
        if section:
            if section_exists(section):  # This uses the case-insensitive check
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
    dialog = None

    def on_pre_enter(self, *args):
        self.ids.signin_label.text = f"Sign In as {self.role}"

    def show_dialog(self, text):
        if not self.dialog:
            self.dialog = MDDialog(
                text=text,
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
        else:
            self.dialog.text = text
        self.dialog.open()

    def signin(self):
        id_number = self.ids.id_input.text.strip()
        if not id_number:
            self.show_dialog("Please enter your ID number.")
            return

        app = MDApp.get_running_app()

        if self.role == "Student":
            student = get_student_info(id_number)
            if student:
                name, section, points = student
                app.root.get_screen('student_home').ids.student_info.text = f"{name} | Section: {section}"
                app.root.get_screen('student_home').ids.student_points.text = f"Points: {points}"
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


class StudentHomePage(Screen):
    pass


class TeacherHomePage(Screen):
    pass


class CleanerListPage(Screen):
    pass


class VoucherShopPage(Screen):
    pass


class RatingFormPage(Screen):
    pass


class VoucherApprovalPage(Screen):
    pass


class StudentPointsPage(Screen):
    pass


# --- App ---
class MyApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    MyApp().run()
