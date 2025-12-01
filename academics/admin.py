from django.contrib import admin

from .models import AthleteExam, Exam, Highschool, University, UniversityEmailDomain

admin.site.register(Highschool)
admin.site.register(University)
admin.site.register(Exam)
admin.site.register(AthleteExam)
admin.site.register(UniversityEmailDomain)
