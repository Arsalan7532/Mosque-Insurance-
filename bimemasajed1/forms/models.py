from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator,MinLengthValidator
class Signup(models.Model):
    username=models.CharField(max_length=20,verbose_name="نام کاربری",unique=True)
    password=models.CharField(max_length=200,verbose_name="رمز عبور")
    email=models.EmailField(verbose_name="ایمیل",unique=True)
    def __str__(self):
        return self.username
    class Meta:
        verbose_name="کاربران"
class MainRegistration(models.Model):
    registration=models.ForeignKey(Signup,on_delete=models.CASCADE,related_name="mosque",verbose_name="کاربر ثبت کننده")
    mosque_name=models.CharField(max_length=50,verbose_name="نام مسجد")
    mosque_id=models.IntegerField(verbose_name="کد شناسایی مسجد")
    mosque_Capacity=models.IntegerField(validators=[MinValueValidator(10)],verbose_name='ظرفیت نمازگزار')
    mosque_postalcode=models.CharField(verbose_name="کدپستی مسجد",validators=[MinLengthValidator(9)],max_length=11)
    mosque_address=models.CharField(max_length=200,verbose_name="آدرس مسجد")
    mosque_phone=models.CharField(verbose_name="تلفن ثابت مسجد",blank=True,max_length=11,validators=[MinLengthValidator(11)])
    created_phone=models.CharField(verbose_name="تلفن موبایل",max_length=11,validators=[MinLengthValidator(11)],unique=True)
    create_date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.mosque_name
    class Meta:
        verbose_name="لیست مساجد"
class PersonInfo(models.Model):
    registration=models.ForeignKey(MainRegistration,on_delete=models.CASCADE,related_name="persons",verbose_name="خادمین")
    servan_number=models.IntegerField(validators= [MinValueValidator(1)],verbose_name='تعداد خادمین')
    fullname_servan=models.CharField(max_length=30,verbose_name="نام و نام خانوادگی")
    person_role=models.CharField(max_length=60,verbose_name="نقش فرد")
    def __str__(self):
        return f"{self.fullname_servan} - {self.registration.mosque_name}"
    class Meta:
        verbose_name="لیست خادمین"
class BuildingInformation(models.Model):
    registration=models.ForeignKey(MainRegistration,on_delete=models.CASCADE,related_name="structures",verbose_name="بنا")
    total_land_area=models.IntegerField(validators=[MinValueValidator(50),MaxValueValidator(10000)],verbose_name="متراژ کل زمین")
    total_bulding_area=models.IntegerField(validators=[MinValueValidator(50),MaxValueValidator(10000)],verbose_name="متراژ زیربنا")
    user_type=models.CharField(max_length=25,verbose_name="نوع کاربری")#قابل تکرار
    structure_type=models.CharField(max_length=25,verbose_name="نوع سازه")#قابل تکرار
    structure_age=models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(60)],verbose_name="قدمت")#قابل تکرار
    structure_meterage=models.IntegerField(validators=[MinValueValidator(40),MaxValueValidator(10000)])#قابل تکرار
    def __str__(self):
        return f"{self.total_land_area} - {self.registration.mosque_name}"
    class Meta:
        verbose_name="اطلاعات ساختمان"
class TrusteesBoard(models.Model):
    registration=models.ForeignKey(MainRegistration,on_delete=models.CASCADE,related_name="TrusteesBoard")
    number_TrusteesBoard=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(15)],verbose_name=" هیات امنا")
    boss_fullname=models.CharField(verbose_name="نام و نام خانوادگی رئیس هیات امنا")
    boss_nationalcode=models.CharField(max_length=10,verbose_name="کد ملی رئیس هیات امنا")
    boss_phone=models.CharField(max_length=11,verbose_name="تلفن همراه رئیس هیات امنا")
    boss_birthday=models.DateField(verbose_name="تاریخ تولد رئیس هیات امنا")
    secretary_fullname=models.CharField(verbose_name="نام و نام خانوادگی دبیر هیاامنا")
    secretary_nationalcode=models.CharField(max_length=10,verbose_name="کد ملی دبیر هیات امنا")
    secretary_phone=models.CharField(max_length=11,verbose_name="تل همراه دبیر هیات امنا")
    secretary_birthday=models.DateField(verbose_name="تاریخ تولد دبیر هیات امنا")
    def __str__(self):
        return self.boss_fullname
    class Meta:
        verbose_name="هیات امنا"
class question(models.Model):
    registration=models.ForeignKey(MainRegistration,on_delete=models.CASCADE,related_name="question",verbose_name="سوالات")
    bimeHavades=models.BooleanField(default=False,verbose_name="بیمه حوادث؟")
    dakhelRahn=models.BooleanField(default=False,verbose_name="رهن ساختمان در داخل؟")
    dakhelVagozar=models.BooleanField(default=False,verbose_name="واگذاری ساختمان در داخل؟")
    kharejMalek=models.BooleanField(default=False,verbose_name="مالک فضای خارج از مسجد؟")
    def __str__(self):  # اضافه: برای نمایش بهتر
        return f"سؤال‌های مسجد {self.registration.mosque_name}"
    class Meta:
        verbose_name="سوالات"