from rest_framework import serializers
from forms.models import MainRegistration, BuildingInformation, PersonInfo, TrusteesBoard, question
from Insurance.models import Insurance, Coverage

class PersonInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonInfo
        fields = ['servan_number', 'fullname_servan', 'person_role']

class BuildingInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingInformation
        fields = ['total_land_area', 'total_bulding_area', 'user_type', 
                 'structure_type', 'structure_age', 'structure_meterage']

class TrusteesBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrusteesBoard
        fields = ['number_TrusteesBoard', 'boss_fullname', 'boss_nationalcode',
                 'boss_phone', 'boss_birthday', 'secretary_fullname',
                 'secretary_nationalcode', 'secretary_phone', 'secretary_birthday']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = question
        fields = ['bimeHavades', 'dakhelRahn', 'dakhelVagozar', 'kharejMalek']

class CoverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coverage
        fields = [
            'vahanele_motori', 'hazine_pezezhki', 'jange_az_sanavi', 
            'tabareh_66', 'masouliat_ashkhas_sevom', 'tedad_diyat',
            'mamooriat_kharej', 'masouliat_mojri', 'gharamat_roozane',
            'hazine_kargoshay', 'tabareh_66_person', 'tabareh_66_total',
            'mamooriat_kharej_person', 'mamooriat_kharej_total',
            'gharamat_roozane_person', 'gharamat_roozane_total',
            'hazine_kargoshay_person', 'hazine_kargoshay_total',
            'die_increase', 'die_increase_option'
        ]

class InsuranceSerializer(serializers.ModelSerializer):
    coverage = CoverageSerializer()
    
    class Meta:
        model = Insurance
        fields = ['id', 'status', 'created_at', 'updated_at', 'coverage']

class MainRegistrationSerializer(serializers.ModelSerializer):
    # اضافه کردن اطلاعات مرتبط
    persons = PersonInfoSerializer(many=True, read_only=True)
    building = BuildingInformationSerializer(many=True, read_only=True)
    TrusteesBoard = TrusteesBoardSerializer(many=True, read_only=True)
    question = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = MainRegistration
        fields = [
            'mosque_name', 'mosque_id', 'mosque_Capacity', 'mosque_postalcode',
            'mosque_address', 'mosque_phone', 'created_phone', 'create_date',
            'persons', 'building', 'TrusteesBoard', 'question'
        ]

class SendToInsuranceSerializer(serializers.Serializer):
    # تعیین فیلدهای اصلی
    mosque_info = MainRegistrationSerializer(source='inform_main')
    insurance_info = InsuranceSerializer(source='inform_insurance')
    
    def to_representation(self, instance):
        # اضافه کردن اطلاعات اضافی اگر نیاز باشد
        representation = super().to_representation(instance)
        
        # اضافه کردن تاریخ و زمان ارسال
        from django.utils import timezone
        representation['sent_at'] = timezone.now().isoformat()
        representation['request_id'] = self.context.get('request_id', '')
        
        return representation