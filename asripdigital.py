import streamlit as st
import json
import os

# --- 1. LOGIKA STRUKTUR DATA (Versi Ringan untuk JSON) ---
class BSTLogic:
    @staticmethod
    def insert(tree, user_id, name):
        if not tree:
            return {"id": user_id, "name": name, "left": None, "right": None}
        if user_id < tree["id"]:
            tree["left"] = BSTLogic.insert(tree.get("left"), user_id, name)
        else:
            tree["right"] = BSTLogic.insert(tree.get("right"), user_id, name)
        return tree

    @staticmethod
    def get_all_sorted(tree, data_list):
        if tree:
            BSTLogic.get_all_sorted(tree.get("left"), data_list)
            data_list.append({"id": tree["id"], "name": tree["name"]})
            BSTLogic.get_all_sorted(tree.get("right"), data_list)

    @staticmethod
    def visualize(tree, level=0, prefix="Root: "):
        ret = ""
        if tree:
            ret += " " * (level * 4) + prefix + f"[{tree['id']}: {tree['name']}]\n"
            if tree.get("left") or tree.get("right"):
                ret += BSTLogic.visualize(tree.get("left"), level + 1, "L── ")
                ret += BSTLogic.visualize(tree.get("right"), level + 1, "R── ")
        return ret

# --- 2. FUNGSI SAVE & LOAD (Ganti Pickle ke JSON agar aman) ---
DB_FILE = "database_asrip.json"

def save_db():
    data = {
        "bst_root": st.session_state.bst_root,
        "bst_count": st.session_state.bst_count,
        "storage": st.session_state.storage,
        "logs": st.session_state.logs
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return None

# --- 3. INISIALISASI ---
st.set_page_config(page_title="Hybrid DB - Persistent", layout="wide")

if "initialized" not in st.session_state:
    saved = load_db()
    if saved:
        st.session_state.bst_root = saved["bst_root"]
        st.session_state.bst_count = saved["bst_count"]
        st.session_state.storage = saved["storage"]
        st.session_state.logs = saved["logs"]
    else:
        st.session_state.bst_root = None
        st.session_state.bst_count = 0
        st.session_state.storage = []
        st.session_state.logs = []
    st.session_state.initialized = True

# --- 4. UI TAMPILAN ---
st.title("📂 Sistem Pengarsipan Digital")
st.info("Data disimpan dalam format JSON. Aman dari PicklingError.")

# Sidebar untuk Reset
with st.sidebar:
    if st.button("Reset & Hapus Semua Data"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()

# Metrics
col_m1, col_m2 = st.columns(2)
col_m1.metric("Cache (BST)", f"{st.session_state.bst_count} / 5")
col_m2.metric("Storage Utama", f"{len(st.session_state.storage)} Data")

# Input
with st.container(border=True):
    c1, c2, c3 = st.columns([1, 2, 1])
    in_id = c1.number_input("User ID", min_value=1, step=1)
    in_name = c2.text_input("Nama User")
    if c3.button("Tambah", use_container_width=True):
        if in_name:
            st.session_state.bst_root = BSTLogic.insert(st.session_state.bst_root, in_id, in_name)
            st.session_state.bst_count += 1
            st.session_state.logs.append(f"📥 [{in_id}] {in_name} masuk Cache")
            
            if st.session_state.bst_count >= 5:
                # Migrasi ke Storage Utama
                migrated_data = []
                BSTLogic.get_all_sorted(st.session_state.bst_root, migrated_data)
                st.session_state.storage.extend(migrated_data)
                # Sort agar seperti B+ Tree (Urut)
                st.session_state.storage = sorted(st.session_state.storage, key=lambda x: x['id'])
                # Reset Cache
                st.session_state.bst_root = None
                st.session_state.bst_count = 0
                st.session_state.logs.append("🚀 Migrasi Cache ke Storage Berhasil!")
            
            save_db()
            st.rerun()

# Search
st.subheader("🔍 Multi-Pencarian ID")
search_raw = st.text_input("Masukkan ID (Koma sebagai pemisah, misal: 1, 5, 10)")

if search_raw:
    search_list = [int(x.strip()) for x in search_raw.split(",") if x.strip().isdigit()]
    res_data = []
    
    # Kumpulkan semua data
    cache_temp = []
    BSTLogic.get_all_sorted(st.session_state.bst_root, cache_temp)
    full_data = cache_temp + st.session_state.storage
    
    for sid in search_list:
        match = next((u for u in full_data if u['id'] == sid), None)
        if match:
            loc = "Cache" if any(u['id'] == sid for u in cache_temp) else "Storage"
            res_data.append({"ID": sid, "Nama": match['name'], "Lokasi": loc})
        else:
            res_data.append({"ID": sid, "Nama": "❌ Tidak Ada", "Lokasi": "-"})
    
    st.table(res_data)

# Visualisasi
t1, t2 = st.tabs(["🌳 Struktur Data", "📜 Log Riwayat"])
with t1:
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.write("**Visualisasi BST (Cache):**")
        if st.session_state.bst_root:
            st.code(BSTLogic.visualize(st.session_state.bst_root))
        else:
            st.write("Cache Kosong")
    with col_v2:
        st.write("**Visualisasi Storage Utama:**")
        if st.session_state.storage:
            nodes = " ↔️ ".join([f"({d['id']})" for d in st.session_state.storage])
            st.info(f"Leaf Nodes: {nodes}")
        else:
            st.write("Storage Kosong")

with t2:
    for log in reversed(st.session_state.logs):
        st.text(log)
