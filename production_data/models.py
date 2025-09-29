from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # Để sử dụng timezone.now cho trường ngày tháng


class Line(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã Line")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên Line")

    def __str__(self):
        return self.code
class ProductModel(models.Model):
    code = models.CharField(max_length=255, unique=True, verbose_name="Mã Model")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên Model")
    group_model = models.ForeignKey('ProductGroup', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nhóm Model")

    def __str__(self):
        return self.code
    
class Group(models.Model):
    code = models.CharField(max_length=50, verbose_name="Mã Group")  # VD: MDU-11
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên Group")

    def __str__(self):
        return f"{self.code} - {self.line.code}"

class Shift(models.Model):
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="shifts")
    name = models.CharField(max_length=50, verbose_name="Ca")  # VD: 1st, 2nd, 3rd
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.line.code})"
    
class ProductGroup(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã nhóm model")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên nhóm")

    def __str__(self):
        return self.code


class ProductionResult(models.Model):
    # Thông tin chung
    # Sử dụng CharField cho date để dễ dàng hiển thị theo format DD/MM/YYYY trên form nếu cần,
    # hoặc DateField nếu bạn muốn lưu trữ dạng ngày tháng thực sự và validate
    date = models.DateField(default=timezone.now, verbose_name="Ngày")
    user_input = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người nhập liệu") # Có thể làm khóa ngoại tới User model sau này

    line = models.ForeignKey(Line, on_delete=models.CASCADE, verbose_name="Line", null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name="Ca", null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Group", null=True, blank=True)
    product_model = models.ForeignKey(ProductModel, on_delete=models.CASCADE, verbose_name="Model", null=True, blank=True)

   

    # (Yesterday PLN/RSLT)
    pc_plan = models.IntegerField(verbose_name="PC PLAN", null=True, blank=True) # Trường mới
    pro_plan = models.IntegerField(verbose_name="PRO PLAN", null=True, blank=True) # Trường mới
    result = models.IntegerField(verbose_name="RESULT", null=True, blank=True) # Trường mới
    pc_diff = models.IntegerField(verbose_name="PC 差異 (Chênh lệch)", blank=True, null=True) # Có thể tính toán tự động
    prod_diff = models.IntegerField(verbose_name="PROD 差異 (Chênh lệch)", blank=True, null=True) # Có thể tính toán tự động
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Đạt tỉ lệ (%)", blank=True, null=True) # Có thể tính toán tự động
    

    # Giờ làm việc
    to_assess = models.CharField(max_length=10, blank=True, null=True, verbose_name="TO ASSESS") # Ví dụ: O/X
    hour_pc_plan = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="HOUR PC PLAN", blank=True, null=True) # Có thể tính toán tự động
    hour_pro_plan = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="HOUR PRO" , blank=True, null=True) # Có thể tính toán tự động
    hour_actual = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="HOUR Thực lĩnh", blank=True, null=True) # Có thể tính toán tự động
    qty_hour = models.IntegerField(verbose_name="QTY/HOUR",blank=True, null=True) # Số lượng trên mỗi giờ

    # Tổng hợp & Đánh giá
    po_plan_ref = models.IntegerField(verbose_name="PO PLAN-REF", blank=True, null=True) # Có thể tính toán tự động
    pc_plan_ref_2 = models.IntegerField(verbose_name="PC PLAN REF 2", blank=True, null=True) # Có thể tính toán tự động
    actuals = models.IntegerField(verbose_name="Kết quả (Actuals)", blank=True, null=True) # Có thể tính toán tự động
    difference = models.IntegerField(verbose_name="Balance", blank=True, null=True) # Có thể tính toán tự động
    plan_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Đạt tỉ lệ (%) (Plan)", blank=True, null=True) # Có thể tính toán tự động
    total = models.IntegerField(verbose_name="TOTAL", blank=True, null=True) # Có thể tính toán tự động
    acc_ng = models.IntegerField(verbose_name="ACC NG", blank=True, null=True) # Có thể tính toán tự động

    # input output
    input_material = models.IntegerField(verbose_name="Input Material", blank=True, null=True) # Có thể tính toán tự động
    output = models.IntegerField(verbose_name="Output", blank=True, null=True) # Có thể tính toán tự động
    output_before = models.IntegerField(verbose_name="Output Before",   blank=True, null=True) # Có thể tính toán tự động
    ng = models.IntegerField(verbose_name="NG", blank=True, null=True) # Có thể tính toán tự động
    input_actual = models.IntegerField(verbose_name="Input actual", blank=True, null=True) # Có thể tính toán tự động

    # so nguoi
    person_standard = models.IntegerField(verbose_name="Person Standard", blank=True, null=True) # Có thể tính toán tự động
    person_actual = models.IntegerField(verbose_name="Person Actual", blank=True, null=True) # Có thể tính toán tự động
    person_diff = models.IntegerField(verbose_name="Person Diff", blank=True, null=True) # Có thể tính toán tự động   



    # Trường tự động tạo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kết quả Sản xuất"
        verbose_name_plural = "Kết quả Sản xuất"
        ordering = ['-date', 'product_model__code'] # Sắp xếp mặc định

    def __str__(self):
        return f"{self.product_model.code} - {self.date.strftime('%d/%m/%Y')} bởi {self.user_input or 'N/A'}"


    # Bạn có thể thêm các phương thức tính toán tự động ở đây
    def save(self, *args, **kwargs):
        if self.pc_plan_ref_2 and self.actuals:
            self.difference = self.actuals - self.pc_plan_ref_2
        if self.person_standard and self.person_actual:
            self.person_diff =   self.person_standard-self.person_actual
        if self.pc_plan and self.result:
            if self.pc_plan != 0:
                self.completion_rate = (self.result / self.pc_plan) * 100
            else:
                self.completion_rate = 0.00 # Tránh chia cho 0
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username
