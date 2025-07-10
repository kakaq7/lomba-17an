import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import datetime
from pytz import timezone

# ====== File Storage ======
ACCOUNT_FILE = "akun_karangtaruna.json"
INVITE_FILE = "invite_codes.json"
DATA_FILE = "data_lomba.json"
ABSENSI_FILE = "absensi_anggota.json"
ACARA_FILE = "daftar_acara.json"

# ====== Helpers ======
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_accounts(): return load_json(ACCOUNT_FILE, {})
def save_accounts(data): save_json(ACCOUNT_FILE, data)
def load_invite_codes(): return load_json(INVITE_FILE, {"kode_aktif": []})
def save_invite_codes(data): save_json(INVITE_FILE, data)
def load_data(): return load_json(DATA_FILE, {})
def save_data(data): save_json(DATA_FILE, data)
def load_absensi(): return load_json(ABSENSI_FILE, {})
def save_absensi(data): save_json(ABSENSI_FILE, data)
def load_acara(): return load_json(ACARA_FILE, [])
def save_acara(data): save_json(ACARA_FILE, data)

def is_acara_berlangsung(waktu_str):
    try:
        waktu = datetime.strptime(waktu_str, "%d-%m-%Y %H:%M")
        waktu = timezone('Asia/Jakarta').localize(waktu)
        now = datetime.now(timezone('Asia/Jakarta'))
        return waktu.date() == now.date()
    except:
        return False

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Daftar Juara Lomba 17 Agustusan", ln=True, align="C")
    pdf.ln(5)
    ada = False
    for nama_lomba, info in data.items():
        if info.get("pemenang"):
            ada = True
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Lomba: {nama_lomba}", ln=True)
            pdf.set_font("Arial", "", 11)
            for i, peserta in enumerate(info["pemenang"], 1):
                pdf.cell(0, 8, f"Juara {i}: {peserta}", ln=True)
            pdf.ln(4)
    if not ada:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "Belum ada lomba yang memiliki juara.", ln=True)
    file_path = "daftar_juara_lomba.pdf"
    pdf.output(file_path)
    return file_path

# ====== Session Login ======
if "login_success" not in st.session_state:
    st.session_state.login_success = False
if "username" not in st.session_state:
    st.session_state.username = ""

accounts = load_accounts()

if not st.session_state.login_success:
    menu_login = st.selectbox("Pilih Aksi", ["Login", "Daftar Akun Baru"])
    if menu_login == "Login":
        st.title("🔐 Login Anggota Karang Taruna")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in accounts and accounts[username] == password:
                st.session_state.login_success = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Username atau password salah")
        st.stop()
    else:
        st.title("📝 Daftar Akun Baru")
        new_user = st.text_input("Buat Username")
        new_pass = st.text_input("Buat Password", type="password")
        invite_code = st.text_input("Kode Undangan")

        codes_data = load_invite_codes()
        kode_aktif = codes_data.get("kode_aktif", [])

        if st.button("Daftar"):
            if new_user in accounts:
                st.warning("Username sudah terdaftar.")
            elif not new_user or not new_pass or not invite_code:
                st.warning("Isi semua kolom.")
            elif invite_code not in kode_aktif:
                st.error("Kode undangan tidak valid.")
            else:
                accounts[new_user] = new_pass
                save_accounts(accounts)
                st.success("Akun berhasil dibuat. Silakan login.")
        st.stop()
else:
    st.sidebar.write(f"Hai, {st.session_state.username} 👋")
    if st.sidebar.button("🔓 Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.username == "admin":
        st.sidebar.markdown("### 🔐 Buat Kode Undangan Baru")
        codes_data = load_invite_codes()
        kode_aktif = codes_data.get("kode_aktif", [])
        new_code = st.sidebar.text_input("Masukkan Kode Baru")
        if st.sidebar.button("Tambah Kode"):
            if new_code in kode_aktif:
                st.sidebar.warning("Kode sudah aktif.")
            elif new_code.strip() == "":
                st.sidebar.warning("Kode tidak boleh kosong.")
            else:
                kode_aktif.append(new_code)
                codes_data["kode_aktif"] = kode_aktif
                save_invite_codes(codes_data)
                st.sidebar.success(f"Kode '{new_code}' berhasil ditambahkan.")

# ====== Menu Utama ======
st.title("🇮🇩 Aplikasi Karang Taruna Bina Bhakti")
main_menu = st.sidebar.selectbox("Pilih Menu Utama", ["Manajemen Lomba", "Manajemen Anggota"])

# ====== Manajemen Anggota ======
if main_menu == "Manajemen Anggota":
    absensi_data = load_absensi()
    acara_list = load_acara()

    if st.session_state.username == "admin":
        st.subheader("📅 Buat Acara Baru")
        nama_acara = st.text_input("Nama Acara")
        waktu_acara = st.text_input("Waktu Acara (format: DD-MM-YYYY HH:MM)")
        token_kode = st.text_input("Kode Unik Absensi")
        if st.button("➕ Simpan Acara"):
            try:
                datetime.strptime(waktu_acara, "%d-%m-%Y %H:%M")
                acara_list.append({"nama": nama_acara, "waktu": waktu_acara, "token": token_kode})
                save_acara(acara_list)
                st.success("Acara berhasil ditambahkan.")
            except:
                st.error("Format waktu salah. Gunakan DD-MM-YYYY HH:MM")

        st.subheader("✏️ Edit atau Hapus Acara")
        if acara_list:
            list_judul = [f"{a['nama']} - {a['waktu']}" for a in acara_list]
            idx = st.selectbox("Pilih Acara", range(len(acara_list)), format_func=lambda x: list_judul[x])
            selected_event = acara_list[idx]
            new_nama = st.text_input("Edit Nama Acara", value=selected_event["nama"], key="edit_nama")
            new_waktu = st.text_input("Edit Waktu Acara (DD-MM-YYYY HH:MM)", value=selected_event["waktu"], key="edit_waktu")
            new_token = st.text_input("Edit Kode Absensi", value=selected_event["token"], key="edit_token")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Simpan Perubahan"):
                    try:
                        datetime.strptime(new_waktu, "%d-%m-%Y %H:%M")
                        acara_list[idx] = {"nama": new_nama, "waktu": new_waktu, "token": new_token}
                        save_acara(acara_list)
                        st.success("Acara berhasil diperbarui.")
                    except:
                        st.error("Format waktu salah. Gunakan DD-MM-YYYY HH:MM")
            with col2:
                if st.button("🗑 Hapus Acara"):
                    acara_list.pop(idx)
                    save_acara(acara_list)
                    st.success("Acara berhasil dihapus.")
    else:
        st.subheader("✅ Absensi Kehadiran")
        aktif = [a for a in acara_list if is_acara_berlangsung(a['waktu'])]
        if not aktif:
            st.info("Tidak ada acara yang sedang berlangsung hari ini.")
        else:
            selected = st.selectbox("Pilih Acara", [f"{a['nama']} ({a['waktu']})" for a in aktif])
            st.text_input("Nama Anggota", value=st.session_state.username, disabled=True)
            kode = st.text_input("Masukkan Kode Absensi")
            acara_dipilih = next((a for a in aktif if f"{a['nama']} ({a['waktu']})" == selected), None)
            if st.button("✅ Absen Hadir"):
                if not kode or kode != acara_dipilih["token"]:
                    st.error("Kode absensi salah atau tidak valid.")
                else:
                    if selected not in absensi_data:
                        absensi_data[selected] = []
                    if st.session_state.username in absensi_data[selected]:
                        st.warning(f"'{st.session_state.username}' sudah absen di '{selected}'.")
                    else:
                        absensi_data[selected].append(st.session_state.username)
                        save_absensi(absensi_data)
                        st.success(f"'{st.session_state.username}' berhasil absen di '{selected}'.")

# ====== Manajemen Lomba ======
elif main_menu == "Manajemen Lomba":
    data = load_data()

    st.subheader("🏆 Tambah Lomba Baru")
    nama_lomba = st.text_input("Nama Lomba")
    if st.button("➕ Tambahkan Lomba"):
        if nama_lomba in data:
            st.warning("Lomba sudah ada.")
        elif nama_lomba.strip() == "":
            st.warning("Nama lomba tidak boleh kosong.")
        else:
            data[nama_lomba] = {"peserta": [], "pemenang": []}
            save_data(data)
            st.success(f"Lomba '{nama_lomba}' berhasil ditambahkan.")

    st.subheader("👤 Tambah Peserta")
    selected_lomba = st.selectbox("Pilih Lomba", list(data.keys()) if data else [])
    peserta = st.text_input("Nama Peserta")
    if st.button("➕ Tambah Peserta"):
        if selected_lomba and peserta:
            if peserta not in data[selected_lomba]["peserta"]:
                data[selected_lomba]["peserta"].append(peserta)
                save_data(data)
                st.success(f"Peserta '{peserta}' ditambahkan ke lomba '{selected_lomba}'.")
            else:
                st.warning("Peserta sudah terdaftar.")

    st.subheader("🏁 Tentukan Pemenang")
    if selected_lomba:
        peserta_lomba = data[selected_lomba]["peserta"]
        juara1 = st.selectbox("Juara 1", peserta_lomba, key="j1")
        juara2 = st.selectbox("Juara 2", peserta_lomba, key="j2")
        juara3 = st.selectbox("Juara 3", peserta_lomba, key="j3")
        if st.button("🏆 Simpan Juara"):
            if len({juara1, juara2, juara3}) < 3:
                st.error("Nama juara tidak boleh sama.")
            else:
                data[selected_lomba]["pemenang"] = [juara1, juara2, juara3]
                save_data(data)
                st.success("Pemenang berhasil disimpan.")

    st.subheader("📋 Lihat Semua Lomba & Juara")
    for lomba, info in data.items():
        if info.get("pemenang"):
            st.markdown(f"### 🏁 {lomba}")
            for i, juara in enumerate(info["pemenang"], 1):
                st.write(f"Juara {i}: {juara}")

    if st.button("📥 Download PDF Hasil Juara"):
        pdf_path = generate_pdf(data)
        with open(pdf_path, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name="daftar_juara_lomba.pdf")

    st.subheader("❌ Hapus Data")
    lomba_hapus = st.selectbox("Pilih Lomba yang Akan Dihapus", list(data.keys()) if data else [], key="hapus_lomba")
    if st.button("🗑 Hapus Lomba"):
        if lomba_hapus in data:
            del data[lomba_hapus]
            save_data(data)
            st.success(f"Lomba '{lomba_hapus}' berhasil dihapus.")

    peserta_hapus = st.text_input("Nama Peserta yang Akan Dihapus")
    if st.button("🗑 Hapus Peserta"):
        if selected_lomba and peserta_hapus in data[selected_lomba]["peserta"]:
            data[selected_lomba]["peserta"].remove(peserta_hapus)
            save_data(data)
            st.success(f"Peserta '{peserta_hapus}' dihapus dari '{selected_lomba}'.")
        else:
            st.warning("Peserta tidak ditemukan di lomba tersebut.")
