# Instagram Crop Tool

Tool untuk mengkrop foto sesuai standar Instagram:
- **Feed Instagram**: 4:5 (1080×1350 piksel)
- **Grid Feed**: 3:4 (354×472 piksel)
- **Reels**: 9:16

![Instagram Crop Tool Preview](https://i.ibb.co/Gnxk3GK/instagram-crop-tool.png)

## Instalasi

1. Pastikan Python sudah terinstal di komputer Anda (versi 3.6 atau lebih tinggi)
2. Install dependensi yang diperlukan:
   ```
   pip install -r requirements.txt
   ```

## Cara Penggunaan

1. Jalankan program:
   ```
   python instagram_crop.py
   ```
2. Pilih format Instagram yang diinginkan (Feed 4:5, Grid Feed 3:4, atau Reels 9:16)
3. Klik "Select Image" untuk memilih foto yang ingin dicrop
4. Lihat preview hasil crop secara langsung
5. Klik "Process Image(s)" untuk memproses satu atau beberapa foto
6. Pilih folder untuk menyimpan hasil foto yang sudah dicrop
7. Foto yang sudah dicrop akan disimpan dengan format nama: `namaasli_formatinstagram.ekstensi`

### Untuk Foto Panorama/Lebar:

1. Centang opsi "Split wide images (for carousel)"
2. Pilih jumlah panel (2-5) yang Anda inginkan
3. Preview akan menampilkan bagaimana foto Anda akan dibagi
4. Hasil akan disimpan sebagai beberapa gambar terpisah dengan nama: `namaasli_formatinstagram_panel1of3.ekstensi`

## Fitur

- Antarmuka pengguna modern dengan area preview
- Preview langsung untuk melihat hasil crop sebelum memproses
- **Fitur Split untuk Foto Panorama/Lebar**: Otomatis membagi foto yang sangat lebar menjadi beberapa panel yang sesuai untuk carousel Instagram
- Crop otomatis yang mempertahankan bagian tengah gambar
- Resize sesuai standar Instagram
- Mendukung format gambar JPG, JPEG, PNG, dan WEBP
- Dapat memproses beberapa gambar sekaligus
- Progress bar untuk memantau proses pengolahan gambar 