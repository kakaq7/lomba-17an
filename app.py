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

# Inisialisasi data
data = load_data()

st.title("🏁 Manajemen Lomba 17 Agustus")
st.subheader("Karang Taruna Bina Bhakti")

menu = st.sidebar.radio("Menu", ["Tambah Lomba", "Tambah Peserta", "Catat Pemenang", "Lihat Semua"])

if menu == "Tambah Lomba":
    nama_lomba = st.text_input("Nama Lomba Baru")
    if st.button("Tambah Lomba"):
        if nama_lomba in data:
            st.warning("Lomba sudah ada!")
        else:
            data[nama_lomba] = {"peserta": [], "pemenang": []}
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

elif menu == "Catat Pemenang":
    if not data:
        st.warning("Belum ada lomba.")
    else:
        nama_lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        peserta = data[nama_lomba]["peserta"]
        if not peserta:
            st.warning("Belum ada peserta.")
        else:
            juara1 = st.selectbox("Juara 1", [""] + peserta)
            juara2 = st.selectbox("Juara 2", [""] + peserta)
            juara3 = st.selectbox("Juara 3", [""] + peserta)

            if st.button("Simpan Pemenang"):
                pemenang = []
                for juara in [juara1, juara2, juara3]:
                    if juara and juara not in pemenang:
                        pemenang.append(juara)
                data[nama_lomba]["pemenang"] = pemenang
                save_data(data)
                st.success("Pemenang berhasil dicatat.")

elif menu == "Lihat Semua":
    if not data:
        st.info("Belum ada data lomba.")
    else:
        for nama, info in data.items():
            st.markdown(f"### 🏁 {nama}")
            st.markdown("**Peserta:**")
            for p in info["peserta"]:
                st.write(f"- {p}")
            if info["pemenang"]:
                st.markdown("**🏆 Pemenang:**")
                for i, p in enumerate(info["pemenang"], 1):
                    st.write(f"Juara {i}: {p}")