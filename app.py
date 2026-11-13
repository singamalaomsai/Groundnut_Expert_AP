import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
from PIL import Image

from knowledge_base import (
    AP_VARIETIES,
    get_variety_lifecycle,
    DISEASES_PESTS_DB,
    analyze_leaf_image_gemini,
    AP_MANDI_PRICES,
    GOVT_MSP_GROUNDNUT,
    calculate_quality_adjusted_rate
)

# ------------------------------------------------------------------------------
# Page Configuration & Custom Telugu Styling
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="ఆంధ్రప్రదేశ్ వేరుశనగ సాగు నిపుణుడు (AP Groundnut AI)",
    page_icon="🥜",
    layout="wide"
)

st.markdown("""
<style>
    .main-banner {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        color: #FFFFFF !important;
        padding: 22px;
        border-radius: 14px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .main-banner h2, .main-banner p {
        color: #FFFFFF !important;
    }
    .stage-box {
        background-color: #F1F8E9 !important;
        color: #111111 !important;
        border-left: 6px solid #2E7D32;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .stage-box h3, .stage-box h4, .stage-box p, .stage-box li, .stage-box b {
        color: #111111 !important;
    }
    .organic-card {
        background-color: #E8F5E9 !important;
        color: #111111 !important;
        border: 1px solid #81C784;
        padding: 15px;
        border-radius: 10px;
    }
    .organic-card h3, .organic-card h4, .organic-card p, .organic-card li, .organic-card b {
        color: #111111 !important;
    }
    .chemical-card {
        background-color: #FFF8E1 !important;
        color: #111111 !important;
        border: 1px solid #FFD54F;
        padding: 15px;
        border-radius: 10px;
    }
    .chemical-card h3, .chemical-card h4, .chemical-card p, .chemical-card li, .chemical-card b {
        color: #111111 !important;
    }
    .alert-card {
        background-color: #E0F2F1 !important;
        color: #004D40 !important;
        border-left: 6px solid #00695C;
        padding: 14px;
        border-radius: 8px;
    }
    .alert-card h3, .alert-card h4, .alert-card p, .alert-card li, .alert-card b {
        color: #004D40 !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Global Sidebar: Master Variety & Season Selection
# ------------------------------------------------------------------------------
st.sidebar.markdown("## 🥜 **వేరుశనగ రైతు సేవా కేంద్రం**")
st.sidebar.markdown("మీ విత్తన రకం & సీజన్ ఎంచుకోండి:")

selected_variety = st.sidebar.selectbox(
    "🌾 వేరుశనగ రకం (Select AP Variety):",
    list(AP_VARIETIES.keys()),
    index=0
)

selected_season = st.sidebar.radio(
    "🌦️ సాగు సీజన్ (Season):",
    ["ఖరీఫ్ (Kharif - వర్షాధార/ఆరుతడి)", "రబీ / వేసవి (Rabi - నీటి ఆధార)"],
    index=0
)

selected_soil = st.sidebar.selectbox(
    "🪨 నేల రకం (Soil Type):",
    ["ఇసుక గరప నేలలు (Sandy Loam)", "ఎర్ర గరప నేలలు (Red Loam)", "నల్ల రేగడి నేలలు (Light Black Soil)"]
)

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "📌 **విభాగాన్ని ఎంచుకోండి (Menu):**",
    [
        "1. ఆంధ్రప్రదేశ్ వేరుశనగ రకాలు (AP Varieties)",
        "2. పంట జీవిత చక్రం (Full Crop Life Cycle)",
        "3. విత్తిన రోజుల ఆధారంగా పనులు (Smart DAS Advisor)",
        "4. తెగుళ్లు & పురుగుల ఫోటో పరీక్ష (AI Photo Diagnosis)",
        "5. ఈ రోజు మార్కెట్ ధర & ఆదాయం లెక్కింపు (Market Rate)"
    ]
)

v_data = AP_VARIETIES[selected_variety]
lifecycle_stages = get_variety_lifecycle(selected_variety, selected_season)
total_crop_days = v_data["duration_kharif"] if "ఖరీఫ్" in selected_season else v_data["duration_rabi"]

# Top Header Banner
st.markdown(f"""
<div class="main-banner">
    <h2 style="margin:0;">🥜 ఆంధ్రప్రదేశ్ వేరుశనగ సాగు మరియు AI యాజమాన్య నిపుణుడు</h2>
    <p style="margin:6px 0 0 0; font-size:16px;">
        <b>ఎంచుకున్న రకం:</b> {selected_variety} &nbsp;|&nbsp; 
        <b>పంట కాలం:</b> {total_crop_days} రోజులు ({selected_season.split()[0]}) &nbsp;|&nbsp; 
        <b>నేల రకం:</b> {selected_soil}
    </p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# MODULE 1: ఆంధ్రప్రదేశ్ వేరుశనగ రకాలు (AP Varieties & Comparison)
# ==============================================================================
if menu.startswith("1."):
    st.subheader(f"🌾 ఎంచుకున్న రకం పూర్తి వివరాలు: {selected_variety}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⏳ పంట కాలపరిమితి", v_data["duration_text"])
    c2.metric("📦 ఖరీఫ్ దిగుబడి", v_data["yield_kharif"])
    c3.metric("🌟 రబీ దిగుబడి", v_data["yield_rabi"])
    c4.metric("🛢️ నూనె & గింజ శాతం", f"{v_data['oil_content']} | {v_data['shelling_percent']}% పప్పు")

    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.markdown(f"""
        <div class="stage-box">
            <h4>📋 {selected_variety} ముఖ్య లక్షణాలు & సాగు వివరాలు</h4>
            <ul>
                <li><b>విత్తన మోతాదు (Seed Rate):</b> {v_data['seed_rate']}</li>
                <li><b>విత్తే దూరం (Spacing):</b> {v_data['spacing']}</li>
                <li><b>అనుకూలమైన నేలలు:</b> {v_data['soil']}</li>
                <li><b>అనుకూల సీజన్:</b> {v_data['season']}</li>
                <li><b>జిప్సం వేయాల్సిన సమయం:</b> విత్తిన {v_data['gypsum_window'][0]} నుండి {v_data['gypsum_window'][1]} రోజుల మధ్య</li>
                <li><b>ప్రత్యేక గుణాలు:</b> {v_data['special_features']}</li>
                <li><b>తెగుళ్ల నిరోధకత:</b> {v_data['disease_resistance']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.image(generate_stage_visual_banner(6), caption=f"{selected_variety} - కాయ మరియు మొక్క వృద్ధి నమూనా", use_container_width=True)

    # Deep Agronomy Card for TAG-24 and others
    if "deep_agronomy" in v_data:
        da = v_data["deep_agronomy"]
        st.markdown(f"""
        <div class="alert-card" style="margin-top:10px; margin-bottom:15px;">
            <h4>🔬 {selected_variety} — లోతైన శాస్త్రీయ మరియు సాగు విశ్లేషణ (Deep Agronomy Profile)</h4>
            <ul>
                <li><b>జన్యు మూలం (Pedigree & Institute):</b> {da['pedigree']}</li>
                <li><b>మొక్క ఆకృతి (Plant Architecture):</b> {da['plant_habit']} | <b>హార్వెస్ట్ ఇండెక్స్:</b> {da['harvest_index']}</li>
                <li><b>గింజ లక్షణాలు (Kernel Specs):</b> {da['kernel_info']}</li>
                <li><b>🌿 కలుపు మందు సమయం:</b> {da['weed_timing']}</li>
                <li><b>🚨 కోత జాగ్రత్త (Dormancy Alert):</b> {da['dormancy_alert']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🧮 మీ పొలం విస్తీర్ణానికి కావాల్సిన విత్తనం & ఎరువుల లెక్కింపు (Input Calculator)")
    acres_input = st.number_input("మీరు సాగు చేసే ఎకరాల సంఖ్యను నమోదు చేయండి (Enter Acres):", min_value=0.5, max_value=50.0, value=1.0, step=0.5)
    
    seed_per_acre = 72 if v_data["code"] in ["TAG-24", "TCGS-320"] else 65
    total_seed = round(acres_input * seed_per_acre, 1)
    total_gypsum = int(acres_input * 200)
    total_ssp = int(acres_input * 100)
    total_urea = int(acres_input * 18)
    total_mop = int(acres_input * 33)
    total_jeevamrutham = int(acres_input * 200)
    total_trichoderma = round(acres_input * 2.0, 1)

    ic1, ic2, ic3, ic4 = st.columns(4)
    ic1.metric("🌱 కావాల్సిన విత్తన పప్పు", f"{total_seed} కిలోలు", f"{acres_input} ఎకరాలకు")
    ic2.metric("🪨 కావాల్సిన జిప్సం (పూత దశలో)", f"{total_gypsum} కిలోలు", f"{int(total_gypsum/50)} బస్తాలు (50kg)")
    ic3.metric("🧪 ఆఖరి దుక్కి రసాయన ఎరువులు", f"SSP: {total_ssp}kg", f"యూరియా: {total_urea}kg | MOP: {total_mop}kg")
    ic4.metric("🌿 సేంద్రియ కావాల్సినవి", f"జీవామృతం: {total_jeevamrutham} లీ", f"ట్రైకోడెర్మా: {total_trichoderma} కిలోలు")

    st.markdown("### 📊 ఆంధ్రప్రదేశ్‌లోని అన్ని ప్రధాన వేరుశనగ రకాల పోలిక పట్టిక")
    comp_rows = []
    for name, d in AP_VARIETIES.items():
        comp_rows.append({
            "వేరుశనగ రకం": name,
            "పంట కాలం": d["duration_text"],
            "ఖరీఫ్ దిగుబడి": d["yield_kharif"],
            "రబీ దిగుబడి": d["yield_rabi"],
            "నూనె శాతం": d["oil_content"],
            "గింజ దిగుబడి (Outturn %)": f"{d['shelling_percent']}%",
            "ప్రత్యేకత": d["special_features"]
        })
    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

# ==============================================================================
# MODULE 2: పంట జీవిత చక్రం (Complete Crop Life Cycle)
# ==============================================================================
elif menu.startswith("2."):
    st.subheader(f"🔄 {selected_variety} - విత్తనం నుండి కోత వరకు 8 దశల జీవిత చక్రం ({total_crop_days} రోజులు)")
    
    timeline_data = []
    for s in lifecycle_stages:
        timeline_data.append({
            "దశ": s["name"],
            "ప్రారంభ రోజు": s["min_day"],
            "ముగింపు రోజు": s["max_day"],
            "రోజుల వ్యవధి": s["days_range"]
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    fig = px.bar(
        timeline_df,
        x=[s["max_day"] - s["min_day"] + 1 for s in lifecycle_stages],
        y="దశ",
        base="ప్రారంభ రోజు",
        orientation="h",
        color="దశ",
        text="రోజుల వ్యవధి",
        title=f"{selected_variety} దశల వారీ కాలపరిమితి (0 నుండి {total_crop_days} రోజులు)"
    )
    fig.update_layout(xaxis_title="విత్తిన తర్వాత రోజులు (DAS)", yaxis_title="", showlegend=False, height=360)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📖 ప్రతి దశలో చేయాల్సిన సేంద్రియ మరియు రసాయన యాజమాన్యం")
    for stage in lifecycle_stages:
        with st.expander(f"{stage['icon']} {stage['name']}  —  [{stage['days_range']}]", expanded=(stage["stage_id"] in [1, 4])):
            sc1, sc2 = st.columns([1, 2])
            with sc1:
                st.image(
                    generate_stage_visual_banner(stage["stage_id"]),
                    caption=stage["name"],
                    use_container_width=True
                )
            with sc2:
                st.markdown(f"**📌 దశ వివరణ:** {stage['summary']}")
                oc, cc = st.columns(2)
                with oc:
                    st.markdown(f"<div class='organic-card'><b>🌿 సేంద్రియ విధానం (Organic):</b><br>{stage['organic_plan'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                with cc:
                    st.markdown(f"<div class='chemical-card'><b>🧪 రసాయన & పోషక విధానం (Chemical):</b><br>{stage['chemical_plan'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                st.info(f"💧 **నీటి & కలుపు యాజమాన్యం:** {stage['water_weed']}")

# ==============================================================================
# MODULE 3: విత్తిన రోజుల ఆధారంగా పనులు (Smart DAS Advisor)
# ==============================================================================
elif menu.startswith("3."):
    st.subheader(f"🗓️ విత్తిన తర్వాత రోజుల (DAS) ఆధారంగా తదుపరి పనుల సూచిక ({selected_variety})")
    
    input_mode = st.radio(
        "రోజులను ఎలా నమోదు చేయాలనుకుంటున్నారు?",
        ["🔢 నేరుగా విత్తిన తర్వాత రోజుల సంఖ్య (Enter Days Directly)", "📅 విత్తిన తేదీని ఎంచుకోవడం ద్వారా (Select Sowing Date)"],
        horizontal=True
    )

    if input_mode.startswith("🔢"):
        das_days = st.slider("విత్తిన తర్వాత ఎన్ని రోజులు అయింది? (Days After Sowing - DAS):", min_value=0, max_value=total_crop_days, value=min(32,total_crop_days), step=1)
    else:
        sowing_date = st.date_input("విత్తిన తేదీని ఎంచుకోండి:", datetime.date.today() - datetime.timedelta(days=32))
        das_days = max(0, (datetime.date.today() - sowing_date).days)

    progress_ratio = min(1.0, das_days / float(total_crop_days))
    st.progress(progress_ratio, text=f"పంట పురోగతి: {das_days} / {total_crop_days} రోజులు ({int(progress_ratio*100)}% పూర్తయింది)")

    current_stage = lifecycle_stages[-1]
    next_stage = None
    for idx, stg in enumerate(lifecycle_stages):
        if stg["min_day"] <= das_days <= stg["max_day"]:
            current_stage = stg
            if idx + 1 < len(lifecycle_stages):
                next_stage = lifecycle_stages[idx + 1]
            break

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.image(generate_stage_visual_banner(current_stage["stage_id"]), caption=f"ప్రస్తుత దశ ({das_days}వ రోజు)", use_container_width=True)
        st.metric("ప్రస్తుత పంట రోజు (DAS)", f"{das_days} రోజులు", f"కోతకు ఇంకా {max(0, total_crop_days - das_days)} రోజులు")

    with col_b:
        st.markdown(f"""
        <div class="stage-box">
            <h3>{current_stage['icon']} ప్రస్తుత దశ: {current_stage['name']} ({current_stage['days_range']})</h3>
            <p style="font-size:16px;">{current_stage['summary']}</p>
        </div>
        """, unsafe_allow_html=True)

        g_start, g_end = v_data["gypsum_window"]
        if g_start <= das_days <= g_end:
            st.markdown(f"""
            <div class="alert-card">
                <b>🚨 అత్యంత కీలక హెచ్చరిక (Gypsum Alert):</b> మీరు ఎంచుకున్న <b>{selected_variety}</b> రకానికి ఇప్పుడు <b>{das_days}వ రోజు</b> నడుస్తోంది. 
                ఇది ఎకరాకు <b>200 కిలోల జిప్సం (Gypsum)</b> వేయడానికి సరైన సమయం! వెంటనే మొక్కల మొదళ్ల దగ్గర వేసి మట్టి ఎగదోయండి.
            </div>
            """, unsafe_allow_html=True)
            
        elif das_days > 45:
            st.warning("⚠️ **జాగ్రత్త:** పంట 45 రోజులు దాటింది కాబట్టి ఊడలు భూమిలో ఉంటాయి. ఇప్పుడు పొలంలో కలుపు తీయడం లేదా గుంటక తోలడం చేయకండి!")

        # TAG-24 Specific Alerts
        if v_data["code"] == "TAG-24" and 15 <= das_days <= 19:
            st.warning("🌿 **TAG-24 ప్రత్యేక సూచన (15-18 రోజులు):** ఈ రకంలో 22వ రోజు నుండే పూత వస్తుంది కాబట్టి, కలుపు మందు (Imazethapyr) పిచికారీని పూత రాకముందే (18వ రోజు లోపు) పూర్తి చేయండి!")
        elif v_data["code"] == "TAG-24" and das_days >= (total_crop_days - 8):
            st.error("🚨 **TAG-24 అత్యవసర కోత హెచ్చరిక (Zero Dormancy Alert):** ట్యాగ్-24 రకానికి నిద్రావస్థ ఉండదు! 75-80% కాయలు పక్వానికి రాగానే వెంటనే కోత కోయండి. ఆలస్యమైతే నేలలోని తేమకు కాయలు భూమిలోనే మొలకెత్తుతాయి!")

    st.markdown("### ✅ ఇప్పుడు మీరు పొలంలో చేయాల్సిన పనులు:")
    c_org, c_chem = st.columns(2)
    with c_org:
        st.markdown(f"<div class='organic-card'><h4>🌿 సేంద్రియ యాజమాన్యం (Organic Action)</h4>{current_stage['organic_plan'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
    with c_chem:
        st.markdown(f"<div class='chemical-card'><h4>🧪 రసాయన & ఎరువుల యాజమాన్యం (Chemical Action)</h4>{current_stage['chemical_plan'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    st.info(f"💧 **నీటి తడి మరియు కలుపు సూచన:** {current_stage['water_weed']}")

    if next_stage:
        st.markdown(f"--- \n#### ⏭️ రాబోయే తదుపరి దశ ({next_stage['days_range']}): **{next_stage['name']}**")
        st.write(f"**ముందస్తు తయారీ:** {next_stage['summary']}")

# ==============================================================================
# MODULE 4: తెగుళ్లు & పురుగుల ఫోటో పరీక్ష (AI Photo Diagnosis)
# ==============================================================================
elif menu.startswith("4."):
    st.subheader("📸 వేరుశనగ తెగుళ్లు & పురుగుల ఫోటో గుర్తింపు మరియు నివారణ")
    st.write("మొక్క ఆకు లేదా కాండం ఫోటోను అప్‌లోడ్ చేయండి. మా AI కంప్యూటర్ విజన్ మోడల్ మచ్చలను గుర్తించి, సేంద్రియ మరియు రసాయన నివారణ చర్యలను అందిస్తుంది.")

    up_col1, up_col2 = st.columns([1, 1])
    with up_col1:
        uploaded_file = st.file_uploader("📂 ఇక్కడ వేరుశనగ ఆకు/మొక్క ఫోటోను అప్‌లోడ్ చేయండి (JPG/PNG):", type=["jpg", "jpeg", "png"])
        use_demo = st.checkbox("🔍 పరీక్ష కోసం నమూనా తెగులు ఫోటోను ఉపయోగించండి", value=(uploaded_file is None))

    with up_col2:
        demo_choice = st.selectbox(
            "నమూనా లేదా లక్షణాల ఆధారంగా తెగులు/పురుగును ఎంచుకోండి:",
            list(DISEASES_PESTS_DB.keys())
        )

    if uploaded_file is not None:
        input_img = Image.open(uploaded_file)
    else:
        v_type = DISEASES_PESTS_DB[demo_choice]["visual_type"]
        input_img = generate_disease_visual_card(v_type)

    annotated_img, cv_metrics = analyze_leaf_image(input_img)
    active_disease_key = cv_metrics["detected_key"] if uploaded_file is not None else demo_choice
    d_info = DISEASES_PESTS_DB[active_disease_key]

    img_c1, img_c2, img_c3 = st.columns(3)
    with img_c1:
        st.image(input_img, caption="1. అప్‌లోడ్ చేసిన అసలు ఫోటో", use_container_width=True)
    with img_c2:
        st.image(annotated_img, caption="2. AI గుర్తించిన తెగులు మచ్చలు (Red Boxes)", use_container_width=True)
    with img_c3:
        st.image(generate_disease_visual_card(d_info["visual_type"]), caption=f"3. {active_disease_key.split('(')[0]} నిర్ధారణ చిత్రం", use_container_width=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 గుర్తించిన సమస్య", active_disease_key.split("(")[0])
    m2.metric("📊 AI నిర్ధారణ శాతం", f"{cv_metrics['confidence']}%")
    m3.metric("⚠️ తీవ్రత స్థాయి", cv_metrics["severity"])
    m4.metric("🍃 ఆకుపై మచ్చల సంఖ్య", f"{cv_metrics['spot_count']} మచ్చలు")

    st.markdown(f"""
    <div class="stage-box">
        <h3>🔍 గుర్తించిన తెగులు / పురుగు: {active_disease_key}</h3>
        <p><b>వర్గం:</b> {d_info['category']} &nbsp;|&nbsp; <b>కారకం:</b> <i>{d_info['pathogen']}</i> &nbsp;|&nbsp; <b>ఆశించే సమయం:</b> {d_info['risk_window']}</p>
        <p><b>📋 ప్రధాన లక్షణాలు:</b><br>{d_info['symptoms_telugu'].replace(chr(10), '<br>')}</p>
    </div>
    """, unsafe_allow_html=True)

    sol_col1, sol_col2 = st.columns(2)
    with sol_col1:
        st.markdown(f"""
        <div class="organic-card">
            <h3>🌿 సేంద్రియ నివారణ చర్యలు (Organic Control)</h3>
            <p style="font-size:15.5px; line-height:1.7;">{d_info['organic_control'].replace(chr(10), '<br>')}</p>
        </div>
        """, unsafe_allow_html=True)
    with sol_col2:
        st.markdown(f"""
        <div class="chemical-card">
            <h3>🧪 రసాయన నివారణ చర్యలు (Chemical Control)</h3>
            <p style="font-size:15.5px; line-height:1.7;">{d_info['chemical_control'].replace(chr(10), '<br>')}</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# MODULE 5: ఈ రోజు మార్కెట్ ధర & ఆదాయం లెక్కింపు (Daily Market Rate Calculator)
# ==============================================================================
elif menu.startswith("5."):
    st.subheader("💰 ఆంధ్రప్రదేశ్ వేరుశనగ మార్కెట్ ధరలు & రోజువారీ రేటు లెక్కింపు")
    st.write(f"తేదీ: **{datetime.date.today().strftime('%d-%m-%Y')}** నాటి ఆంధ్రప్రదేశ్ వ్యవసాయ మార్కెట్ కమిటీ (APMC) ధరలు మరియు మీ పంట నాణ్యత ఆధారంగా వచ్చే ఖచ్చితమైన ధర.")

    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        selected_mandi = st.selectbox("🏪 మీ సమీప మార్కెట్ యార్డును (APMC Mandi) ఎంచుకోండి:", list(AP_MANDI_PRICES.keys()), index=2)
        mandi_info = AP_MANDI_PRICES[selected_mandi]
    with col_m2:
        custom_rate_toggle = st.checkbox("✍️ స్థానిక వ్యాపారి ధరను సొంతంగా నమోదు చేయండి")

    if custom_rate_toggle:
        base_modal = st.number_input("ఈ రోజు క్వింటాల్ సగటు మార్కెట్ ధర (₹):", min_value=3000, max_value=15000, value=mandi_info["modal"], step=50)
    else:
        base_modal = mandi_info["modal"]

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("📉 కనిష్ట ధర (Min)", f"₹{mandi_info['min']:,} / క్వింటాల్")
    p2.metric("⚖️ సగటు ధర (Modal Price)", f"₹{base_modal:,} / క్వింటాల్")
    p3.metric("📈 గరిష్ట ధర (Max)", f"₹{mandi_info['max']:,} / క్వింటాల్")
    p4.metric("🏛️ ప్రభుత్వ మద్దతు ధర (MSP)", f"₹{GOVT_MSP_GROUNDNUT:,} / క్వింటాల్")

    st.markdown("---")
    st.markdown("### 🧮 మీ పంట నాణ్యత & దిగుబడి ఆధారంగా ఈ రోజు ఖచ్చితమైన ఆదాయం లెక్కింపు")

    calc_c1, calc_c2, calc_c3 = st.columns(3)
    with calc_c1:
        input_unit = st.radio("దిగుబడి కొలత:", ["క్వింటాళ్లలో (Quintals - 100 kg)", "బస్తాల్లో (40 కిలోల బస్తాలు - Bags)"])
        if input_unit.startswith("క్వింటాళ్లలో"):
            yield_quintals = st.number_input("మీ మొత్తం దిగుబడి (క్వింటాళ్లు):", min_value=1.0, max_value=500.0, value=15.0, step=0.5)
        else:
            bags_40kg = st.number_input("మొత్తం బస్తాల సంఖ్య (ఒక్కో బస్తా 40 కిలోలు):", min_value=1, max_value=1000, value=38, step=1)
            yield_quintals = round((bags_40kg * 40.0) / 100.0, 2)
            st.caption(f"మొత్తం బరువు: **{yield_quintals} క్వింటాళ్లు**")

    with calc_c2:
        moisture_pct = st.slider("💧 కాయలో తేమ శాతం (Moisture % - ఆదర్శం 8%):", min_value=6.0, max_value=18.0, value=8.0, step=0.5)
        shelling_pct = st.slider(
            "🥜 కాయలో గింజ దిగుబడి శాతం (Outturn / Shelling %):",
            min_value=60.0, max_value=80.0, value=float(v_data["shelling_percent"]), step=1.0
        )

    with calc_c3:
        acres_cultivated = st.number_input("సాగు చేసిన విస్తీర్ణం (ఎకరాల్లో):", min_value=0.5, max_value=100.0, value=1.0, step=0.5)
        cost_per_acre = st.number_input("ఎకరాకు అయిన సాగు ఖర్చు (₹):", min_value=5000, max_value=60000, value=24000, step=1000)

    eff_rate, moist_ded, shell_adj = calculate_quality_adjusted_rate(base_modal, moisture_pct, shelling_pct)
    gross_income = round(yield_quintals * eff_rate, 2)
    total_cost = round(acres_cultivated * cost_per_acre, 2)
    net_profit = round(gross_income - total_cost, 2)

    st.markdown(f"""
    <div class="stage-box">
        <h3>💵 ఈ రోజు మీ పంటకు లభించే నికర ధర మరియు ఆదాయ నివేదిక ({selected_variety})</h3>
        <ul>
            <li><b>మార్కెట్ సగటు ధర:</b> ₹{base_modal:,.2f} / క్వింటాల్</li>
            <li><b>తేమ తగ్గింపు ({moisture_pct}% తేమ):</b> -₹{moist_ded:,.2f} / క్వింటాల్</li>
            <li><b>గింజ దిగుబడి బోనస్ ({shelling_pct}% Outturn):</b> {'+' if shell_adj >= 0 else ''}₹{shell_adj:,.2f} / క్వింటాల్</li>
            <li><b>👉 మీ నాణ్యతకు ఈ రోజు వచ్చే ఖచ్చితమైన క్వింటాల్ ధర:</b> <span style="color:#1B5E20; font-size:20px; font-weight:bold;">₹{eff_rate:,.2f} / క్వింటాల్</span></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    r1.metric("💰 మొత్తం స్థూల ఆదాయం (Gross Value)", f"₹{gross_income:,.2f}")
    r2.metric("🚜 మొత్తం సాగు ఖర్చు (Total Cost)", f"₹{total_cost:,.2f}")
    r3.metric("🏆 రైతు నికర లాభం (Net Profit)", f"₹{net_profit:,.2f}")

    # Mandi Comparison Bar Chart
    mandi_data = []
    for m, v in AP_MANDI_PRICES.items():
        mandi_data.append({
            "మార్కెట్ యార్డు": m, 
            "కనిష్ట ధర": v["min"], 
            "సగటు ధర (Modal)": v["modal"], 
            "గరిష్ట ధర": v["max"]
        })
        
    mandi_df = pd.DataFrame(mandi_data)
    
    fig_m = px.bar(
        mandi_df, 
        x="మార్కెట్ యార్డు", 
        y=["కనిష్ట ధర", "సగటు ధర (Modal)", "గరిష్ట ధర"],
        barmode="group", 
        title="ఆంధ్రప్రదేశ్ ప్రధాన మార్కెట్లలో ఈ రోజు వేరుశనగ ధరల పోలిక (₹/క్వింటాల్)"
    )
    st.plotly_chart(fig_m, use_container_width=True)