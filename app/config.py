
# تنظیم حالت موبایل یا دسکتاپ
import os
IS_MOBILE = True  # اگر True باشد، حالت موبایل فعال است

# تابع کمکی برای مسیر استاتیک
def get_static_path(path: str) -> str:
    if IS_MOBILE:
        return f"mobile/{path}"
    else:
        return f"desktop/{path}"

# تابع مرکزی برای تعیین دایرکتوری اصلی فایل‌ها
def get_base_dir() -> str:
    if IS_MOBILE:
        return "/sdcard/Share"
    else:
        return os.getcwd()
