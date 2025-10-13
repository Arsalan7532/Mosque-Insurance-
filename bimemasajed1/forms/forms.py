from django import forms
from .models import Signup , MainRegistration,PersonInfo,BuildingInformation, TrusteesBoard,question
class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username', None)
        super().__init__(*args, **kwargs)

        # استایل عمومی برای همهٔ فیلدها
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-400 focus:outline-none',
                'placeholder': field.label
            })

        # محدودسازی فیلد registration به کاربر فعلی
        if username and 'registration' in self.fields:
            self.fields['registration'].queryset = Signup.objects.filter(username=username)
            
class SignupForm(forms.ModelForm):
    class Meta:
        model=Signup
        fields=['username','password','email']
        labels={
            'username':"نام کاربری",
            'password':"رمز عبور",
            'email':"ایمیل",
            }
class LoginForm(forms.Form):
    username=forms.CharField(max_length=20, label="نام کاربری")
    password=forms.CharField(max_length=20, label="رمز عبور")
class MainRegistration_form(StyledModelForm):
    class Meta:
        model=MainRegistration
        #fields=['mosque_name','mosque_id','mosque_Capacity','mosque_postalcode','mosque_address','mosque_phone','created_phone']
        fields='__all__'
        widgets = {
            'mosque_phone': forms.NumberInput(attrs={'placeholder': 'تلفن ثابت'}),
            'created_phone': forms.NumberInput(attrs={'placeholder': 'موبایل نماینده'}),
        }
        labels={'mosque_name':"نام مسجد",
                'mosque_id':"شماره شناسایی مسجد",
                'mosque_Capacity':"ظرفیت نمازگزار",
                'mosque_postalcode':"کدپستی مسجد",
                'mosque_address':"آدرس مسجد",
                'mosque_phone':"تلفن ثابت",
                'created_phone':"تلفن موبایل نماینده"}
        help_texts = {
            'mosque_postalcode': 'کد ۱۰ رقمی وارد کنید.',
            'created_phone': 'شماره موبایل ۱۱ رقمی.',
        }
    def __init__(self, *args, **kwargs):
        # گرفتن username از view (در صورت وجود)
        username = kwargs.pop('username', None)
        super().__init__(*args, **kwargs)

        # ظاهر کلی فیلدها (قبلاً StyledModelForm این رو انجام میداد، اینجا هم می‌تونه اضافه بشه)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-400 focus:outline-none',
                'placeholder': field.label
            })

        # اگر username داده شده و فیلد registration هست، queryset را محدود کن
        if username and 'registration' in self.fields:
            self.fields['registration'].queryset = Signup.objects.filter(username=username)
class PersonInfo_form(forms.ModelForm):
    class Meta:
        model=PersonInfo
        fields=['servan_number','fullname_servan','person_role']
        labels={'servan_number':"تعداد خدمتگزاران",
                'fullname_servan':"نام و نام خانوادگی خادم",
                'person_role':"نقش خادم",
                }
class BuildingInformation_form(forms.ModelForm):
    class Meta:
        model=BuildingInformation
        fields=['total_land_area','total_bulding_area','user_type','structure_type','structure_age','structure_meterage']
        labels={'total_land_area':"متراژ کل زمین",
                'total_bulding_area':"متراژ کل زیربنا",
                'user_type':"نوع کاربری",
                'structure_type':"نوع سازه",
                'structure_age':"قدمت سازه",
                'structure_meterage':"متراژ",
                }
class TrusteesBoard_form(forms.ModelForm):
    class Meta:
        model=TrusteesBoard
        fields=['number_TrusteesBoard','boss_fullname','boss_nationalcode','boss_phone','boss_birthday','secretary_fullname','secretary_nationalcode','secretary_phone','secretary_birthday']
        labels={'number_TrusteesBoard':"تعداد هیات امنا",
                'boss_fullname':"نام و نام خانوادگی رئیس هیات امنا",
                'boss_nationalcode':"کدملی رئیس هیات امنا",
                'boss_phone':"موبایل رئیس هیات امنا",
                'boss_birthday':"تاریخ تولد رئیس هیات امنا",
                'secretary_fullname':"نام و نام خانوادگی سر دبیر هیات امنا", 
                'secretary_nationalcode':"کدملی سر دبیر هیات امنا", 
                'secretary_phone':"موبایل سر دبیر هیات امنا", 
                'secretary_birthday':"تاریخ تولد سر دبیر هیات امنا", 
                }
class question_form(forms.ModelForm):
    class Meta:
        model=question
        fields=['bimeHavades','dakhelRahn','dakhelVagozar','kharejMalek']
        labels={'bimeHavades':"بیمه حوادث؟",
                'dakhelRahn':"بنا داخل رهن؟",
                'dakhelVagozar':"بنا داخل واگذاری؟",
                'kharejMalek':"مالک بنای خارجی؟",
        }