import streamlit as st
import time
import pickle
import os

# --- 1. LOGIKA STRUKTUR DATA (Sama seperti sebelumnya) ---
class BSTNode:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.left = None
        self.right = None

class SimpleBST:
    def __init__(self):
        self.root = None
        self.count = 0
    
    def insert(self, id, name):
        if not self.root: self.root = BSTNode(id, name)
        else: self._insert_recursive(self.root, id, name)
        self.count += 1
        
    def _insert_recursive(self, node, id, name):
        if id < node.id:
            if node.left: self._insert_recursive(node.left, id, name)
            else: node.left = BSTNode(id, name)
        else:
            if node.right: self._insert_recursive(node.right, id, name)
            else: node.right = BSTNode(id, name)

    def get_all_data_sorted(self, node, data_list):
        if node:
            self.get_all_data_sorted(node.left, data_list)
            data_list.append({"id": node.id, "name": node.name})
            self.get_all_data_sorted(node.right, data_list)

    def visualize(self, node, level=0, prefix="Root: "):
        ret = ""
        if node:
            ret += " " * (level * 4) + prefix + f"[{node.id}: {node.name}]\n"
            if node.left or node.right:
                ret += self.visualize(node.left, level + 1, "L── ")
                ret += self.visualize(node.right, level + 1, "R── ")
        return ret

# --- 2. FUNGSI SAVE & LOAD (Agar data tidak hilang) ---
DB_FILE = "asrip_database.pkl"

def save_data():
    data = {
        'bst': st.session_state.bst,
        'storage': st.session_state.storage,
        'history': st.session_state.history
    }
    with open(DB_FILE, 'wb') as f:
        pickle.dump(data, f)

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'rb') as f:
            return pickle.load(f)
    return None

# --- 3. SETUP TAMPILAN ---
st.set_page_config(page_title="Hybrid DB Persistent", layout="wide")

# Inisialisasi State dari File atau Default
if 'initialized' not in st.session_state:
    saved = load_data()
    if saved:
        st.session_state.bst = saved['bst']
        st.session_state.storage = saved['storage']
        st.session_state.history = saved['history']
    else:
        st.session_state.bst = SimpleBST()
        st.session_state.storage = []
        st.session_state.history = []
    st.session_state.initialized = True

st.title("📂 Digital Archiving (Persistent Mode)")
st.caption("Data otomatis tersimpan ke file asrip_database.pkl")

# --- 4. HEADER METRICS ---
m1, m2 = st.columns(2)
m1.metric("Cache (BST)", f"{st.session_state.bst.count} / 5")
m2.metric("Storage (B+ Tree)", f"{len(st.session_state.storage)} Data")

# --- 5. INPUT AREA ---
with st.expander("➕ Tambah User Baru", expanded=True):
    c1, c2, c3 = st.columns([1, 2, 1])
    u_id = c1.number_input("User ID", min_value=1, step=1)
    u_name = c2.text_input("Nama Lengkap")
    if c3.button("Simpan", use_container_width=True):
        if u_name:
            st.session_state.bst.insert(u_id, u_name)
            st.session_state.history.append(f"📥 [{u_id}] {u_name} masuk ke BST")
            
            if st.session_state.bst.count >= 5:
                temp_list = []
                st.session_state.bst.get_all_data_sorted(st.session_state.bst.root, temp_list)
                st.session_state.storage.extend(temp_list)
                st.session_state.storage = sorted(st.session_state.storage, key=lambda x: x['id'])
                st.session_state.bst = SimpleBST()
                st.session_state.history.append("🚀 MIGRASI: Cache dipindah ke Storage")
            
            save_data() # Simpan ke file setiap kali ada perubahan
            st.rerun()

# --- 6. PENCARIAN MASSAL ---
st.subheader("🔍 Multi-ID Search")
s_input = st.text_input("Masukkan ID (pisahkan dengan koma, contoh: 10, 20, 30)")

if s_input:
    # Parsing input string menjadi list integer
    try:
        search_ids = [int(x.strip()) for x in s_input.split(",") if x.strip()]
        results = []
        
        # Ambil semua data dari BST & Storage untuk dicocokkan
        cache_data = []
        st.session_state.bst.get_all_data_sorted(st.session_state.bst.root, cache_data)
        all_data = cache_data + st.session_state.storage
        
        for sid in search_ids:
            found = next((x for x in all_data if x['id'] == sid), None)
            if found:
                # Cek posisinya di mana
                is_in_cache = any(x['id'] == sid for x in cache_data)
                pos = "Cache (BST)" if is_in_cache else "Storage (B+ Tree)"
                results.append({"ID": sid, "Nama": found['name'], "Posisi": pos})
            else:
                results.append({"ID": sid, "Nama": "❌ Tidak Ditemukan", "Posisi": "-"})
        
        st.table(results)
    except ValueError:
        st.error("Format input salah! Gunakan angka dan koma saja.")

# --- 7. VISUALISASI ---
tab_tree, tab_log = st.tabs(["🌲 Visualisasi Struktur", "📜 Log Sistem"])
with tab_tree:
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Struktur BST (Cache):**")
        st.code(st.session_state.bst.visualize(st.session_state.bst.root))
    with col_b:
        st.write("**B+ Tree Leaf Nodes:**")
        leaf_nodes = " ↔️ ".join([f"({d['id']})" for d in st.session_state.storage])
        st.markdown(f"`{leaf_nodes}`" if leaf_nodes else "Storage Kosong")

with tab_log:
    if st.button("Hapus Semua Data (Reset Database)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()
    for log in reversed(st.session_state.history):
        st.write(log)
