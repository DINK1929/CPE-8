from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton

from database import get_student_info, get_teacher_info

Window.size = (360, 640)

# --- Section Check Function ---
def section_exists(input_section):
    input_section = input_section.strip().lower()
    import sqlite3
    conn = sqlite3.connect("malin_ease.db")
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT section FROM students")
    student_sections = {row[0].lower() for row in cursor.fetchall()}

    cursor.execute("SELECT DISTINCT section FROM teachers")
    teacher_sections = {row[0].lower() for row in cursor.fetchall()}

    conn.close()
    return input_section in student_sections.union(teacher_sections)

def generate_cleaners_list(self):
    import sqlite3
    conn = sqlite3.connect("malin_ease.db")
    cursor = conn.cursor()

    # Get students of the current section
    cursor.execute("SELECT id, name FROM students WHERE lower(section) = ?", (self.section.lower(),))
    students = cursor.fetchall()

        # Sort alphabetically by name
    students.sort(key=lambda x: x[1])

        # Assign to days (Monday to Friday)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for i, (student_id, _) in enumerate(students):
        assigned_day = days[i % 5]
        cursor.execute("UPDATE students SET cleaning_day = ? WHERE id = ?", (assigned_day, student_id))

    conn.commit()
    conn.close()

# --- Kivy UI ---
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

<StudentHomePage>:
    name: 'student_home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            MDIconButton:
                icon: "logout"
                on_release: app.confirm_logout()
                pos_hint: {"center_y": 0.5}

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

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            MDIconButton:
                icon: "logout"
                on_release: app.confirm_logout()
                pos_hint: {"center_y": 0.5}

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
        spacing: dp(10)

        MDTopAppBar:
            title: "Cleaner List"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        ScrollView:
            MDBoxLayout:
                id: cleaners_list
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                adaptive_height: True

<VoucherShopPage>:
    name: 'voucher_shop'
    BoxLayout:
        orientation: 'vertical'
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.05}
            on_release: app.root.current = 'student_home'

        MDLabel:
            text: 'Voucher Shop (Placeholder)'
            halign: 'center'

<RatingFormPage>:
    name: 'rating_form'
    BoxLayout:
        orientation: 'vertical'
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.05}
            on_release: app.root.current = 'student_home'

        MDLabel:
            text: 'Rate Cleaners (Placeholder)'
            halign: 'center'

<VoucherApprovalPage>:
    name: 'voucher_approval'
    BoxLayout:
        orientation: 'vertical'
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.05}
            on_release: app.root.current = 'teacher_home'

        MDLabel:
            text: 'Voucher Approval (Placeholder)'
            halign: 'center'

<StudentPointsPage>:
    name: 'student_points'
    BoxLayout:
        orientation: 'vertical'
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.05}
            on_release: app.root.current = 'teacher_home'

        MDLabel:
            text: 'Student Points (Placeholder)'
            halign: 'center'
'''

# --- Screen Classes ---
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
                self.show_error("Section not found in the database.")
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

    def show_dialog(self, text):
        if not hasattr(self, 'dialog') or not self.dialog:
            self.dialog = MDDialog(
                text=text,
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
        else:
            self.dialog.text = text
        self.dialog.open()

class StudentHomePage(Screen): pass
class TeacherHomePage(Screen): pass

class CleanerListPage(Screen):
    def on_enter(self):
        self.display_cleaners()

    def display_cleaners(self):
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.list import OneLineListItem

        app = MDApp.get_running_app()
        section = app.section

        # Fetch students assigned to cleaning days from the database
        import sqlite3
        conn = sqlite3.connect("malin_ease.db")
        cursor = conn.cursor()

        # Get students assigned to each cleaning day
        cursor.execute("SELECT name, cleaning_day FROM students WHERE lower(section) = ?", (section.lower(),))
        students = cursor.fetchall()

        # Organize students into groups based on cleaning day
        cleaners_by_day = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
        for name, cleaning_day in students:
            cleaners_by_day[cleaning_day].append(name)

        conn.close()

        self.ids.cleaners_list.clear_widgets()
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        # Display the students by their assigned cleaning days
        for day in weekdays:
            day_card = MDCard(
                orientation='vertical',
                size_hint=(1, None),
                padding=dp(10),
                spacing=dp(5),
                elevation=4,
                radius=[15, 15, 15, 15],
                md_bg_color=(1, 1, 1, 1)
            )
            day_card.bind(minimum_height=day_card.setter('height'))

            day_title = MDLabel(
                text=day,
                bold=True,
                theme_text_color='Primary',
                font_style='H6',
                size_hint_y=None,
                height=dp(30)
            )
            day_card.add_widget(day_title)

            # If there are students for this day, display their names
            students_for_day = cleaners_by_day.get(day, [])
            if students_for_day:
                for name in students_for_day:
                    day_card.add_widget(OneLineListItem(text=name))
            else:
                day_card.add_widget(OneLineListItem(text="No students assigned"))

            self.ids.cleaners_list.add_widget(day_card)

    def go_back(self):
        app = MDApp.get_running_app()
        if app.root.get_screen('signin').role == "Student":
            app.root.current = 'student_home'
        else:
            app.root.current = 'teacher_home'

class VoucherShopPage(Screen): pass
class RatingFormPage(Screen): pass
class VoucherApprovalPage(Screen): pass
class StudentPointsPage(Screen): pass

class MalinEASEApp(MDApp):
    section = ""
    dialog = None

    def build(self):
        return Builder.load_string(KV)

    def confirm_logout(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Are you sure you want to log out?",
                buttons=[
                    MDFlatButton(text="No", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="Yes", on_release=self.logout)
                ]
            )
        self.dialog.open()

    def logout(self, *args):
        self.dialog.dismiss()
        self.root.current = 'login'

    def get_cleaner_groups(self, section):
        import sqlite3
        conn = sqlite3.connect("malin_ease.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students WHERE lower(section) = ?", (section.lower(),))
        names = [row[0] for row in cursor.fetchall()]
        conn.close()

        names.sort()
        groups = [[] for _ in range(5)]
        for i, name in enumerate(names):
            groups[i % 5].append(name)
        return groups

if __name__ == '__main__':
    MalinEASEApp().run()
