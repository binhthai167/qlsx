from django.contrib import admin
from .models import ProductionResult

@admin.register(ProductionResult)
class ProductionResultAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'user_input', 'name_of_type', 'pc_plan', 'pro_plan', 'result',
        'prod_diff', 'completion_rate', 'hour_actual', 'actuals', 'difference',
        'total', 'ng', 'acc_ng'
    )
    list_filter = ('date', 'user_input', 'name_of_type')
    search_fields = ('name_of_type', 'user_input')
    date_hierarchy = 'date' # Thêm bộ lọc theo ngày trên thanh công cụ
    readonly_fields = ('prod_diff', 'completion_rate', 'difference', 'plan_percentage', 'created_at', 'updated_at') # Các trường tính toán tự động