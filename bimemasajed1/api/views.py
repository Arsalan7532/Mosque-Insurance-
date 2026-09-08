# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
import requests

from forms.models import MainRegistration
from Insurance.models import Insurance, Coverage


class RequestQuoteAPIView(APIView):

    def post(self, request):

        mosque_code = request.data.get("mosque_id")

        if not mosque_code:
            return Response(
                {"error": "mosque_id الزامی است"},
                status=400
            )

        # 1. گرفتن مسجد از روی mosque_id
        try:
            mosque = MainRegistration.objects.get(mosque_id=mosque_code)
        except MainRegistration.DoesNotExist:
            return Response(
                {"error": "مسجد پیدا نشد"},
                status=404
            )

        # 2. گرفتن signup از مسجد
        signup = mosque.registration

        # 3. گرفتن coverage مربوط به همین مسجد
        coverage = Coverage.objects.filter(signup=signup, mosque=mosque).last()
        if not coverage:
            return Response({"error": "Coverage برای این مسجد یافت نشد"}, status=404)

        # 4. ایجاد رکورد بیمه جدید برای این درخواست
        # فقط وضعیت‌های واقعی حفظ می‌شوند. در آینده پس از پرداخت موفق، اینجا به payment_completed و سپس issued تغییر می‌کند.
        insurance = Insurance.objects.create(signup=signup, coverage=coverage, status='payment_completed')

        # 5. ساخت payload ساده (فعلاً بدون serializer)
        payload = {
            "mosque": {
                "mosque_id": mosque.mosque_id,
                "mosque_name": mosque.mosque_name,
                "capacity": mosque.mosque_Capacity,
                "postalcode": mosque.mosque_postalcode,
                "address": mosque.mosque_address,
                "phone": mosque.mosque_phone,
                "created_phone": mosque.created_phone,
                #"create_date": mosque.create_date.isoformat(),
            },

            "persons": [
                {
                    "servan_number": p.servan_number,
                    "fullname_servan": p.fullname_servan,
                    "person_role": p.person_role,
                }
                for p in mosque.persons.all()
            ],

            "building": [
                {
                    "total_land_area": b.total_land_area,
                    "total_bulding_area": b.total_bulding_area,
                    "user_type": b.user_type,
                    "structure_type": b.structure_type,
                    "structure_age": b.structure_age,
                    "structure_meterage": b.structure_meterage,
                }
                for b in mosque.building.all()
            ],

            "trustees_board": [
                {
                    "number_TrusteesBoard": t.number_TrusteesBoard,
                    "boss_fullname": t.boss_fullname,
                    "boss_nationalcode": t.boss_nationalcode,
                    "boss_phone": t.boss_phone,
                    "boss_birthday": t.boss_birthday.isoformat(),
                    "secretary_fullname": t.secretary_fullname,
                    "secretary_nationalcode": t.secretary_nationalcode,
                    "secretary_phone": t.secretary_phone,
                    "secretary_birthday": t.secretary_birthday.isoformat(),
                }
                for t in mosque.TrusteesBoard.all()
            ],

            "timestamp": timezone.now().isoformat(),
        }
        # 6. ارسال به API بیمه (Mock)
        try:
            response = requests.post( #خط 86 حذف گردد
                "http://localhost:8800/api/get-quote/",
                json=payload,
                timeout=10
            )

            if response.status_code != 200:
                return Response(
                    {
                        "error": "خطا در دریافت نرخ",
                        "detail": response.text
                    },
                    status=400
                )

            quote_data = response.json()

        except requests.RequestException:
            return Response(payload)
            #کار با api خط 86 حذف گردد
            return Response(
                {"error": "سرویس بیمه در دسترس نیست"},
                status=502
            )

        # 7. ذخیره نتیجه
        insurance.premium_quote = quote_data.get("premium_amount")
        insurance.status = "quote_received"
        insurance.quote_received_at = timezone.now()
        insurance.save()

        # 8. پاسخ نهایی
        return Response({
            "success": True,
            "premium_amount": quote_data.get("premium_amount"),
            "currency": quote_data.get("currency", "IRR"),
            "valid_until": quote_data.get("valid_until"),
            "insurance_id": insurance.id,
            "next_step": "payment"
        })