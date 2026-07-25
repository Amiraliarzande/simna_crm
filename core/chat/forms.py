from django import forms
from .models import ChatMessage, ChatRoom, Note
from staff.models import StaffProfile


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'file']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition resize-none',
                'rows': 2,
                'placeholder': 'پیام خود را وارد کنید...'
            }),
            'file': forms.FileInput(attrs={
                'class': 'hidden'
            }),
        }


class ChatRoomForm(forms.Form):
    room_type = forms.ChoiceField(
        choices=ChatRoom.ROOM_TYPES,
        widget=forms.Select(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
        })
    )
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
            'placeholder': 'نام گروه را وارد کنید...'
        })
    )
    department = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].choices = StaffProfile.DEPARTMENT_CHOICES


class NoteForm(forms.ModelForm):
    """فرم یادداشت"""

    class Meta:
        model = Note
        fields = ['title', 'content', 'color', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'عنوان یادداشت را وارد کنید...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 6,
                'placeholder': 'متن یادداشت را وارد کنید...'
            }),
            'color': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].label = 'رنگ'
        self.fields['is_pinned'].label = 'پین شود'
        self.fields['title'].label = 'عنوان'
        self.fields['content'].label = 'متن یادداشت'


# chat/forms.py
from django import forms
from .models import ChatMessage, ChatRoom, Note, CalendarEvent  # <-- CalendarEvent را import کنید


# ... کلاس‌های قبلی (ChatMessageForm, ChatRoomForm, NoteForm) ...


class CalendarEventForm(forms.ModelForm):
    """فرم رویداد تقویم"""

    class Meta:
        model = CalendarEvent
        fields = ['title', 'description', 'date', 'time', 'color', 'priority', 'is_important']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'عنوان رویداد را وارد کنید...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 3,
                'placeholder': 'توضیحات...'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'type': 'time'
            }),
            'color': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'عنوان'
        self.fields['description'].label = 'توضیحات'
        self.fields['date'].label = 'تاریخ'
        self.fields['time'].label = 'ساعت'
        self.fields['color'].label = 'رنگ'
        self.fields['priority'].label = 'اولویت'
        self.fields['is_important'].label = 'مهم'



