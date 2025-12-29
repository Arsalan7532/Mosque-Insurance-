from decimal import Decimal
class CoverageCalculator:
    """
    محاسبه حق بیمه پوشش‌ها
    """

    def __init__(self, base_price, coverage):
        """
        base_price : int
        coverage   : Coverage model instance
        """
        self.base_price = base_price
        self.c = coverage
        self.details = {}

    def calculate(self):
        total = 0

        # --- پوشش‌های درصدی ساده ---
        if self.c.vahanele_motori:   # حوادث ناشی از وسایل نقلیه موتوری
            price = int(self.base_price * Decimal("0.05"))  # 5٪
            self.details["vahanele_motori"] = price
            total += price

        if self.c.hazine_pezezhki: # جبران هزینه های پزشکی
            price = int(self.base_price * Decimal("0.07"))  # 7٪
            self.details["hazine_pezezhki"] = price
            total += price

        if self.c.jange_az_sanavi: # خسارت ناشی از جنگ
            price = int(self.base_price * Decimal("0.03"))
            self.details["jange_az_sanavi"] = price
            total += price

        if self.c.masouliat_ashkhas_sevom: # مسئولیت در قبال اشخاص ثالث
            price = int(self.base_price * Decimal("0.06"))
            self.details["masouliat_ashkhas_sevom"] = price
            total += price

        if self.c.tedad_diyat:  # تعدد دیات و دیات غیر مسری
            price = int(self.base_price * Decimal("0.04"))
            self.details["tedad_diyat"] = price
            total += price

        if self.c.masouliat_mojri: # مسئولیت مجری ذیصلاح ساختمان
            price = int(self.base_price * Decimal("0.02"))
            self.details["masouliat_mojri"] = price
            total += price

        # --- پوشش‌های با سقف تعهد ---
        total += self._calc_by_limit(
            enabled=self.c.tabareh_66,
            person_limit=self.c.tabareh_66_person,
            total_limit=self.c.tabareh_66_total,
            key="tabareh_66", # تبصره 1 ماده 66 قانون تامین اجتماعی
            rate=Decimal("0.001")
        )

        total += self._calc_by_limit(
            enabled=self.c.mamooriat_kharej,
            person_limit=self.c.mamooriat_kharej_person,
            total_limit=self.c.mamooriat_kharej_total,
            key="mamooriat_kharej", # مأموریت خارج از کارگاه
            rate=Decimal("0.0012")
        )

        total += self._calc_by_limit(
            enabled=self.c.gharamat_roozane,
            person_limit=self.c.gharamat_roozane_person,
            total_limit=self.c.gharamat_roozane_total,
            key="gharamat_roozane", # غرامت دستمزد روزانه
            rate=Decimal("0.002")
        )

        total += self._calc_by_limit(
            enabled=self.c.hazine_kargoshay,
            person_limit=self.c.hazine_kargoshay_person,
            total_limit=self.c.hazine_kargoshay_total,
            key="hazine_kargoshay",# هزینه‌های پرداختی به کارشناس
            rate=Decimal("0.0015")
        )

        # --- افزایش دیه ---
        if self.c.die_increase and self.c.die_increase_option:
            multipliers = {
                "1": Decimal ("0.03"),
                "2": Decimal ("0.05"),
                "3": Decimal ("0.08"),
            }
            price = int(self.base_price * multipliers[self.c.die_increase_option])
            self.details["die_increase"] = price
            total += price

        return self.details, total
        
    def _calc_by_limit(self, *, enabled, person_limit, total_limit, key, rate):
        """
        محاسبه پوشش‌های دارای سقف تعهد
        """
        if not enabled:
            return 0
        if not total_limit:
            self.details[key] = 0
            return 0

        price = int(Decimal(total_limit) * rate)
        self.details[key] = price
        return price
