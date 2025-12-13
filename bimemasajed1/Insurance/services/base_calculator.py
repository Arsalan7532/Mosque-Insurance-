class BaseCalculator:
    """
    محاسبه حق بیمه پایه
    """
    def calculate(self,building):
        area = building.total_bulding_area

        if area <= 500:
            base_price = 1_000_000
        elif area <= 1000:
            base_price = 1_500_000
        elif area <= 2000:
            base_price = 2_000_000
        elif area <= 4000:
            base_price = 2_500_000
        else:
            base_price = 2_500_000

        return base_price