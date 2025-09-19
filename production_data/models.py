from django.db import models
from django.utils import timezone # Để sử dụng timezone.now cho trường ngày tháng

class ProductionResult(models.Model):
    # Thông tin chung
    # Sử dụng CharField cho date để dễ dàng hiển thị theo format DD/MM/YYYY trên form nếu cần,
    # hoặc DateField nếu bạn muốn lưu trữ dạng ngày tháng thực sự và validate
    date = models.DateField(default=timezone.now, verbose_name="Ngày")
    user_input = models.CharField(max_length=100, default="TUYẾT-13749", verbose_name="Người nhập liệu") # Có thể làm khóa ngoại tới User model sau này

    line = models.CharField(max_length=50, blank=True, null=True, verbose_name="LINE") # Ví dụ: NSAA01, NSKA01
    group = models.CharField(max_length=50, blank=True, null=True, verbose_name="GROUP") # Ví dụ: MDU-11, MDU-13
    shift = models.CharField(max_length=50, blank=True, null=True, verbose_name="SHIFT") # Ví dụ: 1st, 3rd

    name_of_type = models.CharField(max_length=255, verbose_name="Mã sản phẩm (MODEL)") # Đổi verbose_name cho rõ hơn

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
    difference = models.IntegerField(verbose_name="Chênh lệch", blank=True, null=True) # Có thể tính toán tự động
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
        ordering = ['-date', 'name_of_type'] # Sắp xếp mặc định

    def __str__(self):
        return f"{self.name_of_type} - {self.date.strftime('%d/%m/%Y')} bởi {self.user_input}"

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

