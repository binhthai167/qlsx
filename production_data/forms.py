from django import forms
from .models import ProductionResult
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class ProductionResultForm(forms.ModelForm):
    class Meta:
        model = ProductionResult
        exclude = ['user_input']  # user_input tự động set, không cho nhập tay
        labels = {
            'date': 'Ngày',
            'name_of_type': 'Mã sản phẩm',
            'pc_plan': 'PC PLAN',
            'pro_plan': 'PRO PLAN',
            'result': 'RESULT',
            'pc_diff': 'PC 差異 (Chênh lệch)',
            'prod_diff': 'PROD 差異 (Chênh lệch)',
            'completion_rate': 'Đạt tỉ lệ (%)',
            'hour_pc_plan': 'HOUR PC PLAN',
            'hour_pro_plan': 'HOUR PRO',
            'hour_actual': 'HOUR Thực lĩnh',
            'qty_hour': 'OUT HOUR',
            'po_plan_ref': 'PO PLAN-REF',
            'pc_plan_ref_2': 'PC PLAN REF 2',
            'actuals': 'Kết quả (Actuals)',
            'total': 'TOTAL',
            'ng': 'NG',
            'acc_ng': 'ACC NG',
            'input_material': 'Input Material',
            'output': 'Output',
            'output_before': 'Output Before',
            'input_actual': 'Input actual',
            'person_standard': 'Person Standard',
            'person_actual': 'Person Actual',
            'person_diff': 'Person Diff',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name_of_type': forms.TextInput(attrs={'class': 'form-control'}),
            'pc_plan': forms.NumberInput(attrs={'class': 'form-control'}),
            'pro_plan': forms.NumberInput(attrs={'class': 'form-control'}),
            'result': forms.NumberInput(attrs={'class': 'form-control'}),
            'pc_diff': forms.NumberInput(attrs={'class': 'form-control'}),
            'prod_diff': forms.NumberInput(attrs={'class': 'form-control'}),
            'completion_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'step': '0.01'
            }),
            'hour_pc_plan': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hour_pro_plan': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hour_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'qty_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'po_plan_ref': forms.NumberInput(attrs={'class': 'form-control'}),
            'pc_plan_ref_2': forms.NumberInput(attrs={'class': 'form-control'}),
            'actuals': forms.NumberInput(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control'}),
            'ng': forms.NumberInput(attrs={'class': 'form-control'}),
            'acc_ng': forms.NumberInput(attrs={'class': 'form-control'}),
            'input_material': forms.NumberInput(attrs={'class': 'form-control'}),
            'output': forms.NumberInput(attrs={'class': 'form-control'}),
            'output_before': forms.NumberInput(attrs={'class': 'form-control'}),
            'input_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'person_standard': forms.NumberInput(attrs={'class': 'form-control'}),
            'person_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'person_diff': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Thêm field readonly để hiển thị tên
            self.fields['người_nhập'] = forms.CharField(
                initial=user.username,
                label="Người nhập liệu",
                disabled=True,
                required=False
            )
            self.user = user

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:  # gán user hiện tại
            instance.user_input = self.user
        if commit:
            instance.save()
        return instance

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']   # chỉ cho phép upload avatar

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")