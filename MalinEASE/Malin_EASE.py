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
from database import get_student_info, get_teacher_info, section_exists, create_voucher, get_pending_vouchers, approve_voucher, reject_voucher, can_purchase_voucher, get_student_vouchers

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


def change_screen(self, screen_name):
    self.root.current = screen_name


def generate_cleaners_list(self):
    import sqlite3
    conn = sqlite3.connect("malin_ease.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM students WHERE lower(section) = ?", (self.section.lower(),))
    students = cursor.fetchall()

    students.sort(key=lambda x: x[1])

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
    StudentRatingsPage:

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
            id: student_ratings
            halign: 'center'
            font_style: 'H6'

        ScrollView:
            MDBoxLayout:
                id: voucher_status_container
                orientation: 'vertical'
                spacing: dp(10)
                adaptive_height: True
                size_hint_y: None
                height: self.minimum_height

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
            text: 'Student Ratings'
            on_press: app.root.current = 'student_ratings'

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
        spacing: dp(10)

        MDTopAppBar:
            title: "Voucher Shop"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.change_screen('student_home')]]

        ScrollView:
            MDBoxLayout:
                id: voucher_container
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(20)
                adaptive_height: True

<RatingFormPage>:
    name: 'rating_form'
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)

        MDTopAppBar:
            title: "Rate Groupmates"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.change_screen('student_home')]]

        ScrollView:
            MDBoxLayout:
                id: rating_form_container
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(20)
                adaptive_height: True

<VoucherApprovalPage>:
    name: 'voucher_approval'
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)

        MDTopAppBar:
            title: "Voucher Approvals"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.change_screen('teacher_home')]]

        ScrollView:
            MDBoxLayout:
                id: voucher_approval_container
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                adaptive_height: True

<StudentRatingsPage>:  
    name: 'student_ratings'  
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.05}
            on_release: app.root.current = 'teacher_home'
            theme_text_color: "Custom"
            text_color: (0, 0, 0, 1)

        MDLabel:
            text: 'All Students Ratings'
            halign: 'center'
            font_style: 'H4'
            size_hint_y: None
            height: dp(50)
            theme_text_color: "Primary"

        ScrollView:
            MDList:
                id: student_ratings_list
                spacing: dp(10)  


'''

class VoucherStatusCard(MDCard):
    def __init__(self, voucher_id, voucher_type, status, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.height = dp(100)
        self.padding = dp(10)
        self.spacing = dp(5)
        self.elevation = 2
        self.radius = [15]

        # Set color based on status
        if status == 'approved':
            self.md_bg_color = get_color_from_hex('#4CAF50')  # Green
        elif status == 'rejected':
            self.md_bg_color = get_color_from_hex('#F44336')  # Red
        else:
            self.md_bg_color = get_color_from_hex('#FFC107')  # Yellow (pending)

        # Add first label
        self.add_widget(MDLabel(
            text=f"{voucher_type.replace('_', ' ').title()} Voucher",
            bold=True,
            halign='center',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1)
        ))

        # Add second label
        self.add_widget(MDLabel(
            text=f"Status: {status.upper()}",
            halign='center',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1)
        ))

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


class StudentHomePage(Screen):
    def on_enter(self):
        self.update_student_info()
        self.display_voucher_statuses()

    def update_student_info(self):
        app = MDApp.get_running_app()
        student = get_student_info(app.current_student_id)
        if student:
            name, section, rating = student
            self.ids.student_info.text = f"{name} | Section: {section}"
            self.ids.student_ratings.text = f"Ratings: {rating}"

    def display_voucher_statuses(self):
        app = MDApp.get_running_app()
        vouchers = get_student_vouchers(app.current_student_id)

        self.ids.voucher_status_container.clear_widgets()

        if not vouchers:
            no_vouchers = MDLabel(
                text="No voucher purchases yet",
                halign='center',
                theme_text_color='Secondary'
            )
            self.ids.voucher_status_container.add_widget(no_vouchers)
            return

        for voucher_id, voucher_type, status in vouchers:
            card = VoucherStatusCard(
                voucher_id=voucher_id,
                voucher_type=voucher_type,
                status=status
            )
            self.ids.voucher_status_container.add_widget(card)

class TeacherHomePage(Screen): pass

class CleanerListPage(Screen):
    def on_enter(self):
        self.display_cleaners()

    def display_cleaners(self):
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.list import OneLineListItem
        from kivy.metrics import dp  # <-- you forgot to import dp here!

        app = MDApp.get_running_app()
        section = app.section

        import sqlite3
        conn = sqlite3.connect("malin_ease.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name, cleaning_day FROM students WHERE lower(section) = ?", (section.lower(),))
        students = cursor.fetchall()
        conn.close()

        # Group students by cleaning day
        cleaners_by_day = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
        for name, cleaning_day in students:
            if cleaning_day in cleaners_by_day:
                cleaners_by_day[cleaning_day].append(name)

        # Clear previous widgets
        self.ids.cleaners_list.clear_widgets()

        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            # Create a card for each day
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

            # Day title
            day_title = MDLabel(
                text=day,
                bold=True,
                font_style='H6',
                theme_text_color='Primary',
                size_hint_y=None,
                height=dp(30)
            )
            day_card.add_widget(day_title)

            # Students list
            students_list = cleaners_by_day.get(day)
            if students_list:
                for name in students_list:
                    day_card.add_widget(OneLineListItem(text=name))
            else:
                day_card.add_widget(OneLineListItem(text="No students assigned"))

            # Add day card to the cleaners list container
            self.ids.cleaners_list.add_widget(day_card)


    def go_back(self):
        app = MDApp.get_running_app()
        if app.root.get_screen('signin').role == "Student":
            app.root.current = 'student_home'
        else:
            app.root.current = 'teacher_home'

class VoucherShopPage(Screen):
    def on_enter(self):
        self.display_vouchers()

    def display_vouchers(self):
        self.ids.voucher_container.clear_widgets()  # Clear previous vouchers first
        app = MDApp.get_running_app()
        student_id = app.current_student_id

        # Define available vouchers
        vouchers = [
            {
                'type': 'skip_cleaning',
                'name': 'Skip Cleaning Pass',
                'description': 'Skip cleaning next week and get automatic 5 rating points',
                'cost': 20
            }
        ]

        for voucher in vouchers:
            can_purchase = can_purchase_voucher(student_id, voucher['type'])

            # Create card
            card = MDCard(
                orientation='vertical',
                size_hint=(1, None),
                height=dp(150),
                padding=dp(15),
                spacing=dp(10),
                elevation=2
            )

            # Name label
            name_label = MDLabel(
                text=voucher['name'],
                theme_text_color='Primary',
                font_style='H6',
                size_hint_y=None,
                height=dp(30)
            )

            # Description label
            desc_label = MDLabel(
                text=voucher['description'],
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(50),
                padding=(10, 0)
            )

            # Cost label
            cost_label = MDLabel(
                text=f"Cost: {voucher['cost']} ratings",
                theme_text_color='Primary',
                size_hint_y=None,
                height=dp(20),
                bold=True
            )

            # Purchase button
            purchase_btn = MDRaisedButton(
                text="Purchase" if can_purchase else "Not enough ratings",
                disabled=not can_purchase,
                size_hint_y=None,
                height=dp(40),
                on_release=lambda x, v=voucher['type']: self.purchase_voucher(v)
            )

            # Add widgets to card
            card.add_widget(name_label)
            card.add_widget(desc_label)
            card.add_widget(cost_label)
            card.add_widget(purchase_btn)

            # Add card to voucher container
            self.ids.voucher_container.add_widget(card)

    def purchase_voucher(self, voucher_type):
        from kivymd.toast import toast
        app = MDApp.get_running_app()

        if can_purchase_voucher(app.current_student_id, voucher_type):
            create_voucher(app.current_student_id, voucher_type)
            toast("Voucher purchased! Waiting for teacher approval.")

            # Update student's rating display
            student = get_student_info(app.current_student_id)
            if student:
                name, section, rating = student
                app.root.get_screen('student_home').ids.student_ratings.text = f"Ratings: {rating}"

            # Return to home and refresh
            self.manager.current = 'student_home'
            self.manager.get_screen('student_home').display_voucher_statuses()
        else:
            toast("You don't have enough ratings for this voucher.")

class RatingFormPage(Screen):
    def on_enter(self):
        self.display_groupmates()

    def display_groupmates(self):
        self.ids.rating_form_container.clear_widgets()
        app = MDApp.get_running_app()
        current_id = app.current_student_id

        import sqlite3
        conn = sqlite3.connect("malin_ease.db")
        cursor = conn.cursor()

        cursor.execute("SELECT cleaning_day FROM students WHERE student_id = ?", (current_id,))
        result = cursor.fetchone()

        if result:
            cleaning_day = result[0]

            cursor.execute("""
                SELECT student_id, name FROM students 
                WHERE cleaning_day = ? AND student_id != ?
            """, (cleaning_day, current_id))
            groupmates = cursor.fetchall()

            self.slider_data = {}

            for sid, name in groupmates:
                card = MDCard(orientation="vertical", padding=10, size_hint_y=None)
                card.height = dp(100)

                label = MDLabel(text=name, halign="center")
                slider = MDSlider(min=0, max=10, value=5, step=1)
                self.slider_data[sid] = slider

                card.add_widget(label)
                card.add_widget(slider)
                self.ids.rating_form_container.add_widget(card)

            submit_btn = MDRaisedButton(
                text="Submit Ratings",
                pos_hint={"center_x": 0.5},
                on_release=self.submit_ratings
            )
            self.ids.rating_form_container.add_widget(submit_btn)

        conn.close()

    def submit_ratings(self, instance):
        from kivymd.toast import toast
        import sqlite3
        app = MDApp.get_running_app()
        current_id = app.current_student_id

        conn = sqlite3.connect("malin_ease.db")
        cursor = conn.cursor()

        for sid, slider in self.slider_data.items():
            points = int(slider.value)
            cursor.execute("INSERT INTO ratings (student_id, rated_by, rating) VALUES (?, ?, ?)", (sid, current_id, points))
            cursor.execute("UPDATE students SET rating = rating + ? WHERE student_id = ?", (points, sid))

        conn.commit()
        conn.close()

        toast("Ratings submitted successfully!")
        app.root.current = 'student_home'

class VoucherApprovalPage(Screen):
    def on_enter(self):
        self.display_pending_vouchers()

    def display_pending_vouchers(self):
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDFlatButton

        self.ids.voucher_approval_container.clear_widgets()

        vouchers = get_pending_vouchers()

        for voucher_id, student_name, voucher_type in vouchers:
            # ... existing card creation code ...
            type_label = MDLabel(
                text=f"Voucher: {self.get_voucher_name(voucher_type)}",
                theme_text_color='Primary',
                size_hint_y=None,
                height=dp(30))

        if not vouchers:
            no_vouchers = MDLabel(
                text="No pending vouchers",
                halign='center',
                theme_text_color='Secondary'
            )
            self.ids.voucher_approval_container.add_widget(no_vouchers)
            return

        for voucher_id, student_name, voucher_type in vouchers:
            card = MDCard(
                orientation='vertical',
                size_hint=(1, None),
                height=dp(150),
                padding=dp(15),
                spacing=dp(10)
            )

            student_label = MDLabel(
                text=f"Student: {student_name}",
                theme_text_color='Primary',
                size_hint_y=None,
                height=dp(30))

            type_label = MDLabel(
                text=f"Voucher: {self.get_voucher_name(voucher_type)}",
                theme_text_color='Primary',
                size_hint_y=None,
                height=dp(30))

            btn_box = MDBoxLayout(
                spacing=dp(10),
                size_hint_y=None,
                height=dp(50))

            approve_btn = MDRaisedButton(
                text="Approve",
                on_release=lambda x, vid=voucher_id: self.process_voucher(vid, True))

            reject_btn = MDFlatButton(
                text="Reject",
                theme_text_color='Error',
                on_release=lambda x, vid=voucher_id: self.process_voucher(vid, False))

            btn_box.add_widget(approve_btn)
            btn_box.add_widget(reject_btn)

            card.add_widget(student_label)
            card.add_widget(type_label)
            card.add_widget(btn_box)

            self.ids.voucher_approval_container.add_widget(card)

    def get_voucher_name(self, voucher_type):
        names = {'skip_cleaning': 'Skip Cleaning Pass'}
        return names.get(voucher_type, voucher_type)

    def process_voucher(self, voucher_id, approve):
        from kivymd.toast import toast

        if approve:
            success = approve_voucher(voucher_id)
            toast("Voucher approved and applied!" if success else "Failed to approve voucher")
        else:
            reject_voucher(voucher_id)
            toast("Voucher rejected")

        self.display_pending_vouchers()

class StudentRatingsPage(Screen):
    def on_enter(self):
        self.display_student_ratings()

    def display_student_ratings(self):
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.app import MDApp
        from kivy.metrics import dp

        app = MDApp.get_running_app()
        section = app.section

        import sqlite3
        conn = sqlite3.connect("malin_ease.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name, rating FROM students WHERE lower(section) = ? ORDER BY name ASC", (section.lower(),))
        students = cursor.fetchall()
        conn.close()

        self.ids.student_ratings_list.clear_widgets()

        if not students:
            no_data_label = MDLabel(
                text="No ratings available.",
                halign='center',
                theme_text_color='Secondary'
            )
            self.ids.student_ratings_list.add_widget(no_data_label)
            return

        for name, rating in students:
            student_card = MDCard(
                orientation='vertical',
                size_hint=(1, None),
                padding=dp(10),
                spacing=dp(5),
                elevation=4,
                radius=[15, 15, 15, 15],
                md_bg_color=(1, 1, 1, 1)
            )
            student_card.bind(minimum_height=student_card.setter('height'))

            name_label = MDLabel(
                text=f"{name}",
                theme_text_color='Primary',
                font_style='H6',
                size_hint_y=None,
                height=dp(30)
            )
            rating_label = MDLabel(
                text=f"Total Points: {rating}",
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(24)
            )

            student_card.add_widget(name_label)
            student_card.add_widget(rating_label)

            self.ids.student_ratings_list.add_widget(student_card)

            def submit_ratings(self, instance):
                from kivymd.toast import toast
                import sqlite3
                app = MDApp.get_running_app()
                current_id = app.current_student_id

                conn = sqlite3.connect("malin_ease.db")
                cursor = conn.cursor()

                for sid, slider in self.slider_data.items():
                    points = int(slider.value)
                    cursor.execute("INSERT INTO ratings (student_id, rated_by, rating) VALUES (?, ?, ?)",
                                   (sid, current_id, points))
                    cursor.execute("UPDATE students SET rating = rating + ? WHERE student_id = ?",
                                   (points, sid))

                conn.commit()
                conn.close()

                # Refresh student info display
                student = get_student_info(current_id)
                if student:
                    name, section, rating = student
                    app.root.get_screen('student_home').ids.student_info.text = f"{name} | Section: {section}"
                    app.root.get_screen('student_home').ids.student_ratings.text = f"Ratings: {rating}"

                toast("Ratings submitted successfully!")
                app.root.current = 'student_home'

class MalinEASEApp(MDApp):
    section = StringProperty("")
    current_student_id = StringProperty("")

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

    def show_voucher_notification(self):
        from kivymd.toast import toast
        pending = get_pending_vouchers()
        if pending:
            toast(f"You have {len(pending)} voucher requests pending approval")

    def get_voucher_name(self, voucher_type):
        names = {
            'skip_cleaning': 'Skip Cleaning Pass'
        }
        return names.get(voucher_type, voucher_type)

    def process_voucher(self, voucher_id, approve):
        from kivymd.toast import toast
        from database import approve_voucher, reject_voucher

        if approve:
            success = approve_voucher(voucher_id)
            if success:
                toast("Voucher approved and applied!")
            else:
                toast("Failed to approve voucher")
        else:
            reject_voucher(voucher_id)
            toast("Voucher rejected")

        self.display_pending_vouchers()

if __name__ == '__main__':
    MalinEASEApp().run()
