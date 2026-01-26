from django import forms
from .models import Coverage
class Coverage_Form(forms.ModelForm):
    class Meta:
        model=Coverage
        fields='__all__'
        labels={
            # پوشش‌های Boolean
            'vahanele_motori': 'حوادث ناشی از وسایل نقلیه موتوری',
            'hazine_pezezhki': 'جبران هزینه های پزشکی',
            'jange_az_sanavi': 'خسارت ناشی از جنگ',
            'tabareh_66': 'تبصره 1 ماده 66 قانون تامین اجتماعی',
            'masouliat_ashkhas_sevom': 'مسئولیت بیمه گذار در قبال اشخاص ثالث',
            'tedad_diyat': 'تعدد دیات و دیات غیر مسری',
            'mamooriat_kharej': 'ماموریت خارج از کارگاه',
            'masouliat_mojri': 'مسئولیت مجری ذیصلاح ساختمان',
            'gharamat_roozane': 'غرامت دستمزد روزانه',
            'hazine_kargoshay': 'هزینه‌های پرداختی به کارشناس',

            # پارامترهای پوشش
            'tabareh_66_person': 'حداکثر تعهد بیمه گر برای هر نفر (تبصره 66)',
            'tabareh_66_total': 'حداکثر تعهد بیمه گر در کل مدت قرارداد (تبصره 66)',
            
            'mamooriat_kharej_person': 'حداکثر تعهد فردی (ماموریت خارج از کارگاه)',
            'mamooriat_kkharej_total': 'حداکثر تعهد کل (ماموریت خارج از کارگاه)',
            
            'gharamat_roozane_person': 'حداکثر تعهد فردی (غرامت دستمزد روزانه)',
            'gharamat_roozane_total': 'حداکثر تعهد کل (غرامت دستمزد روزانه)',
            
            'hazine_kargoshay_person': 'حداکثر تعهد فردی (هزینه‌های پرداختی به کارشناس)',
            'hazine_kargoshay_total': 'حداکثر تعهد کل (هزینه‌های پرداختی به کارشناس)',
            
            # افزایش ریالی دیه
            'die_increase': 'افزایش ریالی دیه',
            'die_increase_option': 'مدت افزایش ریالی دیه',
            }
    def __init__(self, *args, is_endorsement=False, signup=None, **kwargs):
        # بیرون کشیدن signup از kwargs
        if signup:
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['signup'] = signup

        super().__init__(*args, **kwargs)

        # فیلد signup مخفی
        if 'signup' in self.fields:
            self.fields['signup'].widget = forms.HiddenInput()

        # ⚡ غیرفعال کردن پوشش‌ها در صورت بیمه فعال
        if is_endorsement:
            for field_name, field in self.fields.items():
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['disabled'] = 'disabled'