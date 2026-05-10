# ============================================================
#  ARITHMETIC CODING — Kompresi Lossless berbasis probabilitas
#  Paper: Witten, Neal & Cleary (1987)
#  Jenis: Lossless (data dapat dikembalikan 100% sama persis)
#
#  Ide utama:
#  → Seluruh string di-encode jadi SATU angka desimal antara 0.0–1.0
#  → Setiap karakter mempersempit interval berdasarkan probabilitasnya
#  → Karakter sering muncul = interval lebih lebar = bit lebih sedikit
# ============================================================
#
#  Catatan: Menggunakan modul 'decimal' Python untuk presisi tinggi
#           supaya string lebih panjang pun bisa di-decode dengan benar
# ============================================================

from decimal import Decimal, getcontext
from collections import Counter
import time

# Set presisi tinggi untuk menghindari floating-point error
getcontext().prec = 50


# ============================================================
#  LANGKAH 1 — Hitung probabilitas tiap simbol
# ============================================================

def build_symbol_table(text):
    """
    Buat tabel: simbol → (low_cumulative, high_cumulative)
    Ini menentukan sub-interval tiap simbol di rentang [0, 1).

    Contoh untuk "AABBC" (5 karakter):
        A: prob=2/5=0.4  → interval [0.0, 0.4)
        B: prob=2/5=0.4  → interval [0.4, 0.8)
        C: prob=1/5=0.2  → interval [0.8, 1.0)
    """
    freq   = Counter(text)
    total  = len(text)
    table  = {}
    cumul  = Decimal('0')

    # Urutkan agar konsisten antara encode & decode
    for sym in sorted(freq.keys()):
        prob = Decimal(freq[sym]) / Decimal(total)
        table[sym] = (cumul, cumul + prob, prob)
        cumul += prob

    return table


def print_symbol_table(table):
    """Tampilkan tabel interval tiap simbol."""
    print("\n[1] Tabel Probabilitas & Interval Tiap Simbol:")
    print(f"    {'Simbol':^8} | {'Prob':^8} | {'Low':^10} | {'High':^10}")
    print(f"    {'─'*8}-+-{'─'*8}-+-{'─'*10}-+-{'─'*10}")
    for sym, (lo, hi, prob) in sorted(table.items()):
        bar = '▓' * int(float(prob) * 20)
        print(f"    '{sym}':     {float(prob):.4f}  |  {float(lo):.6f}  |  {float(hi):.6f}  {bar}")


# ============================================================
#  LANGKAH 2 — ENCODING
# ============================================================

def ac_encode(text, table):
    """
    Encoding: persempit interval [low, high) satu per satu untuk tiap karakter.

    Algoritma:
        low  = 0.0
        high = 1.0
        untuk setiap karakter c:
            range = high - low
            high  = low + range * table[c].high
            low   = low + range * table[c].low

    Codeword = titik tengah interval akhir → satu angka mewakili seluruh string
    """
    low  = Decimal('0')
    high = Decimal('1')

    print("\n[2] Proses Encoding (penyempitan interval):")
    print(f"    {'Karakter':^10} | {'Low':^20} | {'High':^20}")
    print(f"    {'─'*10}-+-{'─'*20}-+-{'─'*20}")

    for ch in text:
        sym_low, sym_high, _ = table[ch]
        diff = high - low
        high = low + diff * sym_high
        low  = low + diff * sym_low
        print(f"    '{ch}' → [{float(low):.10f},  {float(high):.10f})")

    codeword = (low + high) / 2
    print(f"\n    Interval akhir : [{float(low):.12f}, {float(high):.12f})")
    print(f"    Codeword (tengah): {float(codeword):.15f}")
    return low, high, codeword


# ============================================================
#  LANGKAH 3 — DECODING
# ============================================================

def ac_decode(codeword, table, length):
    """
    Decoding: dari satu angka (codeword), kembalikan string asli.

    Algoritma:
        untuk setiap posisi karakter:
            cari simbol s di mana table[s].low ≤ codeword < table[s].high
            output s
            perbarui codeword:
                codeword = (codeword - table[s].low) / table[s].prob

    Ulangi sebanyak panjang string asli (length).
    """
    tag    = Decimal(str(codeword))
    result = []

    print("\n[3] Proses Decoding (dari codeword ke string):")

    for step in range(length):
        for sym, (lo, hi, prob) in sorted(table.items()):
            if lo <= tag < hi:
                result.append(sym)
                # Normalisasi: geser codeword ke interval [0,1)
                tag = (tag - lo) / prob
                print(f"    Langkah {step+1}: tag={float(tag):.10f} → '{sym}'")
                break

    return ''.join(result)


# ============================================================
#  FUNGSI UTAMA — Demo lengkap untuk satu input
# ============================================================

def arithmetic_coding_demo(text, label=""):
    """Jalankan encode + decode dan tampilkan semua langkahnya."""
    separator = '═' * 55
    print(f"\n{separator}")
    print(f"  ARITHMETIC CODING — {label}")
    print(f"  Input  : \"{text}\"")
    print(f"  Panjang: {len(text)} karakter")
    print(separator)

    # --- Hitung tabel simbol ---
    table = build_symbol_table(text)
    print_symbol_table(table)

    # --- Estimasi bit ---
    # Uncompressed: len * 8 bit (ASCII)
    # Compressed  : -sum(p * log2(p)) * len  (Shannon entropy)
    import math
    entropy = -sum(
        float(prob) * math.log2(float(prob))
        for _, _, prob in table.values()
    )
    bits_before = len(text) * 8
    bits_after  = int(entropy * len(text)) + 1
    saving      = (1 - bits_after / bits_before) * 100

    print(f"\n    Entropi Shannon  : {entropy:.4f} bit/simbol")
    print(f"    Bit sebelum      : {bits_before} bit  ({bits_before//8} byte)")
    print(f"    Bit sesudah (est): {bits_after} bit  ({bits_after//8} byte)")
    print(f"    Penghematan      : {saving:.1f}%")

    # --- Encode ---
    t0 = time.time()
    low, high, codeword = ac_encode(text, table)

    # --- Decode ---
    decoded = ac_decode(codeword, table, len(text))
    elapsed = time.time() - t0

    # --- Verifikasi ---
    match = (text == decoded)
    print(f"\n[4] Verifikasi:")
    print(f"    Input   : {text}")
    print(f"    Decoded : {decoded}")
    print(f"    Cocok   : {'✓ YA' if match else '✗ TIDAK'}")
    print(f"    Waktu   : {elapsed*1000:.2f} ms")
    print(separator)

    return match


# ============================================================
#  MAIN — Jalankan dengan beberapa contoh data
# ============================================================

if __name__ == "__main__":

    contoh = [
        ("AABBBCCCC",   "string dengan frekuensi berbeda"),
        ("INFORMATIKA", "kata teknis"),
        ("BANDUNG",     "nama kota"),
        ("ABCDE",       "string semua karakter unik"),
        ("AAAAAAB",     "satu karakter dominan"),
    ]

    sukses = 0
    for text, label in contoh:
        ok = arithmetic_coding_demo(text, label)
        if ok:
            sukses += 1

    print(f"\n{'─'*55}")
    print(f"  RINGKASAN: {sukses}/{len(contoh)} test berhasil di-decode dengan benar")
    print(f"{'─'*55}")

    # --------------------------------------------------------
    #  EKSPERIMEN: bandingkan compression ratio
    # --------------------------------------------------------
    print("\n\nPERBANDINGAN COMPRESSION RATIO:")
    print(f"{'Input':<25} | {'Sebelum':>8} | {'Sesudah':>8} | {'Hemat':>7}")
    print(f"{'─'*25}-+-{'─'*8}-+-{'─'*8}-+-{'─'*7}")

    import math
    for text, _ in contoh:
        freq = Counter(text)
        total = len(text)
        entropy = -sum(
            (c/total) * math.log2(c/total)
            for c in freq.values()
        )
        before = total * 8
        after  = int(entropy * total) + 1
        saving = (1 - after/before) * 100
        print(f"{text:<25} | {before:>7}b  | {after:>7}b  | {saving:>6.1f}%")
