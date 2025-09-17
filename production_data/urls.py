from django.urls import path
from . import views

urlpatterns = [
    path('', views.production_results_list, name='production_results_list'), # Trang danh sách
    path('enter/', views.data_entry_view, name='data_entry'), # Trang nhập liệu
    path('list/', views.production_results_list, name='production_results_list'), # Trang danh sách
    path('detail/<int:pk>/', views.production_result_detail, name='production_result_detail'), # Xem chi tiết
    path('update/<int:pk>/', views.production_result_update, name='production_result_update'), # Cập nhật
    path('delete/<int:pk>/', views.production_result_delete, name='production_result_delete'), # Xóa
    path('report/', views.production_report, name='production_report'), # Trang báo cáo/thống kê
]