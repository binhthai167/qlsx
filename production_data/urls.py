from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.production_report, name='production_report'), # Trang báo cáo/thống kê
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path('enter/', views.data_entry_view, name='data_entry'), # Trang nhập liệu
    path('list/', views.production_results_list, name='production_results_list'), # Trang danh sách
    path('detail/<int:pk>/', views.production_result_detail, name='production_result_detail'), # Xem chi tiết
    path('update/<int:pk>/', views.production_result_update, name='production_result_update'), # Cập nhật
    path('delete/<int:pk>/', views.production_result_delete, name='production_result_delete'), # Xóa
    path('report/', views.production_report, name='production_report'), # Trang báo cáo/thống kê
    path('setting/', views.production_setting, name='production_setting'), # Trang setting
    path('ajax/load-product-models/', views.load_product_models, name='ajax_load_product_models'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)