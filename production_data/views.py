from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # Để hiển thị thông báo thành công/lỗi
from .forms import ProductionResultForm
from .models import ProductionResult, Profile
from django.db.models import Sum, F, ExpressionWrapper, DecimalField # Để tính tổng và tham chiếu trường
from django.utils import timezone
import json
from django.db.models import Sum,IntegerField
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce
from datetime import timedelta # Để tính toán ngày
from django.db.models import Count
from django.db.models.functions import NullIf
from django.db.models.functions import Substr
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib.auth.decorators import permission_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib import messages
from .forms import ProfileForm, UserUpdateForm
from django.contrib.auth import update_session_auth_hash




def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()   # Lưu user vào DB
            login(request, user) # Đăng nhập ngay sau khi đăng ký
            return redirect("login")  # Đổi "home" thành trang bạn muốn sau đăng ký
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

def data_entry_view(request):
    if request.method == 'POST':
        form = ProductionResultForm(request.POST, user=request.user)  # Truyền user hiện tại vào form
        if form.is_valid():
            form.save()
            messages.success(request, 'Dữ liệu đã được nhập thành công!')
            return redirect('data_entry')  # Chuyển hướng về trang nhập liệu sau khi lưu
        else:
            messages.error(request, 'Có lỗi xảy ra khi nhập liệu. Vui lòng kiểm tra lại.')
    else:
        # Nếu muốn hiển thị ngày hiện tại tự động
        initial_data = {'date': timezone.now().strftime('%Y-%m-%d')}
        form = ProductionResultForm(initial=initial_data, user=request.user)  # ⚡ thêm user vào đây

    context = {
        'form': form,
        'current_page': 'entry'  # Để active menu item
    }
    return render(request, 'production_data/data_entry.html', context)

@login_required
def production_results_list(request):
    date_filter = request.GET.get('date')
    name_filter = request.GET.get('name_of_type')
    # Lấy tất cả kết quả, sắp xếp theo ngày giảm dần và tên loại tăng dần
    results = ProductionResult.objects.all().order_by('-date', 'name_of_type')

    # Tính tổng cho các cột cần thiết, ví dụ:
    # totals = results.aggregate(
    #     total_pc_plan=Sum('pc_plan'),
    #     total_result=Sum('result'),
    #     total_prod_diff=Sum('prod_diff'),
    #     total_hour_pc_plan=Sum('hour_pc_plan'),
    #     # ... thêm các tổng khác
    # )
    if date_filter:
        results = results.filter(date=date_filter)
    if name_filter:
        results = results.filter(name_of_type__icontains=name_filter)
     # Sort dữ liệu
    sort = request.GET.get('sort', 'date')  # default sort by date
    dir = request.GET.get('dir', 'desc')     # default ascending
    valid_fields = [f.name for f in ProductionResult._meta.fields]  # tất cả field model
    if sort in valid_fields:
        if dir == 'desc':
            sort = f'-{sort}'
        results = results.order_by(sort)

     # Phân trang, mỗi trang 10 mục mặc định
    paginator = Paginator(results, 20)  
    page_number = request.GET.get('page')
    results = paginator.get_page(page_number)


    context = {
        'results': results,
        'date_filter': date_filter,
        'name_filter': name_filter,
        # 'totals': totals,
        'current_page': 'list', # Để active menu item
        'sort': request.GET.get('sort', ''),
        'dir': request.GET.get('dir', ''),

    }
    return render(request, 'production_data/production_results_list.html', context)

@login_required
def production_result_detail(request, pk):
    result = get_object_or_404(ProductionResult, pk=pk)
    context = {
        'result': result,
        'current_page': 'list'
    }
    return render(request, 'production_data/production_result_detail.html', context)

def production_result_update(request, pk):
    result = get_object_or_404(ProductionResult, pk=pk)
    if request.method == 'POST':
        form = ProductionResultForm(request.POST, instance=result, user=request.user)  # Truyền user hiện tại vào form
        if form.is_valid():
            form.save()
            messages.success(request, 'Dữ liệu đã được cập nhật thành công!')
            return redirect('production_results_list')
        else:
            messages.error(request, 'Có lỗi xảy ra khi cập nhật dữ liệu. Vui lòng kiểm tra lại.')
    else:
        form = ProductionResultForm(instance=result)

    context = {
        'form': form,
        'result': result,
        'current_page': 'list'
    }
    return render(request, 'production_data/data_entry.html', context) # Dùng lại template nhập liệu

def production_result_delete(request, pk):
    result = get_object_or_404(ProductionResult, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Dữ liệu đã được xóa thành công!')
        return redirect('production_results_list')
    context = {
        'result': result,
        'current_page': 'list'
    }
    return render(request, 'production_data/production_result_confirm_delete.html', context)

@login_required
# @permission_required('production_data.view_productionresult', raise_exception=True)
def production_report(request):
    # Lấy các tham số lọc từ request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Xử lý ngày lọc
    today = timezone.now().date()
    # Mặc định là 7 ngày gần nhất nếu không có ngày lọc
    default_start_date = today - timedelta(days=6) # 7 ngày bao gồm hôm nay
    default_end_date = today

    try:
        start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else default_start_date
        end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else default_end_date
    except ValueError:
        messages.error(request, 'Định dạng ngày không hợp lệ. Vui lòng sử dụng YYYY-MM-DD.')
        start_date = default_start_date
        end_date = default_end_date

    # Đảm bảo ngày bắt đầu không lớn hơn ngày kết thúc
    if start_date > end_date:
        start_date, end_date = end_date, start_date # Hoán đổi nếu không hợp lệ
        messages.warning(request, 'Ngày bắt đầu không được lớn hơn ngày kết thúc. Đã điều chỉnh.')

    # Lọc dữ liệu theo khoảng ngày
    filtered_results = ProductionResult.objects.filter(date__range=[start_date, end_date]).order_by('date', 'name_of_type')

    # Báo cáo tổng sản lượng theo ngày (cho biểu đồ đường hoặc cột)
    daily_production_summary = filtered_results.values('date').annotate(
        total_result=Sum('result'),
        total_pc_plan=Sum('pc_plan'),
        total_pc_diff=Sum('pc_diff'),
        total_prod_diff=Sum('prod_diff'),
        total_person_diff=Sum('person_diff', output_field=IntegerField()),
        avg_completion_rate=ExpressionWrapper(
            Coalesce(Sum('completion_rate') / NullIf(Count('id'), 0), 0),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        ),
        total_hour_pc_plan=Sum('hour_pc_plan'),
        total_hour_pro_plan=Sum('hour_pro_plan'),
        total_hour_prod_diff=Sum(
            ExpressionWrapper(F('hour_actual') - F('hour_pro_plan'), output_field=DecimalField())
        ),
    ).order_by('date')

    person_diff_by_model = filtered_results.values('name_of_type').annotate(
    total_person_diff=Sum('person_diff', output_field=IntegerField())
    ).order_by('name_of_type')

    # Chuyển đổi dữ liệu cho Chart.js
    dates = [item['date'].strftime('%Y-%m-%d') for item in daily_production_summary]
    prod_results = [item['total_result'] for item in daily_production_summary]
    pc_plans = [item['total_pc_plan'] for item in daily_production_summary]
    model_labels = [item['name_of_type'] for item in person_diff_by_model]
    model_person_diffs = [item['total_person_diff'] for item in person_diff_by_model]

    # Báo cáo tổng sản lượng theo loại sản phẩm (cho biểu đồ cột hoặc bánh)
    production_by_type_summary = filtered_results.values('name_of_type').annotate(
        total_pc_plan=Sum('pc_plan'),
        total_pro_plan=Sum('pro_plan'),
        total_result=Sum('result'),
        total_pc_diff=Sum('pc_diff'),
        total_prod_diff=Sum('prod_diff'),
        total_completion_rate=Sum('completion_rate'),
        total_person_diff=Sum('person_diff', output_field=IntegerField())
    ).order_by('name_of_type')
        # Dữ liệu cho biểu đồ tổng sản lượng theo loại
    type_labels = [item['name_of_type'] for item in production_by_type_summary]
    type_prod_results = [item['total_result'] for item in production_by_type_summary]
    type_pc_plans = [item['total_pc_plan'] for item in production_by_type_summary]
    person_diffs = [item['total_person_diff'] for item in daily_production_summary]



    # Tính tổng cho bảng tóm tắt
    grand_totals = filtered_results.aggregate(
        overall_total_pc_plan=Sum('pc_plan'),
        overall_total_pro_plan=Sum('pro_plan'),
        overall_total_result=Sum('result'),
        overall_total_prod_diff=Sum('prod_diff'),
        overall_total_hour_pc_plan=Sum('hour_pc_plan'),
        overall_total_hour_prod_plan=Sum('hour_pro_plan'),
        overall_total_hour_prod_diff=Sum(
        ExpressionWrapper(F('hour_actual') - F('hour_pro_plan'), output_field=DecimalField())
        
    ),
        overall_total_person_diff=Sum('person_diff', output_field=IntegerField()),
        overall_total_hour_actual=Sum('hour_actual'),
        # overall_total_actual_shift_a=Sum('actual_shift_a'),
        # overall_total_actual_shift_b=Sum('actual_shift_b'),
        # overall_total_actual_shift_c=Sum('actual_shift_c'),
        # overall_total_ot=Sum('ot'),
        # overall_total_total_actual=Sum('total_actual'),
        # overall_total_actual_diff=Sum('actual_diff'),
    )

    production_by_prefix_summary = (
    filtered_results
    .annotate(prefix=Substr('name_of_type', 1, 4))
    .values('prefix')
    .annotate(
        total_pc_plan=Sum('pc_plan'),
        total_pro_plan=Sum('pro_plan'),
        total_result=Sum('result'),
        total_pc_diff=Sum('pc_diff'),
        total_prod_diff=Sum('prod_diff'),
        avg_completion_rate=ExpressionWrapper(
            Coalesce(Sum('completion_rate') / NullIf(Count('id'), 0), 0),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        ),
        
    )
    .order_by('prefix')
)

    # Dữ liệu chart (luôn full dataset)
    prefix_labels = [item['prefix'] for item in production_by_prefix_summary]
    prefix_pc_plans = [item['total_pc_plan'] for item in production_by_prefix_summary]
    prefix_results = [item['total_result'] for item in production_by_prefix_summary]


  

    page = request.GET.get('page', 1)
    per_page = 5 
    paginator_type = Paginator(production_by_type_summary, per_page)
    paginator_prefix = Paginator(production_by_prefix_summary, per_page)
    paginator_daily = Paginator(daily_production_summary, per_page)

    #sort
    sort_field = request.GET.get('sort', 'date')  # default sort by 'date'
    sort_dir = request.GET.get('dir', 'asc')      # default ascending

    valid_fields = [f.name for f in ProductionResult._meta.fields]

    if sort_field in valid_fields:
        if sort_dir == 'desc':
            sort_field = f'-{sort_field}'
        filtered_results = filtered_results.order_by(sort_field)


    context = {
        'current_page': 'report',
        'sort': request.GET.get('sort', 'date'),
        'dir': request.GET.get('dir', 'asc'),
        'date_filter': request.GET.get('date_filter', ''),
        'name_filter': request.GET.get('name_of_type', ''),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'daily_production_summary': paginator_daily.get_page(page), # Bảng chi tiết
        'production_by_type_summary': paginator_type.get_page(page), # Bảng chi tiết theo loại
        'grand_totals': grand_totals,
        'production_by_prefix_summary': paginator_prefix.get_page(page), # Bảng chi tiết theo tiền tố
        


        # Dữ liệu cho Chart.js
        'chart_dates': json.dumps(dates),
        'chart_prod_results': json.dumps(prod_results),
        'chart_pc_plans': json.dumps(pc_plans),
        'chart_type_labels': json.dumps(type_labels),
        'chart_type_prod_results': json.dumps(type_prod_results),
        'chart_type_pc_plans': json.dumps(type_pc_plans),
        'chart_person_diffs': json.dumps(person_diffs),
        'chart_model_labels': json.dumps(model_labels),
        'chart_model_person_diffs': json.dumps(model_person_diffs),
        'chart_prefix_labels': json.dumps(prefix_labels),
        'chart_prefix_pc_plans': json.dumps(prefix_pc_plans),
        'chart_prefix_results': json.dumps(prefix_results),
    }
    return render(request, 'production_data/production_report.html', context)

@login_required
def production_setting(request):
    context = {
        'current_page': 'setting'
    }
    return render(request, 'production_data/production_setting.html', context)

def ajax_filter_results(request):
    # Lấy tham số từ yêu cầu
    name_filter = request.GET.get("name_of_type", "").strip()
    date_filter = request.GET.get("date", "")
    sort = request.GET.get("sort", "date")
    dir = request.GET.get("dir", "asc")
    page = request.GET.get("page", 1)

    # Lấy dữ liệu
    results = ProductionResult.objects.all()

    # Lọc
    if name_filter:
        results = results.filter(name_of_type__icontains=name_filter)
    if date_filter:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_filter, "%Y-%m-%d").date()
            results = results.filter(date=date_obj)
        except ValueError:
            # Nếu ngày không hợp lệ, trả về dữ liệu rỗng
            results = results.none()

    # Sắp xếp
    if sort:
        if dir == "desc":
            sort = f"-{sort}"
        results = results.order_by(sort)

    # Phân trang
    paginator = Paginator(results, 10)  # 10 bản ghi mỗi trang
    page_obj = paginator.get_page(page)

    # Debug: In dữ liệu để kiểm tra


    # Render HTML cho tbody và phân trang
    context = {
        "results": page_obj,
        "date_filter": date_filter,
        "name_filter": name_filter,
        "sort": sort.lstrip("-"),
        "dir": dir,
    }
    html = render_to_string("production_data/_results_table_body.html", context, request=request)
    # pagination_html = render_to_string("production_data/_pagination.html", context, request=request)

    return JsonResponse({
        "html": html,
        # "pagination": pagination_html
    })

@login_required
def production_setting(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid():
            # Lưu avatar
            profile_form.save()

            # Cập nhật thông tin user cơ bản
            user.email = request.POST.get('email', user.email)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)

            # Nếu có mật khẩu mới thì đổi mật khẩu
            new_password = request.POST.get('password', None)
            if new_password:
                user.set_password(new_password)

            user.save()

            messages.success(request, "Cập nhật tài khoản thành công!")
            return redirect('production_setting')  # reload lại trang
        else:
            messages.error(request, "Có lỗi xảy ra, vui lòng kiểm tra lại.")
    else:
        profile_form = ProfileForm(instance=profile)

    context = {
        'profile_form': profile_form,
        'user': user,
    }
    return render(request, 'production_data/production_settings.html', context)