from django import forms
from .models import ProductionResult
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProductionResultForm(forms.ModelForm):
    class Meta:
        model = ProductionResult
        # Chỉ hiển thị các trường người dùng cần nhập
        # Các trường tính toán tự động sẽ không cần hiển thị trên form
        fields = [
            'date', 'user_input', 'name_of_type',
            'pc_plan','pro_plan','result', 'pc_diff', 'prod_diff', 'completion_rate',
            'hour_pc_plan', 'hour_pro_plan', 'hour_actual', 'qty_hour',
            'po_plan_ref', 'pc_plan_ref_2', 'actuals',
            'total', 'ng', 'acc_ng', 
            'input_material', 'output', 'output_before', 'input_actual',
            'person_standard', 'person_actual', 'person_diff',
        ]
        labels = {
            'date': 'Ngày',
            'user_input': 'Người nhập liệu',
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
            'user_input': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # Có thể làm readonly hoặc ẩn
            'name_of_type': forms.TextInput(attrs={'class': 'form-control'}),
            'pc_plan': forms.NumberInput(attrs={'class': 'form-control'}),
            'pro_plan': forms.NumberInput(attrs={'class': 'form-control'}),
            'result': forms.NumberInput(attrs={'class': 'form-control'}),
            'pc_diff': forms.NumberInput(attrs={'class': 'form-control'}),
            'prod_diff': forms.NumberInput(attrs={'class': 'form-control'}),
            'completion_rate': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'step': '0.01'}),
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
        user = kwargs.pop('user', None)  # lấy user từ kwargs (do view truyền vào)
        super().__init__(*args, **kwargs)

        # Nếu là form tạo mới thì set user mặc định
        if not self.instance.pk and user:
            self.initial['user_input'] = user.username

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")