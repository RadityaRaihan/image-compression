# Image Compression Algorithms — Challenge Submission

## Struktur File

```
image_compression/
├── 1_huffman_encoding.py     ← Algoritma 1: Huffman Encoding (Lossless)
├── 2_kmeans_compression.py   ← Algoritma 2: K-Means Clustering (Lossy)
├── 3_arithmetic_coding.py    ← Algoritma 3: Arithmetic Coding (Lossless)
└── README.md                 ← Panduan ini
```

---

## Cara Menjalankan

### Prasyarat — Install library yang dibutuhkan

```bash
pip install numpy matplotlib Pillow scikit-learn
```

---

### 1. Huffman Encoding

**Konsep:**  
Algoritma kompresi *lossless* yang memberikan kode biner pendek pada karakter
yang sering muncul, dan kode panjang pada karakter yang jarang muncul.
Menggunakan Binary Tree untuk membangun kode tersebut.

**Cara run:**
```bash
python 1_huffman_encoding.py
```

**Output yang diharapkan:**
- Frekuensi tiap karakter dalam input
- Tabel kode biner Huffman tiap karakter
- Perbandingan bit sebelum vs sesudah kompresi
- Hasil encoding (string bit) dan decoding (string asli)
- Verifikasi bahwa hasil decode = input asli ✓

**Ubah data input:**  
Edit bagian `test_cases` di bawah `if __name__ == "__main__":` untuk mengganti
dengan string pilihanmu sendiri.

---

### 2. K-Means Image Compression

**Konsep:**  
Algoritma kompresi gambar *lossy* yang mengelompokkan warna-warna piksel
menjadi `k` cluster menggunakan K-Means. Setiap piksel diganti dengan warna
rata-rata clusternya → gambar hanya memiliki `k` warna unik.

**Cara run:**
```bash
python 2_kmeans_compression.py
```

**Output yang diharapkan:**
- File `sample_image.png` dibuat otomatis (jika belum ada)
- Tabel perbandingan: K | Ukuran Asli | Sesudah | Hemat | Rasio
- File `compressed_k2.png`, `compressed_k4.png`, dst. (hasil tiap K)
- File `kmeans_comparison.png` (gambar perbandingan visual semua K)

**Ubah gambar input:**  
Edit baris berikut di bagian `if __name__ == "__main__":`:
```python
image_file = "nama_gambar_kamu.jpg"   # ← ganti ini
```
Hapus atau komentari baris `create_sample_image(...)` jika pakai gambar sendiri.

**Ubah nilai K:**  
Edit baris `k_values = [2, 4, 8, 16, 32]` untuk mencoba nilai lain.

---

### 3. Arithmetic Coding

**Konsep:**  
Algoritma kompresi *lossless* berbasis probabilitas. Seluruh string
di-*encode* menjadi **satu angka desimal** antara 0.0 dan 1.0.
Setiap karakter mempersempit interval tersebut sesuai probabilitasnya.
Karakter yang sering muncul mendapat interval lebih lebar → butuh lebih sedikit bit.

**Cara run:**
```bash
python 3_arithmetic_coding.py
```

**Output yang diharapkan:**
- Tabel probabilitas & interval tiap simbol
- Proses encoding: penyempitan interval langkah per langkah
- Codeword akhir (satu angka yang mewakili seluruh string)
- Proses decoding: dari codeword kembali ke string asli
- Verifikasi bahwa decoded = input asli ✓
- Tabel perbandingan compression ratio semua contoh

**Ubah data input:**  
Edit bagian `contoh = [...]` di bawah `if __name__ == "__main__":`.

---

## Ringkasan Perbandingan Algoritma

| Algoritma       | Jenis      | Digunakan untuk         | Kunci Cara Kerja                          |
|----------------|------------|------------------------|------------------------------------------|
| Huffman        | Lossless   | Teks, biner, file ZIP  | Pohon biner berdasarkan frekuensi        |
| K-Means        | Lossy      | Gambar (image)         | Clustering warna piksel                  |
| Arithmetic     | Lossless   | Teks, data digital     | Encode string jadi satu angka 0.0–1.0    |

### Kapan pakai yang mana?

- **Huffman** → kompresi teks sederhana, mudah diimplementasikan
- **K-Means** → kompresi gambar saat kualitas sedikit turun masih oke
- **Arithmetic** → kompresi lebih optimal dari Huffman (mendekati entropy Shannon)
