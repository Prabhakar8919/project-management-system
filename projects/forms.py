from django import forms
from .models import Project, Category


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'student_name', 'roll_number', 'project_link', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Project title'}),
            'student_name': forms.TextInput(attrs={'placeholder': 'Student name'}),
            'roll_number': forms.TextInput(attrs={'placeholder': 'Roll number'}),
            'project_link': forms.URLInput(attrs={'placeholder': 'Deployed project URL (optional)'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your project', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'select-field'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Category name'}),
        }
