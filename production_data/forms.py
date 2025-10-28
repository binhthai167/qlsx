from django import forms
from .models import ProductionResult,ProductModel, ProductGroup
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class ProductionResultForm(forms.ModelForm):
    group_model = forms.ModelChoiceField(
        queryset=ProductGroup.objects.all(),
        required=True,
        label="Nhóm Model",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = ProductionResult
        exclude = ['user_input']  # user_input tự động set, không cho nhập tay
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'product_model': forms.Select(attrs={'class': 'form-control'}),
            'pc_plan': forms.NumberInput(attrs={'class': 'form-control'}),
            'pro_plan': forms.NumberInput(attrs={'class': 'form-control'}),
            'result': forms.NumberInput(attrs={'class': 'form-control'}),
            'pc_diff': forms.NumberInput(attrs={'class': 'form-control'}),
            'prod_diff': forms.NumberInput(attrs={'class': 'form-control'}),
            'completion_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'step': '0.1'
            }),
            'hour_pc_plan': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'hour_pro_plan': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'hour_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
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
            'person_diff': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['product_model'].queryset = ProductModel.objects.none()
        self.fields['product_model'].required = True
        if self.instance and self.instance.product_model:
            pm = self.instance.product_model
            if pm.group_model:
                self.fields['group_model'].initial = pm.group_model
                self.fields['product_model'].queryset = ProductModel.objects.filter(group_model=pm.group_model).order_by('code')
            else:
                self.fields['product_model'].queryset = ProductModel.objects.filter(pk=pm.pk)

        # Nếu là POST (submit) và người dùng đã chọn group_model -> lọc product_model theo group đó
        if 'group_model' in self.data:
            try:
                group_id = int(self.data.get('group_model'))
                self.fields['product_model'].queryset = ProductModel.objects.filter(group_model_id=group_id).order_by('code')
            except (ValueError, TypeError):
                pass
            
        if user:
            self.fields['người_nhập'] = forms.CharField(
                initial=user.username,
                label="Người nhập liệu",
                disabled=True,
                required=False
            )
            self.user = user
            # đưa "người_nhập" lên đầu form
            self.order_fields(['người_nhập'] + list(self.fields.keys()))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(self, 'user'):
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