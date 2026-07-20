import os
import requests
import zipfile
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

class LauncherUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=50, spacing=20, **kwargs)
        
        self.add_widget(Label(text="Minecraft Mobile Launcher", font_size='24sp'))
        
        self.status_label = Label(text="آماده برای نصب", font_size='16sp')
        self.add_widget(self.status_label)
        
        self.progress_bar = ProgressBar(max=100, value=0)
        self.add_widget(self.progress_bar)
        
        self.install_btn = Button(text="نصب نسخه 1.8.9", size_hint=(1, 0.3), background_color=(0, 1, 0, 1))
        self.install_btn.bind(on_press=self.start_install_thread)
        self.add_widget(self.install_btn)

        # مسیر ذخیره سازی در اندروید (Internal Storage)
        self.download_path = "/sdcard/Download/MinecraftLauncher"
        if not os.path.exists(self.download_path):
            try:
                os.makedirs(self.download_path)
            except:
                self.download_path = os.getcwd() # اگر دسترسی نداشت، در پوشه برنامه ذخیره کن

    def start_install_thread(self, instance):
        # اجرای دانلود در یک Thread جداگانه تا صفحه گوشی هنگ نکند
        threading.Thread(target=self.download_and_install).start()

    def download_and_install(self):
        version_name = "DC_1.8.9"
        url = "https://cdn.imgurl.ir/uploads/j8535___.zip" # <--- لینک مستقیم فایل خود را اینجا بگذارید
        
        try:
            self.update_status("در حال شروع دانلود...")
            self.install_btn.disabled = True
            
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            file_path = os.path.join(self.download_path, f"{version_name}.zip")
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # محاسبه درصد پیشرفت
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            Clock.schedule_once(lambda dt: self.update_progress(percent))

            self.update_status("در حال استخراج فایل‌ها...")
            self.extract_file(file_path, version_name)
            
            self.update_status("نصب با موفقیت انجام شد!")
        except Exception as e:
            self.update_status(f"خطا: {str(e)}")
        finally:
            Clock.schedule_once(lambda dt: setattr(self.install_btn, 'disabled', False))

    def extract_file(self, zip_path, version_name):
        extract_to = os.path.join(self.download_path, version_name)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(zip_path)

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))

    def update_progress(self, value):
        self.progress_bar.value = value

class MinecraftApp(App):
    def build(self):
        return LauncherUI()

if __name__ == '__main__':
    MinecraftApp().run()
