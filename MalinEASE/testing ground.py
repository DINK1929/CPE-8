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
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.boxlayout import MDBoxLayout
import json
import urllib.parse
from kivymd.toast import toast
import requests
from urllib.parse import urljoin

Window.size = (360, 640)

# --- API Configuration ---
API_BASE_URL = "http://dirk.x10.mx/Malin_EASE/api.php"  # Replace with your actual domain


def api_request(action, params=None, method='GET', callback=None, error_callback=None):
    """Make an API request to the PHP backend"""

    def request_callback(req, result):
        try:
            if isinstance(result, str):
                result = json.loads(result)
            if callback:
                callback(req, result)
        except Exception as e:
            if error_callback:
                error_callback(req, str(e))

    def request_error(req, error):
        if error_callback:
            error_callback(req, error)

    url = API_BASE_URL
    if method.upper() == 'GET':
        params = params or {}
        params['action'] = action
        url += '?' + urllib.parse.urlencode(params)
        req_body = None
    else:
        data = params or {}
        data['action'] = action
        req_body = json.dumps(data)

    print("Request URL:", url)

    UrlRequest(
        url,
        req_body=req_body,
        on_success=request_callback,
        on_error=request_error,
        on_failure=request_error,
        req_headers={'Content-Type': 'application/json'} if method.upper() != 'GET' else {}
    )


def section_exists(section, callback, error_callback=None):
    """Check if section exists"""
    api_request('section_exists', {'section': section},
                callback=callback, error_callback=error_callback)


def get_student_info(student_id, callback, error_callback=None):
    """Get student info"""
    api_request('get_student_info', {'student_id': student_id},
                callback=callback, error_callback=error_callback)


def get_teacher_info(teacher_id, callback, error_callback=None):
    """Get teacher info"""
    api_request('get_teacher_info', {'teacher_id': teacher_id},
                callback=callback, error_callback=error_callback)


# ---------------------------------------------------------------------------------------
def create_voucher(student_id, voucher_type, callback, error_callback=None):
    """Create a new voucher"""
    api_request('create_voucher',
                {'student_id': student_id, 'voucher_type': voucher_type},
                method='POST',
                callback=callback, error_callback=error_callback)


# ---------------------------------------------------------------------------------------

def get_pending_vouchers(callback, error_callback=None):
    """Get pending vouchers"""
    api_request('get_pending_vouchers',
                callback=callback, error_callback=error_callback)


def approve_voucher(voucher_id, callback, error_callback=None):
    """Approve a voucher"""
    api_request('approve_voucher', {'voucher_id': voucher_id},
                method='POST',
                callback=callback, error_callback=error_callback)


def reject_voucher(voucher_id, callback, error_callback=None):
    """Reject a voucher"""
    api_request('reject_voucher', {'voucher_id': voucher_id},
                method='POST',
                callback=callback, error_callback=error_callback)


# ---------------------------------------------------------------------------------------
def can_purchase_voucher(student_id, voucher_type, callback, error_callback=None):
    """Check if student can purchase voucher"""
    api_request('can_purchase_voucher',
                {'student_id': student_id, 'voucher_type': voucher_type},
                callback=callback, error_callback=error_callback)


def get_student_vouchers(student_id, callback, error_callback=None):
    """Get student's vouchers"""
    api_request('get_student_vouchers', {'student_id': student_id},
                callback=callback, error_callback=error_callback)


# ---------------------------------------------------------------------------------------


def get_cleaners_list(section, callback, error_callback=None):
    """Get cleaners list for a section"""
    api_request('get_cleaners_list', {'section': section},
                callback=callback, error_callback=error_callback)


def submit_ratings(rated_by, ratings, callback, error_callback=None):
    """Submit ratings"""
    api_request('submit_ratings',
                {'rated_by': rated_by, 'ratings': ratings},
                method='POST',
                callback=callback, error_callback=error_callback)


def get_student_ratings(section, callback, error_callback=None):
    """Get all student ratings for a section"""
    api_request('get_student_ratings', {'section': section},
                callback=callback, error_callback=error_callback)


def get_groupmates(student_id, success_cb, error_cb):
    url = f"{API_BASE_URL}?action=get_groupmates&student_id={student_id}"
    UrlRequest(url, on_success=success_cb, on_failure=error_cb, on_error=error_cb)


# --- Kivy UI ---
KV = '''
ScreenManager:
    LoginPage:
    ChoicePage:
    SignInPage:
    StudentHomePage:
    TeacherHomePage:
    StudentCleanerListPage:
    TeacherCleanerListPage:
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
            pos_hint: {"center_x": .5}
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

        # Horizontal container for the buttons
        BoxLayout:
            orientation: 'horizontal'
            spacing: dp(20)
            size_hint_y: None
            height: self.minimum_height
            padding: dp(20)  # Optional padding around buttons
            pos_hint: {'center_x': 0.45}

            MDRaisedButton:
                text: 'Teacher'
                on_press: root.signin('Teacher')
                size_hint_x: 0.5 if root.width > 500 else None
                width: dp(150) if root.width <= 500 else None

            MDRaisedButton:
                text: 'Student'
                on_press: root.signin('Student')
                size_hint_x: 0.5 if root.width > 500 else None
                width: dp(150) if root.width <= 500 else None

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
            pos_hint: {"center_x": .5}
            on_press: root.signin()

<StudentHomePage>:
    name: 'student_home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        # Top bar with logout button
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            MDIconButton:
                icon: "logout"
                on_release: app.confirm_logout()
                pos_hint: {"center_y": 0.5}

        # Student information labels
        MDLabel:
            id: student_info
            halign: 'center'
            font_style: 'H5'

        MDLabel:
            id: student_ratings
            halign: 'center'
            font_style: 'H6'

        # Voucher status scroll view
        ScrollView:
            MDBoxLayout:
                id: voucher_status_container
                orientation: 'vertical'
                spacing: dp(4)
                adaptive_height: True
                size_hint_y: None
                height: self.minimum_height
                padding: dp(8)

        # Button group - Cleaner List and Voucher Shop side by side
        BoxLayout:
            orientation: 'horizontal'
            spacing: dp(10)
            size_hint_y: None
            height: dp(48)

            MDRaisedButton:
                text: 'Cleaner List'
                on_press: app.root.current = 'cleaner_list'
                size_hint_x: 0.5

            MDRaisedButton:
                text: 'Voucher Shop'
                on_press: app.root.current = 'voucher_shop'
                size_hint_x: 0.5

        # Rate Cleaners button centered below the other two
        MDRaisedButton:
            text: 'Rate Cleaners'
            on_press: app.root.current = 'rating_form'
            size_hint: (None, None)
            size: (dp(200), dp(48))
            pos_hint: {'center_x': 0.5}

        # Optional spacer if you want to push everything up slightly
        Widget:
            size_hint_y: 0.1

<TeacherHomePage>:
    name: 'teacher_home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        # Top bar with logout button
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            MDIconButton:
                icon: "logout"
                on_release: app.confirm_logout()
                pos_hint: {"center_y": 0.5}

        # Teacher information label
        MDLabel:
            id: teacher_info
            halign: 'center'
            font_style: 'H5'

        # Horizontal layout for Cleaner List and Voucher Approval
        BoxLayout:
            orientation: 'horizontal'
            spacing: dp(10)
            size_hint_y: None
            height: dp(48)

            MDRaisedButton:
                text: 'Cleaner List'
                on_press: app.root.current = 'teacher_cleaner_list'
                size_hint_x: 0.5

            MDRaisedButton:
                text: 'Voucher Approval'
                on_press: app.root.current = 'voucher_approval'
                size_hint_x: 0.5

        # Student Ratings button centered below
        MDRaisedButton:
            text: 'Student Ratings'
            on_press: app.root.current = 'student_ratings'
            size_hint: (None, None)
            size: (dp(200), dp(48))
            pos_hint: {'center_x': 0.5}
        Widget:
            size_hint_y: 0.1

<StudentCleanerListPage>:
    name: 'cleaner_list'
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)

        MDTopAppBar:
            title: "Cleaner List"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.change_screen('student_home')]]

        ScrollView:
            MDBoxLayout:
                id: cleaners_list
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                adaptive_height: True

<TeacherCleanerListPage>:
    name: 'teacher_cleaner_list'
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)

        MDTopAppBar:
            title: "Cleaner List"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.change_screen('teacher_home')]]

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

<VoucherStatusCard>:
    orientation: 'vertical'
    size_hint: (1, None)
    height: dp(100)
    padding: dp(10)
    spacing: dp(5)
    elevation: 2
    radius: [15]

    MDLabel:
        id: voucher_type_label
        bold: True
        halign: 'center'
        theme_text_color: 'Custom'
        text_color: (1, 1, 1, 1)

    MDLabel:
        id: status_label
        halign: 'center'
        theme_text_color: 'Custom'
        text_color: (1, 1, 1, 1)
'''


class VoucherStatusCard(MDCard):
    def __init__(self, voucher_id, voucher_type, status, **kwargs):
        super().__init__(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(100),  # Smaller height
            padding=dp(8),  # Less padding
            **kwargs
        )
        self.ids.voucher_type_label.text = f"{voucher_type.replace('_', ' ').title()} Voucher"
        self.ids.status_label.text = f"Status: {status.upper()}"
        self.md_bg_color = {
            'approved': get_color_from_hex('#4CAF50'),
            'rejected': get_color_from_hex('#F44336'),
        }.get(status, get_color_from_hex('#FFC107'))


# --- Screen Classes ---
class LoginPage(Screen):
    def submit(self):
        section = self.ids.section_input.text.strip()
        if section:
            def callback(request, result):
                if result.get('status') == 'success' and result.get('exists'):
                    app = MDApp.get_running_app()
                    app.section = section
                    self.manager.get_screen('choice').ids.choice_label.text = f'You are in {section}'
                    self.manager.current = 'choice'
                else:
                    self.show_error("Section not found in the database.")

            def error_callback(request, error):
                self.show_error("Connection error. Please try again.")

            section_exists(section, callback, error_callback)
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
            def callback(request, result):
                if result.get('status') == 'success':
                    data = result.get('data', {})
                    name = data.get('name', '')
                    section = data.get('section', '')
                    rating = data.get('rating', 0)

                    app.root.get_screen('student_home').ids.student_info.text = f"{name} | Section: {section}"
                    app.root.get_screen('student_home').ids.student_ratings.text = f"Ratings: {rating}"
                    app.current_student_id = id_number
                    app.root.current = 'student_home'
                else:
                    self.show_dialog("Student not found.")

            def error_callback(request, error):
                self.show_dialog("Connection error. Please try again.")

            get_student_info(id_number, callback, error_callback)

        elif self.role == "Teacher":
            def callback(request, result):
                if result.get('status') == 'success':
                    data = result.get('data', {})
                    name = data.get('name', '')
                    section = data.get('section', '')

                    app.root.get_screen('teacher_home').ids.teacher_info.text = f"{name} | Section: {section}"
                    app.root.current = 'teacher_home'
                else:
                    self.show_dialog("Teacher not found.")

            def error_callback(request, error):
                self.show_dialog("Connection error. Please try again.")

            get_teacher_info(id_number, callback, error_callback)

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

        def callback(request, result):
            if result.get('status') == 'success':
                data = result.get('data', {})
                name = data.get('name', '')
                section = data.get('section', '')
                rating = data.get('rating', 0)

                self.ids.student_info.text = f"{name} | Section: {section}"
                self.ids.student_ratings.text = f"Ratings: {rating}"

        def error_callback(request, error):
            pass  # Silently fail, we'll try again next time

        get_student_info(app.current_student_id, callback, error_callback)

    def display_voucher_statuses(self):
        app = MDApp.get_running_app()

        def callback(request, result):
            self.ids.voucher_status_container.clear_widgets()

            if result.get('status') != 'success' or not result.get('data'):
                no_vouchers = MDLabel(
                    text="No voucher purchases yet",
                    halign='center',
                    theme_text_color='Secondary'
                )
                self.ids.voucher_status_container.add_widget(no_vouchers)
                return

            vouchers = result.get('data', [])
            for voucher in vouchers:
                card = VoucherStatusCard(
                    voucher_id=voucher.get('id'),
                    voucher_type=voucher.get('voucher_type'),
                    status=voucher.get('status')
                )
                self.ids.voucher_status_container.add_widget(card)

        def error_callback(request, error):
            self.ids.voucher_status_container.clear_widgets()
            error_label = MDLabel(
                text="Failed to load vouchers",
                halign='center',
                theme_text_color='Error'
            )
            self.ids.voucher_status_container.add_widget(error_label)

        get_student_vouchers(app.current_student_id, callback, error_callback)


class TeacherHomePage(Screen):
    pass


class StudentCleanerListPage(Screen):
    def on_enter(self):
        self.display_cleaners()

    def display_cleaners(self):
        app = MDApp.get_running_app()

        def callback(request, result):
            self.ids.cleaners_list.clear_widgets()

            if result.get('status') != 'success':
                error_label = MDLabel(
                    text="Failed to load cleaner list",
                    halign='center',
                    theme_text_color='Error'
                )
                self.ids.cleaners_list.add_widget(error_label)
                return

            cleaners_by_day = result.get('data', {})

            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
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
                    font_style='H6',
                    theme_text_color='Primary',
                    size_hint_y=None,
                    height=dp(30)
                )
                day_card.add_widget(day_title)

                students_list = cleaners_by_day.get(day, [])
                if students_list:
                    for name in students_list:
                        item = MDLabel(
                            text=name,
                            theme_text_color='Secondary',
                            size_hint_y=None,
                            height=dp(30))
                        day_card.add_widget(item)
                else:
                    item = MDLabel(
                        text="No students assigned",
                        theme_text_color='Secondary',
                        size_hint_y=None,
                        height=dp(30))
                    day_card.add_widget(item)

                # FIX: This must be outside the `else` to always add the card
                self.ids.cleaners_list.add_widget(day_card)

        def error_callback(request, error):
            self.ids.cleaners_list.clear_widgets()
            error_label = MDLabel(
                text="Connection error",
                halign='center',
                theme_text_color='Error'
            )
            self.ids.cleaners_list.add_widget(error_label)

        get_cleaners_list(app.section, callback, error_callback)


class TeacherCleanerListPage(Screen):
    def on_enter(self):
        self.display_cleaners()

    def display_cleaners(self):
        app = MDApp.get_running_app()

        def callback(request, result):
            self.ids.cleaners_list.clear_widgets()

            if result.get('status') != 'success':
                error_label = MDLabel(
                    text="Failed to load cleaner list",
                    halign='center',
                    theme_text_color='Error'
                )
                self.ids.cleaners_list.add_widget(error_label)
                return

            cleaners_by_day = result.get('data', {})

            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
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
                    font_style='H6',
                    theme_text_color='Primary',
                    size_hint_y=None,
                    height=dp(30)
                )
                day_card.add_widget(day_title)

                students_list = cleaners_by_day.get(day, [])
                if students_list:
                    for name in students_list:
                        item = MDLabel(
                            text=name,
                            theme_text_color='Secondary',
                            size_hint_y=None,
                            height=dp(30))
                        day_card.add_widget(item)
                else:
                    item = MDLabel(
                        text="No students assigned",
                        theme_text_color='Secondary',
                        size_hint_y=None,
                        height=dp(30))
                    day_card.add_widget(item)

                # FIX: This must be outside the `else` to always add the card
                self.ids.cleaners_list.add_widget(day_card)

        def error_callback(request, error):
            self.ids.cleaners_list.clear_widgets()
            error_label = MDLabel(
                text="Connection error",
                halign='center',
                theme_text_color='Error'
            )
            self.ids.cleaners_list.add_widget(error_label)

        get_cleaners_list(app.section, callback, error_callback)


class VoucherShopPage(Screen):
    def on_enter(self):
        self.display_vouchers()

    def display_vouchers(self):
        self.ids.voucher_container.clear_widgets()
        app = MDApp.get_running_app()

        # Define available vouchers
        vouchers = [
            {
                'type': 'skip_cleaning',
                'name': 'Skip Cleaning Pass',
                'description': 'Skip cleaning this week',
                'cost': 20
            }
        ]

        for voucher in vouchers:
            card = MDCard(
                orientation='vertical',
                size_hint=(1, None),
                height=dp(150),
                padding=dp(15),
                spacing=dp(10),
                elevation=2
            )

            name_label = MDLabel(
                text=voucher['name'],
                theme_text_color='Primary',
                font_style='H6',
                size_hint_y=None,
                height=dp(30)
            )

            desc_label = MDLabel(
                text=voucher['description'],
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(50),
                padding=(10, 0)
            )

            cost_label = MDLabel(
                text=f"Cost: {voucher['cost']} ratings",
                theme_text_color='Primary',
                size_hint_y=None,
                height=dp(20),
                bold=True
            )

            purchase_btn = MDRaisedButton(
                text="Purchase",
                size_hint_y=None,
                height=dp(40),
                on_release=lambda x, v_type=voucher['type']: self.purchase_voucher(v_type)
            )

            card.add_widget(name_label)
            card.add_widget(desc_label)
            card.add_widget(cost_label)
            card.add_widget(purchase_btn)

            self.ids.voucher_container.add_widget(card)

    def purchase_voucher(self, voucher_type):
        from kivymd.toast import toast
        from kivy.network.urlrequest import UrlRequest
        app = MDApp.get_running_app()

        url = "http://dirk.x10.mx/Malin_EASE/insertVoucher.php"
        headers = {'Content-Type': 'application/json'}
        data = {
            'student_id': app.current_student_id,
            'voucher_type': voucher_type
        }

        def purchase_success(req, result):
            if result.get('status') == 'success':
                toast("Voucher purchased! Waiting for teacher approval.")
                # Update the student info and voucher status
                self.manager.get_screen('student_home').update_student_info()
                self.manager.get_screen('student_home').display_voucher_statuses()
                self.manager.current = 'student_home'
            else:
                toast(result.get('message', "Failed to purchase voucher."))

        def purchase_failure(req, error):
            toast("Connection error. Please try again.")

        # Send the request
        UrlRequest(
            url,
            on_success=purchase_success,
            on_failure=purchase_failure,
            on_error=purchase_failure,
            req_headers=headers,
            req_body=json.dumps(data),
            method='POST'
        )


class RatingFormPage(Screen):
    def on_enter(self):
        self.display_groupmates()
        self.submit_button = None
        self.has_rated_today = False  # Track if user has rated today

    def display_groupmates(self):
        self.ids.rating_form_container.clear_widgets()
        app = MDApp.get_running_app()
        self.submit_button = None

        def callback(result):
            try:
                if result.get('status') != 'success':
                    error_label = MDLabel(
                        text="Failed to load groupmates",
                        halign='center',
                        theme_text_color='Error'
                    )
                    self.ids.rating_form_container.add_widget(error_label)
                    return

                # Check if user has already rated today
                if result.get('has_rated_today', False):
                    self.has_rated_today = True
                    rated_label = MDLabel(
                        text="You have already submitted ratings today",
                        halign='center',
                        theme_text_color='Secondary'
                    )
                    self.ids.rating_form_container.add_widget(rated_label)
                    return

                students = result.get('data', [])
                if not students:
                    no_groupmates = MDLabel(
                        text="No groupmates found for your cleaning day",
                        halign='center',
                        theme_text_color='Secondary'
                    )
                    self.ids.rating_form_container.add_widget(no_groupmates)
                    return

                self.slider_data = {}

                for student in students:
                    sid = student.get('student_id')
                    name = student.get('name')

                    if not sid or not name:
                        continue

                    card = MDCard(orientation="vertical", padding=10, size_hint_y=None)
                    card.height = dp(100)

                    label = MDLabel(text=name, halign="center")
                    slider = MDSlider(min=0, max=10, value=5, step=1)
                    self.slider_data[sid] = slider

                    card.add_widget(label)
                    card.add_widget(slider)
                    self.ids.rating_form_container.add_widget(card)

                self.submit_button = MDRaisedButton(
                    text="Submit Ratings",
                    pos_hint={"center_x": 0.5},
                    on_release=self.submit_ratings,
                    disabled=False
                )
                self.ids.rating_form_container.add_widget(self.submit_button)
            except Exception as e:
                print(f"Error processing groupmates: {e}")

        def error_callback(error):
            error_label = MDLabel(
                text="Connection error",
                halign='center',
                theme_text_color='Error'
            )
            self.ids.rating_form_container.add_widget(error_label)

        self.make_request(
            'get_groupmates.php',
            {
                'student_id': app.current_student_id,
                'check_rating_status': True  # Request to check if already rated today
            },
            callback,
            error_callback
        )

    def submit_ratings(self, instance):
        if self.has_rated_today:
            return

        from kivymd.toast import toast
        app = MDApp.get_running_app()

        if not hasattr(self, 'slider_data') or not self.slider_data:
            toast("No groupmates to rate")
            return

        if self.submit_button:
            self.submit_button.disabled = True
            self.submit_button.text = "Submitting..."

        ratings = []
        for sid, slider in self.slider_data.items():
            ratings.append({
                'student_id': sid,
                'rating': int(slider.value)
            })

        def callback(result):
            if result.get('status') == 'success':
                toast("Ratings submitted successfully!")
                if self.submit_button:
                    self.submit_button.disabled = True
                    self.submit_button.text = "Ratings Submitted"
                self.has_rated_today = True
                self.manager.get_screen('student_home').update_student_info()
                self.manager.current = 'student_home'
            else:
                toast(result.get('message', "Failed to submit ratings."))
                if self.submit_button:
                    self.submit_button.disabled = False
                    self.submit_button.text = "Submit Ratings"

        def error_callback(error):
            toast(f"Error: {error}")
            print("Full error details:", error)
            if self.submit_button:
                self.submit_button.disabled = False
                self.submit_button.text = "Submit Ratings"

        self.make_request(
            'submit_ratings.php',
            {
                'rated_by': app.current_student_id,
                'ratings': ratings
            },
            callback,
            error_callback
        )

    def make_request(self, endpoint, data, success_callback, error_callback):
        """Helper method to make HTTP requests"""
        base_url = "http://dirk.x10.mx/Malin_EASE/"
        url = f"{base_url}{endpoint}"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        UrlRequest(
            url,
            req_body=json.dumps(data),
            on_success=lambda req, res: success_callback(res),
            on_error=lambda req, error: error_callback(error),
            on_failure=lambda req, result: error_callback(result),
            req_headers=headers
        )

BASE_URL = "http://dirk.x10.mx/Malin_EASE/"

class VoucherApprovalPage(Screen):
    def on_enter(self):
        self.display_pending_vouchers()

    def display_pending_vouchers(self):
        self.ids.voucher_approval_container.clear_widgets()

        try:
            response = requests.get(urljoin(BASE_URL, "get_pending_vouchers.php"))
            result = response.json()

            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error occurred')
                toast(f"Error: {error_msg}")
                self.show_no_vouchers()
                return

            vouchers = result.get('data', [])
            if not vouchers:
                self.show_no_vouchers()
                return

            for voucher in vouchers:
                card = MDCard(
                    orientation='vertical',
                    size_hint=(1, None),
                    height=dp(150),
                    padding=dp(15),
                    spacing=dp(10)
                )

                student_label = MDLabel(
                    text=f"Student: {voucher.get('student_name', '')}",
                    theme_text_color='Primary',
                    size_hint_y=None,
                    height=dp(30))

                type_label = MDLabel(
                    text=f"Voucher: {self.get_voucher_name(voucher.get('voucher_type', ''))}",
                    theme_text_color='Primary',
                    size_hint_y=None,
                    height=dp(30))

                btn_box = MDBoxLayout(
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(50))

                approve_btn = MDRaisedButton(
                    text="Approve",
                    on_release=lambda x, vid=voucher.get('voucher_id'): self.process_voucher(vid, True))

                reject_btn = MDFlatButton(
                    text="Reject",
                    theme_text_color='Error',
                    on_release=lambda x, vid=voucher.get('voucher_id'): self.process_voucher(vid, False))

                btn_box.add_widget(approve_btn)
                btn_box.add_widget(reject_btn)

                card.add_widget(student_label)
                card.add_widget(type_label)
                card.add_widget(btn_box)

                self.ids.voucher_approval_container.add_widget(card)

        except requests.exceptions.RequestException as e:
            toast("Connection error. Please try again.")
            print(f"Network error: {e}")
        except Exception as e:
            toast("Failed to load vouchers")
            print(f"Error: {e}")

    def show_no_vouchers(self):
        no_vouchers = MDLabel(
            text="No pending vouchers",
            halign='center',
            theme_text_color='Secondary'
        )
        self.ids.voucher_approval_container.add_widget(no_vouchers)

    def get_voucher_name(self, voucher_type):
        names = {'skip_cleaning': 'Skip Cleaning Pass'}
        return names.get(voucher_type, voucher_type)

    def process_voucher(self, voucher_id, approve):
        try:
            endpoint = "approve_voucher.php" if approve else "reject_voucher.php"
            response = requests.post(
                urljoin(BASE_URL, endpoint),
                json={'voucher_id': voucher_id},  # Changed from data to json
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()

            if result.get('success'):
                toast(result.get('message', "Voucher processed successfully"))
                self.display_pending_vouchers()

                # Update student info if needed
                if approve:
                    self.manager.get_screen('student_home').update_student_info()
            else:
                error_msg = result.get('error', 'Failed to process voucher')
                toast(f"Error: {error_msg}")
        except requests.exceptions.RequestException as e:
            toast("Connection error. Please try again.")
            print(f"Network error: {e}")
        except Exception as e:
            toast("Failed to process voucher")
            print(f"Error: {e}")

class StudentRatingsPage(Screen):
    def on_enter(self):
        self.display_student_ratings()

    def display_student_ratings(self):
        app = MDApp.get_running_app()

        # Define the callback functions first
        def success_callback(request, result):
            self.ids.student_ratings_list.clear_widgets()

            try:
                if isinstance(result, str):
                    result = json.loads(result)

                if result.get('status') != 'success' or not result.get('data'):
                    no_data_label = MDLabel(
                        text="No ratings available.",
                        halign='center',
                        theme_text_color='Secondary'
                    )
                    self.ids.student_ratings_list.add_widget(no_data_label)
                    return

                students = result.get('data', [])
                for student in students:
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
                        text=f"{student.get('name', '')}",
                        theme_text_color='Primary',
                        font_style='H6',
                        size_hint_y=None,
                        height=dp(30)
                    )
                    rating_label = MDLabel(
                        text=f"Total Points: {student.get('rating', 0)}",
                        theme_text_color='Secondary',
                        size_hint_y=None,
                        height=dp(24)
                    )

                    student_card.add_widget(name_label)
                    student_card.add_widget(rating_label)

                    self.ids.student_ratings_list.add_widget(student_card)

            except Exception as e:
                error_label = MDLabel(
                    text="Error processing data",
                    halign='center',
                    theme_text_color='Error'
                )
                self.ids.student_ratings_list.add_widget(error_label)

        def error_callback(request, error):
            self.ids.student_ratings_list.clear_widgets()
            error_label = MDLabel(
                text="Failed to load ratings",
                halign='center',
                theme_text_color='Error'
            )
            self.ids.student_ratings_list.add_widget(error_label)

        # Now call get_student_ratings with both arguments
        get_student_ratings(app.section, success_callback, error_callback)


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

        def callback(request, result):
            if result.get('status') == 'success':
                pending = result.get('data', [])
                if pending:
                    toast(f"You have {len(pending)} voucher requests pending approval")

        def error_callback(request, error):
            pass  # Silently fail

        get_pending_vouchers(callback, error_callback)


if __name__ == '__main__':
    MalinEASEApp().run()