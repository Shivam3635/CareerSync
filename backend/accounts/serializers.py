from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from students.models import StudentProfile, StudentQualification

User = get_user_model()


class StudentQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentQualification
        fields = ['id', 'level', 'degree', 'status', 'passing_year', 'percentage']


class StudentProfileSerializer(serializers.ModelSerializer):
    qualifications = StudentQualificationSerializer(many=True, read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'date_of_birth', 'gender', 'category', 'domicile_state', 'additional_certifications', 'qualifications']


class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'student_profile', 'created_at']


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    full_name = serializers.CharField(max_length=255)
    
    # Profile fields
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=StudentProfile.GENDER_CHOICES, default='other')
    category = serializers.ChoiceField(choices=StudentProfile.CATEGORY_CHOICES, default='GEN')
    domicile_state = serializers.CharField(max_length=100, default='All India')
    
    # Primary qualification
    highest_qualification = serializers.ChoiceField(choices=StudentQualification.LEVEL_CHOICES, default='Graduate')
    qualification_status = serializers.ChoiceField(choices=StudentQualification.STATUS_CHOICES, default='completed')
    degree = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        full_name = validated_data['full_name']

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role='student'
        )

        profile = StudentProfile.objects.create(
            user=user,
            date_of_birth=validated_data['date_of_birth'],
            gender=validated_data['gender'],
            category=validated_data['category'],
            domicile_state=validated_data['domicile_state'],
        )

        StudentQualification.objects.create(
            student=profile,
            level=validated_data['highest_qualification'],
            degree=validated_data.get('degree', ''),
            status=validated_data['qualification_status'],
            passing_year=None
        )

        return user


import os

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Must include both email and password.")

        # Ensure default superuser/admin exists if authenticating with authorized admin credentials
        authorized_admin_emails = [
            'singhshivamop36@gmail.com',
            'admin@careersync.in',
            os.getenv('ADMIN_EMAIL', '').strip().lower()
        ]
        admin_pass = os.getenv('ADMIN_PASSWORD', 'Admin@CareerSync2026')

        if email in authorized_admin_emails and password == admin_pass:
            admin_user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'full_name': 'Shivam Singh (Admin)',
                    'role': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            admin_user.set_password(admin_pass)
            admin_user.role = 'admin'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            user = admin_user
        else:
            user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        attrs['user'] = user
        return attrs
