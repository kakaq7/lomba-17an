import streamlit as st
import json
import os
from fpdf import FPDF

DATA_FILE = "data_lomba.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Daftar Juara Lomba 17 Agustusan", ln=True, align="C")
    pdf.ln(5)

    juara_ditemukan = False
    for nama_lomba, info in data.items():
        if info.get("pemenang"):
            juara_ditemukan = True
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Lomba: {nama_lomba}", ln=True)
            pdf.set_font("Arial", "", 11)
            for i, peserta in enumerate(info["pemenang"], 1):
                pdf.cell(0, 8, f"Juara {i}: {peserta}", ln=True)
            pdf.ln(4)

    if not juara_ditemukan:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "Belum ada lomba yang memiliki juara.", ln=True)

    pdf_output_path = "daftar_juara_lomba.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

# ------------------- Aplikasi -------------------

data = load_data()
st.title("🏁 Manajemen Lomba 17 Agustusan")
st.subheader("Karang Taruna Bina Bhakti")

menu = st.sidebar.radio("Menu", [
    "Tambah Lomba", "Tambah Peserta",
    "Kualifikasi", "Final & Juara",
    "Lihat Semua", "Hapus Lomba", "Hapus Peserta"
])

# ------------------- Tambah Lomba -------------------
if menu == "Tambah Lomba":
    nama_lomba = st.text_input("Nama Lomba Baru")
    if st.button("Tambah Lomba"):
        if nama_lomba in data:
            st.warning("Lomba sudah ada!")
        else:
            data[nama_lomba] = {"peserta": [], "lolos_kualifikasi": [], "pemenang": []}
            save_data(data)
            st.success(f"Lomba '{nama_lomba}' ditambahkan.")

# ------------------- Tambah Peserta -------------------
elif menu == "Tambah Peserta":
    if not data:
        st.warning("Belum ada lomba.")
    else:
        nama_lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        peserta = st.text_input("Nama Peserta")
        if st.button("Tambah Peserta"):
            data[nama_lomba]["peserta"].append(peserta)
            save_data(data)
            st.success(f"Peserta '{peserta}' ditambahkan ke lomba '{nama_lomba}'.")

# ------------------- Kualifikasi -------------------
elif menu == "Kualifikasi":
    if not data:
        st.warning("Belum ada lomba.")
    else:
        nama_lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        peserta = data[nama_lomba]["peserta"]
        if not peserta:
            st.warning("Belum ada peserta.")
        else:
            dipilih = st.multiselect("Pilih yang Lolos Kualifikasi", peserta)
            if st.button("Simpan Kualifikasi"):
                data[nama_lomba]["lolos_kualifikasi"] = dipilih
                save_data(data)
                st.success("Peserta yang lolos kualifikasi berhasil disimpan.")

# ------------------- Final & Juara -------------------
elif menu == "Final & Juara":
    if not data:
        st.warning("Belum ada lomba.")
    else:
        nama_lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        finalis = data[nama_lomba].get("lolos_kualifikasi", [])
        if not finalis:
            st.warning("Belum ada yang lolos kualifikasi.")
        else:
            juara1 = st.selectbox("Juara 1", [""] + finalis)
            juara2 = st.selectbox("Juara 2", [""] + finalis)
            juara3 = st.selectbox("Juara 3", [""] + finalis)

            if st.button("Simpan Juara"):
                pemenang = []
                for j in [juara1, juara2, juara3]:
                    if j and j not in pemenang:
                        pemenang.append(j)
                data[nama_lomba]["pemenang"] = pemenang
                save_data(data)
                st.success("Pemenang final telah disimpan.")

# ------------------- Lihat Semua + PDF -------------------
elif menu == "Lihat Semua":
    st.markdown("## 🏆 Daftar Juara Lomba")
    juara_ditemukan = False
    for nama, info in data.items():
        if info["pemenang"]:
            juara_ditemukan = True
            st.markdown(f"### 🏁 {nama}")
            for i, p in enumerate(info["pemenang"], 1):
                st.write(f"Juara {i}: {p}")
    if not juara_ditemukan:
        st.info("Belum ada lomba yang memiliki juara.")

    if st.button("📥 Download PDF"):
        pdf_file_path = generate_pdf(data)
        with open(pdf_file_path, "rb") as f:
            st.download_button(
                label="Unduh Daftar Juara PDF",
                data=f,
                file_name="daftar_juara_lomba.pdf",
                mime="application/pdf"
            )

# ------------------- Hapus Lomba -------------------
elif menu == "Hapus Lomba":
    if not data:
        st.warning("Belum ada lomba.")
    else:
        nama_lomba = st.selectbox("Pilih Lomba yang Ingin Dihapus", list(data.keys()))
        if st.button("Hapus Lomba Ini"):
            del data[nama_lomba]
            save_data(data)
            st.success(f"Lomba '{nama_lomba}' telah dihapus.")

# ------------------- Hapus Peserta -------------------
elif menu == "Hapus Peserta":
    if not data:
        st.warning("Belum ada lomba.")
    else:
        nama_lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        peserta_list = data[nama_lomba]["peserta"]
        if not peserta_list:
            st.warning("Belum ada peserta di lomba ini.")
        else:
            peserta_hapus = st.selectbox("Pilih Peserta yang Ingin Dihapus", peserta_list)
            if st.button("Hapus Peserta Ini"):
                data[nama_lomba]["peserta"].remove(peserta_hapus)
                if peserta_hapus in data[nama_lomba]["lolos_kualifikasi"]:
                    data[nama_lomba]["lolos_kualifikasi"].remove(peserta_hapus)
                if peserta_hapus in data[nama_lomba]["pemenang"]:
                    data[nama_lomba]["pemenang"].remove(peserta_hapus)
                save_data(data)
                st.success(f"Peserta '{peserta_hapus}' dihapus dari lomba '{nama_lomba}'.")

