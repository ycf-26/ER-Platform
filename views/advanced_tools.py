#views/advanced_tools.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from rdkit import Chem
from rdkit.Chem import Draw
from config import ADMET_INFO

import stmol
import py3Dmol
HAS_3D = True


def render_live_preview():
    st.markdown("### 🔍 实时结构预览")
    smiles = st.text_input("输入 SMILES 结构式（实时预览）：", value="Oc1ccc2cc(ccc2c1)c3cc(F)c(O)cc3F",
                           key="live_preview_input")

    if smiles:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            img = Draw.MolToImage(mol, size=(450, 350))
            st.image(img, caption="实时 2D 分子结构", use_container_width=False)
            st.success("✅ 解析成功，已实时渲染分子二维结构。")
        else:
            st.error("❌ 无效的 SMILES 结构式，请检查输入。")


def render_radar_comparison(history_data):
    # 用一个空列把内容推到中间，但不要限制整个页面宽度
    left_spacer, center_col, right_spacer = st.columns([1, 2.5, 1])

    with center_col:
        # 故意加几个换行符，让标题下移一点，跟其他页面视觉对齐
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>多分子 ADMET 属性对比</h2>", unsafe_allow_html=True)

        if not history_data:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: #F0F9FF; border-radius: 10px; color: #0369A1; margin-top: 20px;'>
                暂无历史评估记录。请先在单分子评估模块中测算至少两个分子。
            </div>
            """, unsafe_allow_html=True)
            return

        drug_names = [item['name'] for item in history_data]

        st.markdown(
            "<p style='text-align: center; color: #4A5568; font-size: 14px; margin-top: 20px;'>选择要对比的分子（建议 2-3 个）：</p>",
            unsafe_allow_html=True)
        selected_drugs = st.multiselect("", drug_names, default=drug_names[:min(2, len(drug_names))],
                                        label_visibility="collapsed")

        if len(selected_drugs) < 2:
            st.markdown("<div style='text-align: center; color: #B45309;'>请至少选择两个分子进行对比。</div>",
                        unsafe_allow_html=True)
            return

        categories = [ADMET_INFO[t]["name"] for t in ADMET_INFO.keys()]
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(r=[60] * 6, theta=categories + [categories[0]], mode='lines',
                                      line=dict(color='#CBD5E0', width=1, dash='dot'), name='及格线(60分)'))

        colors = ['#2B6CB0', '#F43F5E', '#48BB78', '#FB923C', '#9F7AEA']
        for idx, drug_name in enumerate(selected_drugs):
            drug_info = next((item for item in history_data if item['name'] == drug_name), None)
            if drug_info:
                values = drug_info['scores']
                hex_color = colors[idx % len(colors)].lstrip('#')
                r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                fillcolor = f'rgba({r}, {g}, {b}, 0.2)'

                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    fillcolor=fillcolor,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    name=drug_name
                ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500,
            margin=dict(l=40, r=40, t=40, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)
def render_3d_molecule(smiles):
    st.markdown("### 3D 分子构象可视化")

    if not HAS_3D:
        st.warning("⚠️ 缺少 stmol 或 py3Dmol 依赖，请在终端运行：`pip install stmol py3Dmol`")
        return

    if not smiles:
        st.info("请先输入分子进行测算，随后在此处查看 3D 构象。")
        return

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        st.error("无效 SMILES，无法生成 3D 构象。")
        return

    from rdkit.Chem import AllChem
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol)
    mb = Chem.MolToMolBlock(mol)

    view = py3Dmol.view(width=600, height=400)
    view.addModel(mb, 'mol')
    view.setStyle({'stick': {'colorscheme': 'cyanCarbon'}, 'sphere': {'scale': 0.3}})
    view.setBackgroundColor('#F8FAFC')
    view.zoomTo()
    stmol.showmol(view, height=400)
    st.caption("可按住鼠标左键旋转，滚轮缩放，查看分子的 3D 立体构象。")