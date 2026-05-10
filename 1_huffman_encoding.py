# ============================================================
#  HUFFMAN ENCODING — Kompresi Lossless berbasis frekuensi
#  Algoritma: David A. Huffman (1952)
#  Jenis: Lossless (data bisa dikembalikan 100% sama persis)
# ============================================================

# ---------- NODE untuk Huffman Tree ----------
class Node:
    def __init__(self, prob, symbol, left=None, right=None):
        self.prob   = prob    # frekuensi/probabilitas simbol
        self.symbol = symbol  # karakter / simbol
        self.left   = left    # anak kiri  → diberi kode '0'
        self.right  = right   # anak kanan → diberi kode '1'
        self.code   = ''      # kode biner yang akan ditetapkan


# ---------- HELPER FUNCTIONS ----------

codes = dict()  # dictionary: simbol → kode biner

def calculate_codes(node, val=''):
    """Rekursif: jalan dari root ke leaf, bangun kode biner tiap simbol."""
    new_val = val + str(node.code)
    if node.left:
        calculate_codes(node.left,  new_val)
    if node.right:
        calculate_codes(node.right, new_val)
    if not node.left and not node.right:   # leaf node = simbol asli
        codes[node.symbol] = new_val
    return codes


def calculate_probability(data):
    """Hitung frekuensi kemunculan tiap karakter dalam data."""
    symbols = dict()
    for ch in data:
        symbols[ch] = symbols.get(ch, 0) + 1
    return symbols


def output_encoded(data, coding):
    """Ubah string asli menjadi string bit hasil encoding."""
    return ''.join(coding[ch] for ch in data)


def total_gain(data, coding):
    """Cetak perbandingan ukuran bit sebelum vs sesudah kompresi."""
    before = len(data) * 8          # ASCII standar: 8 bit per karakter
    after  = sum(data.count(sym) * len(coding[sym]) for sym in coding)
    ratio  = (1 - after / before) * 100

    print(f"\n{'─'*45}")
    print(f"  Ukuran SEBELUM kompresi : {before:>6} bit")
    print(f"  Ukuran SESUDAH  kompresi: {after:>6} bit")
    print(f"  Penghematan              : {ratio:.1f}%")
    print(f"{'─'*45}")


# ---------- CORE: HUFFMAN ENCODING ----------

def huffman_encoding(data):
    """
    Langkah-langkah:
    1. Hitung frekuensi tiap karakter
    2. Urutkan dari terkecil ke terbesar
    3. Gabungkan dua node terkecil menjadi satu node baru (berulang)
    4. Tetapkan kode biner dari pohon yang terbentuk
    """
    global codes
    codes = dict()   # reset supaya tidak campur antar pemanggilan

    # --- Langkah 1: frekuensi ---
    sym_prob = calculate_probability(data)
    print("\n[1] Frekuensi tiap karakter:")
    for sym, freq in sorted(sym_prob.items(), key=lambda x: -x[1]):
        bar = '█' * freq
        print(f"    '{sym}' : {freq:>2}x  {bar}")

    # --- Langkah 2 & 3: bangun pohon Huffman ---
    nodes = [Node(freq, sym) for sym, freq in sym_prob.items()]

    while len(nodes) > 1:
        nodes.sort(key=lambda x: x.prob)   # urutkan ascending
        left  = nodes[1]   # frekuensi terkecil kedua → kode 0
        right = nodes[0]   # frekuensi terkecil        → kode 1
        left.code  = 0
        right.code = 1
        parent = Node(left.prob + right.prob,
                      left.symbol + right.symbol,
                      left, right)
        nodes.remove(left)
        nodes.remove(right)
        nodes.append(parent)

    # --- Langkah 4: tetapkan kode ---
    huffman_codes = calculate_codes(nodes[0])
    print("\n[2] Kode Huffman tiap karakter (karakter paling sering = kode terpendek):")
    for sym, code in sorted(huffman_codes.items(), key=lambda x: len(x[1])):
        print(f"    '{sym}' → {code}  ({len(code)} bit)")

    total_gain(data, huffman_codes)
    encoded = output_encoded(data, huffman_codes)
    return encoded, nodes[0]


# ---------- CORE: HUFFMAN DECODING ----------

def huffman_decoding(encoded_data, huffman_tree):
    """
    Baca bit satu per satu:
    - '0' → ke kiri
    - '1' → ke kanan
    Sampai mencapai leaf node → karakter ditemukan, kembali ke root
    """
    root    = huffman_tree
    current = root
    result  = []

    for bit in encoded_data:
        current = current.right if bit == '1' else current.left
        # leaf node: tidak punya anak
        if not current.left and not current.right:
            result.append(current.symbol)
            current = root   # balik ke root untuk karakter berikutnya

    return ''.join(result)


# ============================================================
#  DEMO — jalankan dengan berbagai contoh data
# ============================================================

if __name__ == "__main__":

    test_cases = [
        "AAAAAAABCCCCCCDDEEEEE",   # contoh dari materi
        "INFORMATIKA",             # kata teknis
        "BANDUNG",                 # nama kota
        "KOMPRESI DATA ADALAH TEKNIK PENTING",  # kalimat
    ]

    for data in test_cases:
        print(f"\n{'═'*50}")
        print(f"  INPUT : \"{data}\"")
        print(f"  Panjang : {len(data)} karakter")
        print(f"{'═'*50}")

        encoded, tree = huffman_encoding(data)

        print(f"\n[3] Hasil Encoding (string biner):")
        print(f"    {encoded}")
        print(f"    Panjang encoded: {len(encoded)} bit")

        decoded = huffman_decoding(encoded, tree)
        print(f"\n[4] Hasil Decoding:")
        print(f"    {decoded}")
        print(f"\n    ✓ Decoding BERHASIL: {data == decoded}")
