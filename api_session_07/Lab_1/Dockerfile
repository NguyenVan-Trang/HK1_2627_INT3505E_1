
FROM python:3.12-slim

WORKDIR /app

# Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép source code
COPY . .

# Flask chạy trên cổng 5000
EXPOSE 5000

# Chạy migration, tạo dữ liệu mẫu và khởi động API
CMD ["sh", "-c", "flask --app wsgi db upgrade && python seed.py && flask --app wsgi run --host=0.0.0.0 --port=5000"]
