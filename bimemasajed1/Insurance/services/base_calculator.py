class BaseCalculator:
    """
    محاسبه حق بیمه پایه
    """
    def calculate(self,building):
        if not building:
            return 1000000

        area = building.total_bulding_area
        if not area or area <= 0:
            return 1000000  # مقدار پیش‌فرض برای مساحت نامعتبر

        if area <= 500:
            base_price = 1000000
        elif area <= 1000:
            base_price = 1500000
        elif area <= 2000:
            base_price = 2000000
        elif area <= 4000:
            base_price = 2500000
        else:
            base_price = 2500000

        return base_price