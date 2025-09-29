from django.contrib import admin
from .models import ProductionResult, Line, Shift, Group, ProductModel, ProductGroup
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Resource ngay trong admin.py
class ProductionResultResource(resources.ModelResource):
    class Meta:
        model = ProductionResult
        # có thể thêm exclude nếu muốn bỏ bớt cột:
        # exclude = ('id', 'created_at', 'updated_at')
        # hoặc chỉ định field cụ thể:
        # fields = ('date', 'user_input', 'name_of_type', 'pc_plan', 'actuals')
@admin.register(ProductionResult)
class ProductionResultAdmin(ImportExportModelAdmin):
    list_display = (
        'date', 'user_input', 'pc_plan', 'pro_plan', 'result', 'pc_diff',
        'prod_diff', 'completion_rate', 'hour_pc_plan', 'hour_pro_plan', 'hour_actual', 'qty_hour', 'difference',
        'po_plan_ref', 'pc_plan_ref_2', 'actuals', 'difference', 'ng', 'plan_percentage', 'created_at', 'updated_at'
    )
    list_filter = ('date', 'user_input', )
    date_hierarchy = 'date' # Thêm bộ lọc theo ngày trên thanh công cụ
    readonly_fields = ('prod_diff', 'completion_rate', 'difference', 'plan_percentage', 'created_at', 'updated_at') # Các trường tính toán tự động

@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('code',)

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'group_model')
    search_fields = ('code', 'name')
    list_filter = ('group_model',)