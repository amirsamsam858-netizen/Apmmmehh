import os
import threading
import requests
import zipfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform

class MinecraftLauncher(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=40, spacing=20, **kwargs)
        
        # --- طراحی ظاهر (UI) ---
        self.add_widget(Label(text="MINECRAFT DOWNLOADER", font_size='30sp', color=(0.2, 0.8, 0.2, 1)))
        
        self.status_label = Label(text="آماده برای شروع", font_size='18sp')
        self.add_widget(self.status_label)
        
        self.progress_bar = ProgressBar(max=100, value=0)
        self.add_widget(self.progress_bar)
        
        self.download_btn = Button(
            text="شروع دانلود و نصب", 
            size_hint=(1, 0.3),
            background_color=(0, 0.6, 0, 1),
            font_size='20sp'
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        self.add_widget(self.download_btn)

        # --- تنظیم مسیر ذخیره‌سازی ---
        if platform == 'android':
            # در اندروید، فایل‌ها در پوشه دانلود ذخیره می‌شوند
            from android.storage import primary_external_storage_path
            self.base_path = os.path.join(primary_external_storage_path(), "Download", "Minecraft_Files")
        else:
            # در ویندوز/مک برای تست
            self.base_path = os.path.join(os.getcwd(), "Minecraft_Files")
            
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def update_ui(self, text, progress, btn_disabled):
        """به‌روزرسانی رابط کاربری از طریق Clock برای جلوگیری از Crash"""
        self.status_label.text = text
        self.progress_bar.value = progress
        self.download_btn.disabled = btn_disabled

    def start_download_thread(self, instance):
        """ایجاد یک رشته جدید برای دانلود تا UI قفل نشود"""
        threading.Thread(target=self.download_process, daemon=True).start()

    def download_process(self):
        # --- تنظیمات نسخه ---
        version_name = "Version_1_20"
        # !!! اینجا لینک مستقیم فایل زیپ خود را جایگزین کنید !!!
        download_url = "https://cdn.imgurl.ir/uploads/j8535___.zip" 
        
        target_zip = os.path.join(self.base_path, f"{version_name}.zip")
        extract_folder = os.path.join(self.base_path, version_name)

        try:
            self.update_ui("در حال اتصال به سرور...", 0, True)
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(target_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024): # دانلود تکه تکه 1 مگابایتی
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # محاسبه درصد
                        if total_size > 0:
                            percent = (downloaded_size / total_size) * 100
                            # ارسال اطلاعات به UI اصلی
                            Clock.schedule_once(lambda dt: self.update_ui(f"در حال دانلود: {int(percent)}%", percent, True))

            # مرحله استخراج
            self.update_ui("دانلود تمام شد. در حال استخراج...", 100, True)
            
            with zipfile.ZipFile(target_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
            
            # حذف فایل زیپ برای آزاد سازی فضا
            os.remove(target_zip)

            self.update_ui("نصب با موفقیت انجام شد!", 100, False)
            
        except Exception as e:
            self.update_ui(f"خطا: {str(e)}", 0, False)
            print(f"Error: {e}")

class MinecraftApp(App):
    def build(self):
        return MinecraftLauncher()

if __name__ == "__main__":
    MinecraftApp().run()
