from django.contrib import admin
from .models import StudentProfile, StudentQualification


class StudentQualificationInline(admin.TabularInline):
    model = StudentQualification
    extra = 1


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'category', 'domicile_state', 'date_of_birth', 'created_at')
    list_filter = ('category', 'gender', 'domicile_state')
    search_fields = ('user__email', 'user__full_name', 'domicile_state')
    inlines = [StudentQualificationInline]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Student Email"


@admin.register(StudentQualification)
class StudentQualificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'level', 'degree', 'status', 'passing_year', 'percentage')
    list_filter = ('level', 'status')
    search_fields = ('student__user__email', 'degree')
