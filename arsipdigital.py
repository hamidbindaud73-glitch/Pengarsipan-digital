import streamlit as st
import graphviz
import time

# --- 1. LOGIKA STRUKTUR DATA (Sederhana) ---
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

    def get_all_data(self, node, data_list):
        if node:
            self.get_all_data(node.left, data_list)
            data_list.append({"id": node.id, "name": node.name})
            self.get_all_data(node.right, data_list)

# --- 2. SETUP STREAMLIT ---
st.set_page_config(page_title="Hybrid Database System", layout="wide")

# Inisialisasi State agar data tidak hilang
if 'bst' not in st.session_state:
    st.session_state.bst = SimpleBST()
if 'storage' not in st.session_state:
    st.session_state.storage = [] # Simulasi B+ Tree (Urut)
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- 3. UI DESIGN ---
st.title("📂 Sistem Pengarsipan Digital Modern")
st.markdown("---")

# Layout Utama
col_input, col_status = st.columns([1, 2])

with col_input:
    st.subheader("📝 Input Data")
    with st.form("input_form", clear_on_submit=True):
        u_id = st.number_input("ID User", min_value=1, step=1)
        u_name = st.text_input("Nama User")
        submitted = st.form_submit_button("Tambah ke Sistem")
        
        if submitted and u_name:
            # Masuk ke BST
            st.session_state.bst.insert(u_id, u_name)
            st.toast(f"Data {u_name} berhasil disimpan di Cache (BST).", icon="📥")
            
            # Cek jika Cache Penuh (5 data)
            if st.session_state.bst.count >= 5:
                with st.status("Cache penuh! Memindahkan ke B+ Tree Utama...", expanded=True) as status:
                    time.sleep(1)
                    new_data = []
                    st.session_state.bst.get_all_data(st.session_state.bst.root, new_data)
                    # Pindahkan & Urutkan (Simulasi B+ Tree)
                    st.session_state.storage.extend(new_data)
                    st.session_state.storage = sorted(st.session_state.storage, key=lambda x: x['id'])
                    # Reset BST
                    st.session_state.bst = SimpleBST()
                    status.update(label="Migrasi Berhasil!", state="complete", expanded=False)
                st.balloons()

with col_status:
    st.subheader("📊 Status Sistem")
    c1, c2 = st.columns(2)
    c1.metric("Cache (BST)", f"{st.session_state.bst.count} / 5")
    c2.metric("Storage (B+ Tree)", len(st.session_state.storage))

st.markdown("---")

# --- 4. MENU SEARCH & RANGE ---
tab1, tab2, tab3 = st.tabs(["🔍 Cari User", "📉 Range Search", "🌳 Visualisasi Struktur"])

with tab1:
    search_id = st.number_input("Masukkan ID yang dicari:", min_value=1, key="search")
    if st.button("Cari Sekarang"):
        found = False
        # Cari di Cache
        cache_data = []
        st.session_state.bst.get_all_data(st.session_state.bst.root, cache_data)
        res_cache = next((item for item in cache_data if item["id"] == search_id), None)
        
        if res_cache:
            st.success(f"Ditemukan di **Cache (BST)**: {res_cache['name']}")
            found = True
        else:
            st.info("Mencari di Cache (BST)... Tidak ditemukan.")
            # Cari di Storage
            res_storage = next((item for item in st.session_state.storage if item["id"] == search_id), None)
            if res_storage:
                st.success(f"Ditemukan di **Storage Utama (B+ Tree)**: {res_storage['name']}")
                found = True
        
        if not found:
            st.error("Data tidak ditemukan di sistem mana pun.")

with tab2:
    col_a, col_b = st.columns(2)
    start = col_a.number_input("ID Awal", min_value=1)
    end = col_b.number_input("ID Akhir", min_value=1)
    
    if st.button("Tampilkan Range"):
        results = [d for d in st.session_state.storage if start <= d['id'] <= end]
        if results:
            st.table(results)
            st.write(f"Total ditemukan: {len(results)} data.")
        else:
            st.warning("Tidak ada data dalam rentang tersebut di Storage Utama.")

with tab3:
    st.subheader("Bentuk Pohon Saat Ini")
    
    # Visualisasi Sederhana menggunakan Graphviz
    dot = graphviz.Digraph()
    
    # Render BST jika ada
    if st.session_state.bst.root:
        def add_edges(node):
            if node.left:
                dot.edge(f"{node.id}\n({node.name})", f"{node.left.id}\n({node.left.name})")
                add_edges(node.left)
            if node.right:
                dot.edge(f"{node.id}\n({node.name})", f"{node.right.id}\n({node.right.name})")
                add_edges(node.right)
        add_edges(st.session_state.bst.root)
        st.graphviz_chart(dot)
    else:
        st.write("Cache kosong, silakan input data.")

    if st.session_state.storage:
        st.write("**B+ Tree Storage (Leaf Nodes Terhubung):**")
        nodes_str = " ↔️ ".join([f"[{d['id']}|{d['name']}]" for d in st.session_state.storage])
        st.code(nodes_str)
