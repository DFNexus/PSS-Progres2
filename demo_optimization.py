import os
import django
from django.db import connection, reset_queries

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from lms.models import Course

def run_demo():
    print("=== PENGETESAN OPTIMASI QUERY (SIMPLE LMS) ===\n")
    
    # --- SKENARIO 1: UNOPTIMIZED (N+1) ---
    reset_queries()
    print("Skenario 1: Query Standar (Potensi N+1)")
    
    # Kita ambil Course tanpa JOIN
    courses = list(Course.objects.all()) 
    for c in courses:
        # Bagian ini memicu query tambahan ke tabel Category dan User per baris
        print(f"Course: {c.title} | Category: {c.category.name} | Instructor: {c.instructor.username}")
    
    unoptimized_count = len(connection.queries)
    print(f"Total Database Hits (Unoptimized): {unoptimized_count}\n")

    # --- SKENARIO 2: OPTIMIZED (SELECT RELATED) ---
    reset_queries()
    print("Skenario 2: Query Teroptimasi (Select Related)")
    
    # Kita ambil Course SEKALIGUS JOIN ke Category dan Instructor dalam 1 Query
    courses_opt = list(Course.objects.select_related('category', 'instructor').all())
    
    for c in courses_opt:
        # Data sudah ada di memori hasil JOIN, tidak ada query tambahan di sini
        print(f"Course: {c.title} | Category: {c.category.name} | Instructor: {c.instructor.username}")
    
    optimized_count = len(connection.queries)
    print(f"Total Database Hits (Optimized): {optimized_count}")
    
    # --- KESIMPULAN ---
    print("\n" + "="*30)
    if optimized_count < unoptimized_count:
        print(f"HASIL: BERHASIL MENGHEMAT {unoptimized_count - optimized_count} QUERY!")
        print("Status: OPTIMASI SUKSES (A)")
    else:
        print("HASIL: OPTIMASI GAGAL (Cek kembali select_related)")
    print("="*30)

if __name__ == "__main__":
    run_demo()
