from django import forms
from helpboard.models import Problem


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem

        fields = [
            "title",
            "short_description",
            "description",
            "category",
            "location",
            "image",
        ]

        labels = {
            "title": "Problem Title",
            "short_description": "Short Description",
            "description": "Detailed Description",
            "category": "Problem Category",
            "location": "Location",
            "image": "Upload Image (optional)",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a clear and concise problem title",
                }
            ),
            "short_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Briefly describe the issue",
                    "rows": 3,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Explain the problem in detail",
                    "rows": 6,
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "City, Region, or specific location (e.g., Downtown Area, School District)",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }
