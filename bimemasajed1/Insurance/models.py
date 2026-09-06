from django.db import models
from forms.models import Signup

class Coverage(models.Model):
    signup = models.OneToOneField(
        Signup,
        on_delete=models.CASCADE,
        related_name="coverage"
    )
    vahanele_motori = models.BooleanField(default=False)  # حوادث ناشی از وسایل نقلیه موتوری
    hazine_pezezhki = models.BooleanField(default=False)  # جبران هزینه های پزشکی
    jange_az_sanavi = models.BooleanField(default=False)  # خسارت ناشی از جنگ
    tabareh_66 = models.BooleanField(default=False)       # تبصره 1 ماده 66 قانون تامین اجتماعی
    masouliat_ashkhas_sevom = models.BooleanField(default=False)  # مسئولیت در قبال اشخاص ثالث
    tedad_diyat = models.BooleanField(default=False)      # تعدد دیات و دیات غیر مسری
    mamooriat_kharej = models.BooleanField(default=False) # مأموریت خارج از کارگاه
    masouliat_mojri = models.BooleanField(default=False)  # مسئولیت مجری ذیصلاح ساختمان
    gharamat_roozane = models.BooleanField(default=False) # غرامت دستمزد روزانه
    hazine_kargoshay = models.BooleanField(default=False) # هزینه‌های پرداختی به کارشناس

    # ---- پوشش‌هایی که پارامتر دارند ----

    # تبصره 66
    tabareh_66_person = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tabareh_66_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # ماموریت خارج
    mamooriat_kharej_person = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    mamooriat_kharej_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # غرامت دستمزد روزانه
    gharamat_roozane_person = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    gharamat_roozane_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # هزینه کارشناس
    hazine_kargoshay_person = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    hazine_kargoshay_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # ---- افزایش ریالی دیه (سه حالت) ----
    DIE_CHOICES = [
        ("1", "حداکثر یکسال"),
        ("2", "حداکثر دو سال"),
        ("3", "حداکثر سه سال"),
    ]
    die_increase = models.BooleanField(default=False)
    die_increase_option = models.CharField(max_length=1, choices=DIE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Coverages for {self.signup}"
    
class Insurance(models.Model):
    signup = models.ForeignKey(Signup, on_delete=models.CASCADE)
    coverage = models.ForeignKey(Coverage, on_delete=models.CASCADE)
    premium_quote = models.PositiveIntegerField(null=True, blank=True)  # مبلغ نهایی که در درگاه پرداخت شده
    STATUS_CHOICES = [
        ('quote_requested', 'درخواست نرخ'),
        ('quote_received', 'نرخ دریافت شد'),
        ('payment_pending', 'منتظر پرداخت'),
        ('payment_completed', 'پرداخت شد'),
        ('issued', 'صادر شده'),
        ('draft', 'پیش‌نویس'),
        ('failed', 'ناموفق'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    
    policy_image = models.ImageField(
    upload_to='insurance_policies/',  # پوشه ذخیره
    null=True,
    blank=True,
    verbose_name='عکس بیمه‌نامه'
)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    quote_received_at = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)