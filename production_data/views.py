from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # Để hiển thị thông báo thành công/lỗi
from .forms import ProductionResultForm
from .models import ProductionResult, Profile, ProductModel, ProductGroup
from django.views.decorators.csrf import csrf_exempt
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

def load_product_models(request):
    group_id = request.GET.get('group_model')
    if not group_id:
        return JsonResponse([], safe=False)
    qs = ProductModel.objects.filter(group_model_id=group_id).order_by('code')
    data = list(qs.values('id', 'code', 'name'))
    return JsonResponse(data, safe=False)
@login_required
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
    # Lấy các tham số lọc/sắp xếp/phân trang
    date_filter = request.GET.get('date')
    name_filter = request.GET.get('product_model')
    sort = request.GET.get('sort', 'date')
    dir = request.GET.get('dir', 'desc')
    page_number = request.GET.get('page')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # 1. Lấy QuerySet ban đầu
    results = ProductionResult.objects.all()

    # 2. Lọc dữ liệu
    if date_filter:
        results = results.filter(date=date_filter)
    if name_filter:
        # Giả định product_model có trường 'code'
        results = results.filter(product_model__code__icontains=name_filter)
        
    # 3. Sắp xếp dữ liệu
    valid_fields = [f.name for f in ProductionResult._meta.fields]
    sort_field = sort if sort in valid_fields else 'date'
    
    if sort_field in valid_fields:
        if dir == 'desc':
            sort_field = f'-{sort_field}'
        results = results.order_by(sort_field)
    else:
         # Sắp xếp mặc định ban đầu nếu không có sắp xếp hợp lệ
        results = results.order_by('-date', 'product_model')

    # 4. Phân trang
    # Giữ số mục trên mỗi trang là 1
    paginator = Paginator(results, 20) # Đặt lại là 10 mục mỗi trang cho thực tế hơn

    try:
        results_page = paginator.page(page_number)
    except:
        results_page = paginator.page(1)

    # 5. Context
    context = {
        'results': results_page, # Truyền đối tượng Page
        'date_filter': date_filter or '',
        'name_filter': name_filter or '',
        'sort': sort,
        'dir': dir,
        'current_page': 'list',
        # 'totals': totals, # Nếu bạn cần tính tổng, hãy đảm bảo chỉ tính trên results đã được lọc
    }

    # 6. Trả lời AJAX hoặc HTML
    if is_ajax:
        # Chỉ render phần thân bảng và phân trang
        html_table_body = render_to_string(
            'production_data/_results_table_body.html', 
            context, 
            request=request
        )
        html_pagination = render_to_string(
            'production_data/_pagination.html', 
            context, 
            request=request
        )
        return JsonResponse({
            'html_table': html_table_body,
            'html_pagination': html_pagination
        })
    
    # Yêu cầu thông thường (tải trang lần đầu)
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
    filtered_results = ProductionResult.objects.filter(date__range=[start_date, end_date]).order_by('date', 'product_model__name')

    # Báo cáo tổng sản lượng theo ngày (cho biểu đồ đường hoặc cột)
    daily_production_summary = filtered_results.values('date').annotate(
        total_result=Sum('result'),
        total_pc_plan=Sum('pc_plan'),
        total_pro_plan=Sum('pro_plan'),
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

     # Báo cáo tổng sản lượng theo loại sản phẩm (cho biểu đồ cột hoặc bánh)
    production_by_type_summary = filtered_results.values('product_model__code').annotate(
        total_pc_plan=Sum('pc_plan'),
        total_pro_plan=Sum('pro_plan'),
        total_result=Sum('result'),
        total_pc_diff=Sum('pc_diff'),
        total_prod_diff=Sum('prod_diff'),
        avg_completion_rate=ExpressionWrapper(
            Coalesce(Sum('completion_rate') / NullIf(Count('id'), 0), 0),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        ),
        total_person_diff=Sum('person_diff', output_field=IntegerField())
    ).order_by('product_model__code')

    person_diff_by_model = filtered_results.values('product_model__name').annotate(
    total_person_diff=Sum('person_diff', output_field=IntegerField())
    ).order_by('product_model__name')

    production_by_group_model_summary = (
    filtered_results
    .values(
        'product_model__group_model__code',
    )
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
    .order_by('product_model__group_model__code')
)
    
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

    PER_PAGE_DATE = 1
    PER_PAGE_TYPE = 1
    PER_PAGE_GROUP = 1

    # --- 3. Xử lý Phân trang & AJAX (CHỈ DÙNG 1 PAGINATOR Ở ĐÂY) ---
    page_number = request.GET.get('page', 1)
    table_id = request.GET.get('table', 'tableProdByGroupModel')

    # 3.1. Xác định QuerySet, Template và Per_page cho request hiện tại
    if table_id == 'tableProdByDate':
        queryset_to_paginate = daily_production_summary
        current_per_page = PER_PAGE_DATE
        template_name = 'production_data/partials/daily_production_table.html'
        context_key = 'daily_production_summary'
    elif table_id == 'tableProdByType':
        queryset_to_paginate = production_by_type_summary
        current_per_page = PER_PAGE_TYPE
        template_name = 'production_data/partials/by_type_production_table.html'
        context_key = 'production_by_type_summary'
    else: # tableProdByGroupModel
        queryset_to_paginate = production_by_group_model_summary
        current_per_page = PER_PAGE_GROUP
        template_name = 'production_data/partials/by_group_model_table.html'
        context_key = 'production_by_group_model_summary'

    # Thực hiện phân trang cho request hiện tại (dùng cho AJAX)
    paginator = Paginator(queryset_to_paginate, current_per_page)
    try:
        current_page_items = paginator.page(page_number)
    except Exception:
        current_page_items = paginator.page(1)

    # --- Xử lý yêu cầu AJAX ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        ajax_context = {
            context_key: current_page_items,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        }
        html_content = render_to_string(template_name, ajax_context, request=request)
        return JsonResponse({'html': html_content, 'table_id': table_id})

    # Tạo các paginator cho mỗi bảng (dùng để render lần đầu)
    daily_paginator = Paginator(daily_production_summary, PER_PAGE_DATE)
    type_paginator = Paginator(production_by_type_summary, PER_PAGE_TYPE)
    group_paginator = Paginator(production_by_group_model_summary, PER_PAGE_GROUP)
    
    # Chuyển đổi dữ liệu cho Chart.js (giữ nguyên logic cũ)
    dates = [item['date'].strftime('%Y-%m-%d') for item in daily_production_summary]
    prod_results = [item['total_result'] for item in daily_production_summary]
    pc_plans = [item['total_pc_plan'] for item in daily_production_summary]
    
    model_labels = [item['product_model__name'] for item in person_diff_by_model]
    model_person_diffs = [item['total_person_diff'] for item in person_diff_by_model]
    
    type_labels = [item['product_model__code'] for item in production_by_type_summary]
    type_prod_results = [item['total_result'] for item in production_by_type_summary]
    type_pc_plans = [item['total_pc_plan'] for item in production_by_type_summary]
    person_diffs = [item['total_person_diff'] for item in daily_production_summary]
    
    group_model_labels = [item['product_model__group_model__code'] for item in production_by_group_model_summary]
    group_model_pc_plans = [item['total_pc_plan'] for item in production_by_group_model_summary]
    group_model_results = [item['total_result'] for item in production_by_group_model_summary]

    # --- Xử lý HTTP Request thông thường (Lần tải trang đầu tiên) ---

    # Chuyển đổi dữ liệu cho Chart.js
    dates = [item['date'].strftime('%Y-%m-%d') for item in daily_production_summary]
    prod_results = [item['total_result'] for item in daily_production_summary]
    pc_plans = [item['total_pc_plan'] for item in daily_production_summary]
    model_labels = [item['product_model__name'] for item in person_diff_by_model]
    model_person_diffs = [item['total_person_diff'] for item in person_diff_by_model]
    # Dữ liệu cho biểu đồ tổng sản lượng theo loại
    type_labels = [item['product_model__code'] for item in production_by_type_summary]
    type_prod_results = [item['total_result'] for item in production_by_type_summary]
    type_pc_plans = [item['total_pc_plan'] for item in production_by_type_summary]
    person_diffs = [item['total_person_diff'] for item in daily_production_summary]
    # Dữ liệu chart (luôn full dataset)
    group_model_labels = [item['product_model__group_model__code'] for item in production_by_group_model_summary]
    group_model_pc_plans  = [item['total_pc_plan'] for item in production_by_group_model_summary]
    group_model_results  = [item['total_result'] for item in production_by_group_model_summary]


  

    context = {
        'current_page': 'report',
        'sort': request.GET.get('sort', 'date'),
        'dir': request.GET.get('dir', 'asc'),
        'date_filter': request.GET.get('date_filter', ''),
        'name_filter': request.GET.get('product_model', ''),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        # Gán kết quả phân trang cho lần tải đầu tiên (dùng để render)
        'daily_production_summary': daily_paginator.page(1),
        'production_by_type_summary': type_paginator.page(1),
        'production_by_group_model_summary': group_paginator.page(1),
        'grand_totals': grand_totals,
        

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
        'chart_group_model_labels': json.dumps(group_model_labels),
        'chart_group_model_pc_plans': json.dumps(group_model_pc_plans),
        'chart_group_model_results': json.dumps(group_model_results),
    }
    return render(request, 'production_data/production_report.html', context)



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