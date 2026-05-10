# ============================================================
#  K-MEANS CLUSTERING — Kompresi Gambar (Lossy)
#  Ide: kurangi jumlah warna unik dalam gambar menggunakan
#       K-Means clustering pada nilai RGB piksel
#  Jenis: Lossy (kualitas berkurang, tapi ukuran jauh lebih kecil)
# ============================================================
#
#  Library yang dibutuhkan:
#    pip install numpy matplotlib Pillow scikit-learn
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
from PIL import Image
from sklearn.cluster import KMeans


# ============================================================
#  LANGKAH 1 — Buat gambar contoh (jika tidak punya file sendiri)
# ============================================================

def create_sample_image(filename="sample_image.png", size=128):
    """
    Buat gambar sintetis berwarna-warni sebagai contoh.
    Kamu bisa ganti dengan gambar asli (foto, dll).
    """
    img = np.zeros((size, size, 3), dtype=np.uint8)

    # Gradasi biru-ungu di background
    for i in range(size):
        for j in range(size):
            img[i, j] = [
                int(50 + 150 * (j / size)),        # R
                int(20 + 80 * (i / size)),          # G
                int(180 - 100 * (j / size)),        # B
            ]

    # Lingkaran merah di tengah
    cy, cx = size // 2, size // 2
    for i in range(size):
        for j in range(size):
            if (i - cy)**2 + (j - cx)**2 < (size // 5)**2:
                img[i, j] = [220, 50, 50]

    # Kotak kuning di sudut kiri atas
    s = size // 6
    img[s:s*2, s:s*2] = [240, 200, 40]

    # Kotak hijau di sudut kanan bawah
    img[size-s*2:size-s, size-s*2:size-s] = [40, 180, 80]

    pil_img = Image.fromarray(img)
    pil_img.save(filename)
    print(f"[INFO] Gambar contoh dibuat: '{filename}' ({size}x{size} piksel)")
    return filename


# ============================================================
#  LANGKAH 2 — Load gambar & ubah ke array piksel
# ============================================================

def load_image(filepath):
    """
    Buka gambar dan ubah jadi array numpy ternormalisasi [0.0, 1.0].
    Hasilnya: array shape (tinggi, lebar, 3) — 3 = R, G, B
    """
    img = Image.open(filepath).convert("RGB")
    img_array = np.array(img, dtype=np.float32) / 255.0
    print(f"[INFO] Gambar dimuat: {img_array.shape[1]}x{img_array.shape[0]} piksel")
    return img_array


# ============================================================
#  LANGKAH 3 — Kompresi dengan K-Means
# ============================================================

def compress_with_kmeans(img_array, k):
    """
    K-Means Clustering untuk kompresi gambar:

    1. Ratakan gambar: (H, W, 3) → (H*W, 3)  ← setiap piksel = 1 baris
    2. Jalankan K-Means: cari 'k' centroid warna yang mewakili semua piksel
    3. Ganti setiap piksel dengan warna centroid cluster-nya
    4. Kembalikan ke bentuk gambar asli (H, W, 3)

    Semakin kecil k → warna lebih sedikit → kompresi lebih besar
    Semakin besar k → warna lebih banyak → kualitas mendekati asli
    """
    h, w, c = img_array.shape

    # Ratakan jadi 2D: (jumlah_piksel, 3)
    pixels = img_array.reshape(-1, 3)

    # Jalankan K-Means (n_init='auto' untuk scikit-learn terbaru)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
    kmeans.fit(pixels)

    # Setiap piksel diganti dengan centroid cluster-nya
    compressed_pixels = kmeans.cluster_centers_[kmeans.labels_]

    # Kembalikan ke bentuk gambar
    compressed_img = compressed_pixels.reshape(h, w, c)
    compressed_img = np.clip(compressed_img, 0, 1)

    return compressed_img, kmeans.cluster_centers_


# ============================================================
#  LANGKAH 4 — Hitung dan tampilkan perbandingan
# ============================================================

def estimate_compression_ratio(img_array, k):
    """
    Estimasi rasio kompresi teoritis:
    - Gambar asli: setiap piksel = 24 bit (8 bit per channel RGB)
    - Gambar terkompresi: setiap piksel = log2(k) bit (hanya index cluster)
      + color palette = k * 24 bit

    Makin kecil k, makin besar kompresi.
    """
    h, w = img_array.shape[:2]
    total_pixels = h * w

    # Ukuran asli (dalam bit)
    original_bits = total_pixels * 24

    # Ukuran setelah kompresi (index + palette)
    bits_per_pixel = max(1, int(np.ceil(np.log2(k))))  # bit untuk index cluster
    palette_bits   = k * 24                              # bit untuk menyimpan k warna
    compressed_bits = total_pixels * bits_per_pixel + palette_bits

    ratio = original_bits / compressed_bits
    saving = (1 - compressed_bits / original_bits) * 100

    return original_bits, compressed_bits, ratio, saving


def run_compression_demo(filepath):
    """
    Demo utama: kompres gambar dengan berbagai nilai K dan tampilkan hasilnya.
    """
    img_array = load_image(filepath)

    # Nilai K yang akan diuji (jumlah warna dalam gambar hasil kompresi)
    k_values = [2, 4, 8, 16, 32]

    # --- Buat visualisasi perbandingan ---
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor('#1a1a2e')

    gs = gridspec.GridSpec(2, len(k_values) + 1,
                           hspace=0.35, wspace=0.15,
                           top=0.88, bottom=0.12)

    # Gambar asli di kiri atas & bawah
    ax_orig_top = fig.add_subplot(gs[0, 0])
    ax_orig_top.imshow(img_array)
    ax_orig_top.set_title("Gambar Asli", color='white', fontsize=10, pad=6)
    ax_orig_top.axis('off')

    ax_orig_bot = fig.add_subplot(gs[1, 0])
    h, w = img_array.shape[:2]
    orig_bits, _, _, _ = estimate_compression_ratio(img_array, 256)
    info_text = (
        f"Resolusi\n{w} × {h}\n\n"
        f"Warna unik\n16.7 juta\n\n"
        f"Ukuran (est.)\n{orig_bits // 8 // 1024:.0f} KB"
    )
    ax_orig_bot.text(0.5, 0.5, info_text,
                     ha='center', va='center',
                     color='#aaaacc', fontsize=9,
                     fontfamily='monospace',
                     transform=ax_orig_bot.transAxes)
    ax_orig_bot.set_facecolor('#12122a')
    ax_orig_bot.axis('off')

    print(f"\n{'═'*60}")
    print(f"  HASIL KOMPRESI K-MEANS")
    print(f"  Gambar: {filepath} | Resolusi: {w}x{h}")
    print(f"{'═'*60}")
    print(f"{'K':>5} | {'Warna':>6} | {'Ukuran Asli':>12} | {'Sesudah':>10} | {'Hemat':>7} | {'Rasio':>7}")
    print(f"{'─'*5}-+-{'─'*6}-+-{'─'*12}-+-{'─'*10}-+-{'─'*7}-+-{'─'*7}")

    for col_idx, k in enumerate(k_values):
        compressed, palette = compress_with_kmeans(img_array, k)
        orig_bits, comp_bits, ratio, saving = estimate_compression_ratio(img_array, k)

        print(f"{k:>5} | {k:>6} | {orig_bits//8//1024:>10} KB | {comp_bits//8//1024:>8} KB | {saving:>6.1f}% | {ratio:>5.1f}:1")

        # Gambar hasil kompresi (atas)
        ax_img = fig.add_subplot(gs[0, col_idx + 1])
        ax_img.imshow(compressed)
        ax_img.set_title(f"K = {k}", color='white', fontsize=10, pad=6)
        ax_img.axis('off')

        # Info kompresi (bawah)
        ax_info = fig.add_subplot(gs[1, col_idx + 1])
        info = (
            f"Warna\n{k}\n\n"
            f"Ukuran\n{comp_bits//8//1024:.0f} KB\n\n"
            f"Hemat\n{saving:.0f}%"
        )
        ax_info.text(0.5, 0.5, info,
                     ha='center', va='center',
                     color='#88ffcc', fontsize=9,
                     fontfamily='monospace',
                     transform=ax_info.transAxes)
        ax_info.set_facecolor('#122a1a')
        ax_info.axis('off')

        # Simpan tiap hasil kompresi sebagai file
        out_name = f"compressed_k{k}.png"
        out_img = Image.fromarray((compressed * 255).astype(np.uint8))
        out_img.save(out_name)
        print(f"        └─ Tersimpan: {out_name}")

    print(f"{'═'*60}")

    # Judul utama
    fig.suptitle("Kompresi Gambar dengan K-Means Clustering\n"
                 "Semakin kecil K → semakin sedikit warna → file lebih kecil",
                 color='white', fontsize=13, y=0.97)

    plt.savefig("kmeans_comparison.png", dpi=120,
                bbox_inches='tight', facecolor='#1a1a2e')
    print("\n[INFO] Grafik perbandingan disimpan: 'kmeans_comparison.png'")
    plt.show()


# ============================================================
#  MAIN
# ============================================================

if __name__ == "__main__":

    image_file = "sample_image.png"

    # Buat gambar contoh jika belum ada
    # → Untuk pakai gambar sendiri, ganti baris di bawah dengan:
    #   image_file = "nama_gambar_kamu.jpg"
    if not os.path.exists(image_file):
        create_sample_image(image_file, size=128)

    run_compression_demo(image_file)
