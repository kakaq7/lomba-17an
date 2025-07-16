import streamlit as st
import json
import os
from datetime import datetime
from pytz import timezone
from fpdf import FPDF

# Zona Waktu Indonesia
wib = timezone("Asia/Jakarta")

# File Data
DATA_FILE = "data_lomba.json"
USER_FILE = "users.json"
ACARA_FILE = "acara.json"
ABSEN_FILE = "absensi.json"
INVITE_FILE = "invite_codes.json"

# Load/Save JSON
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Session Init
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.login_error = ""
    st.session_state.username = ""
if "login_error" not in st.session_state:
    st.session_state.login_error = False
if "lupa_password" not in st.session_state:
    st.session_state.lupa_password = False

# Admin Akun Default
users = load_json(USER_FILE, {})
if "admin" not in users:
    users["admin"] = "merdeka45"
    save_json(USER_FILE, users)

def proses_login():
    user = st.session_state["login_user"]
    pw = st.session_state["login_pass"]
    if user in users and users[user] == pw:
        st.session_state.login = True
        st.session_state.username = user
        return
    if not user or not pw:
        st.session_state.login_error = "Username dan password tidak boleh kosong."
        return
    else:
        st.session_state.login_error = "Username atau password salah."

# Login/Register
st.title("🇮🇩Aplikasi Karang Taruna Bina Bhakti")
if not st.session_state.login:
    mode = st.selectbox("Pilih", ["Login", "Daftar Akun"])
    if mode == "Login":
        if not st.session_state.lupa_password:
            st.header("Login Anggota Karang Taruna")
            st.text_input("Username", key="login_user")
            st.text_input("Password", type="password", key="login_pass")
            st.button("Login", on_click=proses_login)
        
            if st.session_state.login_error:
                st.error(st.session_state.login_error)
                
            if st.button("Lupa Password?"):
                st.session_state.lupa_password = True
                st.rerun()
        else:
            st.header("Reset Password")
            username = st.text_input("Username")
            new_pw = st.text_input("Password Baru", type="password")

            if st.button("Reset Password"):
                if username in users:
                    users[username] = new_pw
                    save_json(USER_FILE, users)
                    st.success("Password berhasil direset. Silakan login kembali.")
                    st.session_state.lupa_password = False
                else:
                    st.error("Username tidak ditemukan.")

            if st.button("Kembali ke Login"):
                st.session_state.lupa_password = False
                st.rerun()
        
    elif mode == "Daftar Akun":
        st.header("Daftar Akun Baru")
        user = st.text_input("Username Baru (Nama Lengkap)")
        pw = st.text_input("Password Baru", type="password")
        kode = st.text_input("Kode Undangan")
        invite = load_json(INVITE_FILE, {"aktif": ""})
        if st.button("Daftar"):
            if not user or not pw or not kode:
                st.error("Semua kolom harus diisi.")
            elif user in users:
                st.error("Username sudah ada.")
            elif kode != invite["aktif"]:
                st.error("Kode undangan tidak valid.")
            else:
                users[user] = pw
                save_json(USER_FILE, users)
                st.success("Akun berhasil dibuat. Silakan login.")
    st.stop()

def proses_logout():
    st.session_state.login = False
    st.session_state.username = ""
    st.session_state.login_error = False

# Sidebar: Logout + Admin Panel
st.sidebar.title(f"Hai, {st.session_state.username}")
st.sidebar.button("Logout", on_click=proses_logout)

# Admin: Update Kode Undangan
if st.session_state.username == "admin":
    st.sidebar.title("Admin Panel")
    kode_baru = st.sidebar.text_input("Kode Undangan Baru")
    if st.sidebar.button("Perbarui Kode"):
        invites = {"aktif": kode_baru}
        save_json(INVITE_FILE, invites)
        st.sidebar.success("Kode diperbarui")

# Menu
menu = st.sidebar.selectbox("Menu", ["Manajemen Anggota", "Manajemen Lomba"])
# Manajemen Lomba
data = load_json(DATA_FILE, {})
if menu == "Manajemen Lomba":
    st.header("Tambah Lomba")
    nama = st.text_input("Nama Lomba")
    if st.button("Tambah Lomba"):
        if nama in data:
            st.warning("Lomba sudah ada.")
        else:
            data[nama] = {"peserta": [], "pemenang": []}
            save_json(DATA_FILE, data)
            st.success("Lomba ditambahkan.")

    if data:
        st.header("Tambah Peserta & Juara")
        lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        peserta = st.text_input("Nama Peserta")
        if st.button("Tambah Peserta"):
            if peserta and peserta not in data[lomba]["peserta"]:
                data[lomba]["peserta"].append(peserta)
                save_json(DATA_FILE, data)
                st.success("Peserta ditambahkan.")

        st.subheader("Tentukan Juara")
        if data[lomba]["peserta"]:
            j1 = st.selectbox("Juara 1", data[lomba]["peserta"], key="j1")
            j2 = st.selectbox("Juara 2", data[lomba]["peserta"], key="j2")
            j3 = st.selectbox("Juara 3", data[lomba]["peserta"], key="j3")
            if st.button("Simpan Juara"):
                if len({j1, j2, j3}) < 3:
                    st.error("Juara tidak boleh sama.")
                else:
                    data[lomba]["pemenang"] = [j1, j2, j3]
                    save_json(DATA_FILE, data)
                    st.success("Juara disimpan.")

        st.header("Lihat Juara")
        for l, isi in data.items():
            if isi["pemenang"]:
                st.subheader(l)
                for i, p in enumerate(isi["pemenang"], 1):
                    st.write(f"Juara {i}: {p}")

        if st.button("Download PDF Juara"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, "Daftar Juara Lomba", ln=1, align="C")
            for l, isi in data.items():
                if isi["pemenang"]:
                    pdf.cell(200, 10, f"Lomba: {l}", ln=1)
                    for i, p in enumerate(isi["pemenang"], 1):
                        pdf.cell(200, 10, f"Juara {i}: {p}", ln=1)
            pdf.output("juara.pdf")
            with open("juara.pdf", "rb") as f:
                st.download_button("📥 Unduh PDF", f, file_name="juara.pdf")

# Manajemen Anggota & Absensi
elif menu == "Manajemen Anggota":
    acara = load_json(ACARA_FILE, [])
    absen = load_json(ABSEN_FILE, {})

    if st.session_state.username == "admin":
        mode = st.selectbox("Pilih", ["Buat Acara", "Daftar Acara", "Kehadiran"])

        if mode == "Buat Acara":
            st.header("Buat Acara")
            judul = st.text_input("Judul Acara")
            waktu_str = st.text_input("Tanggal & Jam (dd-mm-yyyy hh:mm)")
            kode = st.text_input("Kode Absensi")

            if st.button("Simpan Acara"):
                try:
                    waktu = datetime.strptime(waktu_str, "%d-%m-%Y %H:%M")
                    acara.append({
                        "judul": judul,
                        "waktu": waktu.strftime("%d-%m-%Y %H:%M"),
                        "kode": kode
                    })
                    save_json(ACARA_FILE, acara)
                    st.success("Acara dibuat.")
                except:
                    st.error("Format waktu salah.")

        elif mode == "Daftar Acara":
            st.header("Filter Absensi Berdasarkan Tanggal")
            tgl_awal = st.date_input("Dari Tanggal")
            tgl_akhir = st.date_input("Sampai Tanggal")

            for i, ac in enumerate(acara):
                waktu_acara = datetime.strptime(ac["waktu"], "%d-%m-%Y %H:%M")
                if tgl_awal <= waktu_acara.date() <= tgl_akhir:
                    key = f"{ac['judul']} - {ac['waktu']}"
                    daftar = absen.get(key, [])

                    st.subheader(key)
                    st.write(f"Jumlah hadir: {len(daftar)}")
                    for nama in daftar:
                        st.write(f"✅ {nama}")

                    # Tombol Edit & Hapus
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("Edit", key=f"edit_{i}"):
                            st.session_state.editing_index = i
                    with col2:
                        # Di dalam loop acara:
                        if st.button("Hapus", key=f"hapus_{i}"):
                            st.session_state.hapus_index = i
                            st.rerun()

                        # Cek dan proses hapus di luar tombol
                        hapus_index = st.session_state.get("hapus_index", None)
                        if hapus_index is not None:
                            acara.pop(hapus_index)
                            save_json(ACARA_FILE, acara)
                            st.session_state.hapus_index = None
                            st.rerun()

                    # Form edit jika sedang diedit
                    if st.session_state.get("editing_index") == i:
                        st.markdown("**✏️ Edit Acara:**")

                        new_judul = st.text_input("Judul Baru", value=ac["judul"], key=f"judul_{i}")
                        new_waktu = st.text_input("Waktu Baru (dd-mm-yyyy hh:mm)", value=ac["waktu"], key=f"waktu_{i}")
                        new_kode = st.text_input("Kode Baru", value=ac["kode"], key=f"kode_{i}")

                        # Tampilkan error jika sebelumnya gagal
                        if st.session_state.get("edit_error") == i:
                            st.error("❌ Format waktu salah. Gunakan format: dd-mm-yyyy hh:mm.")

                        # Fungsi simpan — jangan panggil st.rerun() di sini
                        def simpan_perubahan():
                            try:
                                # Ambil data dari session_state
                                new_judul = st.session_state[f"judul_{i}"]
                                new_waktu = st.session_state[f"waktu_{i}"]
                                new_kode = st.session_state[f"kode_{i}"]

                                # Validasi waktu
                                datetime.strptime(new_waktu, "%d-%m-%Y %H:%M")

                                # Simpan perubahan
                                acara[i]["judul"] = new_judul
                                acara[i]["waktu"] = new_waktu
                                acara[i]["kode"] = new_kode
                                save_json(ACARA_FILE, acara)

                                st.session_state["edit_success"] = True
                                st.session_state["edit_success_index"] = i
                            except:
                                st.session_state["edit_error"] = i

                        # Tombol simpan — tanpa rerun di dalam fungsi
                        st.button("💾 Simpan Perubahan", key=f"simpan_{i}", on_click=simpan_perubahan)
                    # Jalankan rerun di luar callback
                    if st.session_state.get("edit_success"):
                        # Bersihkan state lalu rerun
                        del st.session_state["edit_success"]
                        del st.session_state["editing_index"]
                        if "edit_error" in st.session_state:
                            del st.session_state["edit_error"]
                        st.rerun()


        elif mode == "Kehadiran":
            st.header("Persentase Kehadiran")
            semua_user = [u for u in users if u != "admin"]
            total_acara = len(acara)
            for user in semua_user:
                hadir = sum(
                    user in absen.get(f"{a['judul']} - {a['waktu']}", [])
                    for a in acara
                )
                persen = (hadir / total_acara) * 100 if total_acara else 0
                st.write(f"{user}: {hadir}/{total_acara} hadir ({persen:.1f}%)")

    else:
        # Untuk user biasa (bukan admin): absen hari ini
        st.header("Absen Kehadiran Hari Ini")
        hari_ini = datetime.now(wib).strftime("%d-%m-%Y")
        aktif = [a for a in acara if a["waktu"].startswith(hari_ini)]

        if not aktif:
            st.info("Tidak ada acara hari ini.")
        else:
            pilihan = st.selectbox("Pilih Acara", [f"{a['judul']} - {a['waktu']}" for a in aktif])
            dipilih = next((a for a in aktif if f"{a['judul']} - {a['waktu']}" == pilihan), None)

            st.text_input("Nama", value=st.session_state.username, disabled=True)
            kode_input = st.text_input("Masukkan Kode Absensi")

            if st.button("Absen"):
                if kode_input != dipilih["kode"]:
                    st.error("Kode salah.")
                else:
                    if pilihan not in absen:
                        absen[pilihan] = []
                    if st.session_state.username in absen[pilihan]:
                        st.warning("Sudah absen.")
                    else:
                        absen[pilihan].append(st.session_state.username)
                        save_json(ABSEN_FILE, absen)
                        st.success("Berhasil absen.")
