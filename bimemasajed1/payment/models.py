from django.db import models
from Insurance.models import Coverage  

class Payment(models.Model):
    coverage = models.ForeignKey(Coverage, on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveIntegerField()  # مبلغ نهایی که برای درگاه میره
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "در انتظار"),
            ("paid", "پرداخت شد"),
            ("failed", "ناموفق")
        ],
        default="pending"
    )
    authority = models.CharField(max_length=100, blank=True, null=True)  # کد برگشتی درگاه
    ref_id = models.CharField(max_length=100, blank=True, null=True)   # تراکنش بانک
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.status}"