(akan saya isi setelah setup file
            if st.button("✅ Absen Hadir"):
                if not kode or kode != acara_dipilih["token"]:
                    st.error("Kode absensi salah atau tidak valid.")
                else:
                    if selected not in absensi_data:
                        absensi_data[selected] = []
                    if nama in absensi_data[selected]:
                        st.warning(f"'{nama}' sudah tercatat hadir di '{selected}'.")
                    else:
                        absensi_data[selected].append(nama)
                        save_absensi(absensi_data)
                        st.success(f"'{nama}' berhasil absen di '{selected}'.")
)