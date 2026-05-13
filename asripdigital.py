import streamlit as st
import time

# --- 1. LOGIKA STRUKTUR DATA ---
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
        if not self.root:
            self.root = BSTNode(id, name)
        else:
            self._insert_recursive(self.root, id, name)
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

# --- 2. SETUP TAMPILAN ---
st.set_page_config(page_title="Hybrid DB System", layout="wide")

# Custom CSS untuk mempercantik UI tanpa library luar
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    pre { background-color: #262730 !important; color: #00ff00 !important; padding: 20px !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Inisialisasi State
if 'bst' not in st.session_state:
    st.session_state.bst = SimpleBST()
if 'storage' not in st.session_state:
    st.session_state.storage = [] # Simulasi B+ Tree
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. HEADER & METRICS ---
st.title("🚀 Hybrid Database Archiving")
st.caption("Penerapan BST (Cache) & B+ Tree (Storage) untuk Skala Startup")

m1, m2, m3 = st.columns(3)
m1.metric("Status Cache", f"{st.session_state.bst.count} / 5", "BST")
m2.metric("Total di Storage", f"{len(st.session_state.storage)} Data", "B+ Tree")
m3.metric("Sistem", "Active", delta_color="normal")

st.divider()

# --- 4. AREA KERJA ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("📥 Input User")
    with st.container(border=True):
        u_id = st.number_input("User ID", min_value=1, step=1)
        u_name = st.text_input("Nama Lengkap")
        btn = st.button("Simpan Data", use_container_width=True)

        if btn and u_name:
            # 1. Simpan ke BST
            st.session_state.bst.insert(u_id, u_name)
            st.session_state.history.append(f"✅ [{u_id}] {u_name} masuk ke BST")
            
            # 2. Cek Ambang Batas (5 Data)
            if st.session_state.bst.count >= 5:
                with st.spinner("Memindahkan Cache ke Storage Utama..."):
                    time.sleep(1.5)
                    temp_list = []
                    st.session_state.bst.get_all_data_sorted(st.session_state.bst.root, temp_list)
                    
                    # Pindahkan ke Storage & Urutkan (Ciri B+ Tree)
                    st.session_state.storage.extend(temp_list)
                    st.session_state.storage = sorted(st.session_state.storage, key=lambda x: x['id'])
                    
                    # Reset BST
                    st.session_state.bst = SimpleBST()
                    st.session_state.history.append("🚀 MIGRASI: Data dipindahkan ke B+ Tree")
                st.toast("Data telah dimigrasi ke Storage!", icon="🔥")
                st.rerun()

with col_right:
    tab_search, tab_viz = st.tabs(["🔍 Search Engine", "🌲 Struktur Data"])
    
    with tab_search:
        s_query = st.number_input("Cari ID User", min_value=1, step=1, key="search")
        if st.button("Mulai Pencarian", use_container_width=True):
            # Cek di BST
            cache_list = []
            st.session_state.bst.get_all_data_sorted(st.session_state.bst.root, cache_list)
            in_cache = next((x for x in cache_list if x['id'] == s_query), None)
            
            if in_cache:
                st.success(f"Ditemukan di **CACHE (BST)**: {in_cache['name']}")
            else:
                st.info("Tidak ada di Cache. Mencari di Storage Utama...")
                # Cek di Storage
                in_storage = next((x for x in st.session_state.storage if x['id'] == s_query), None)
                if in_storage:
                    st.success(f"Ditemukan di **STORAGE (B+ Tree)**: {in_storage['name']}")
                else:
                    st.error("Data tidak ditemukan di seluruh sistem.")

    with tab_viz:
        st.write("**Visualisasi Pohon Cache (BST):**")
        if st.session_state.bst.root:
            tree_art = st.session_state.bst.visualize(st.session_state.bst.root)
            st.code(tree_art, language="text")
        else:
            st.info("Cache kosong.")

        st.write("**Struktur Storage (B+ Tree Leaf Nodes):**")
        if st.session_state.storage:
            # Menampilkan simulasi Linked List pada Leaf Nodes B+ Tree
            leaf_nodes = " ↔️ ".join([f"({d['id']}|{d['name']})" for d in st.session_state.storage])
            st.markdown(f"**Linked List:** `{leaf_nodes}`")
        else:
            st.info("Storage kosong.")

# --- 5. LOG SYSTEM ---
with st.expander("Lihat Log Sistem"):
    for log in reversed(st.session_state.history):
        st.write(log)
