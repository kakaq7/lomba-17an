import streamlit as st
import json
import os

DATA_FILE = "data_lomba.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()
st.title("🏁 Manajemen Lomba 17 Agustusan")
st.subheader("Karang Taruna Bina Bhakti")

menu = st.sidebar.radio("Menu", ["Tambah Lomba", "Tambah Peserta", "Kualifikasi", "Final & Juara", "Lihat Semua"])

if menu == "Tambah Lomba":
    nama_lomba = st.text_input("Nama Lomba Baru")
    if st.button("Tambah Lomba"):
        if nama_lomba in data:
            st.warning("Lomba sudah ada!")
        else:
            data[nama_lomba] = {"peserta": [], "lolos_kualifikasi": [], "pemenang": []}
            save_data(data)
            st.success(f"Lomba '{nama_lomba}' ditambahkan.")

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

elif menu == "Kualifikasi":
    if not data:
        st.warning("Belum ada lomba.")
    else:
        nama_lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        peserta = data[nama_lomba]["peserta"]
        if not peserta:
            st.warning("Belum ada peserta.")
        else:
            st.markdown("### Peserta Kualifikasi")
            dipilih = st.multiselect("Pilih yang Lolos Kualifikasi", peserta)
            if st.button("Simpan Kualifikasi"):
                data[nama_lomba]["lolos_kualifikasi"] = dipilih
                save_data(data)
                st.success("Peserta yang lolos kualifikasi berhasil disimpan.")

elif menu == "Final & Juara":
    if not data:
        st.warning("Belum ada lomba.")
    else:
        nama_lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        finalis = data[nama_lomba].get("lolos_kualifikasi", [])
        if not finalis:
            st.warning("Belum ada yang lolos kualifikasi.")
        else:
            st.markdown("### Finalis")
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

elif menu == "Lihat Semua":
    if not data:
        st.info("Belum ada data lomba.")
    else:
        for nama, info in data.items():
            st.markdown(f"### 🏁 {nama}")
            st.markdown("**Peserta:**")
            for p in info["peserta"]:
                st.write(f"- {p}")
            if info["lolos_kualifikasi"]:
                st.markdown("**✅ Lolos Kualifikasi:**")
                for p in info["lolos_kualifikasi"]:
                    st.write(f"- {p}")
            if info["pemenang"]:
                st.markdown("**🏆 Pemenang:**")
                for i, p in enumerate(info["pemenang"], 1):
                    st.write(f"Juara {i}: {p}")
