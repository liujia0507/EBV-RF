import os
import streamlit as st
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt

# 加载随机森林模型 (字典格式: {"model", "feature_cols", "cutoff", ...})
MODEL_PATH = os.path.join(os.path.dirname(__file__), "EBV_RF_model.pkl")


@st.cache_resource
def load_bundle(path: str):
    return joblib.load(path)


bundle = load_bundle(MODEL_PATH)
model = bundle["model"]
feature_names = bundle["feature_cols"]
cutoff = bundle.get("cutoff", 0.5)

# Streamlit 用户界面
st.title("EBV Pathogenicity Prediction APP (RF 6-Feature Model)")
st.caption(
    "Features: Co-infection, Relative abundance, DNA Reads, DNA/WBC, CCL, CGlu | "
    f"Youden Cutoff: {cutoff:.3f}"
)

# 用户输入特征数据 (顺序需与训练时一致)
co_infection = st.selectbox("Co-infection (0 or 1):", options=[0, 1])
relative_abundance = st.number_input(
    "Relative abundance (0-1):",
    min_value=0.0, max_value=1.0, value=0.5, step=0.01, format="%.4f",
)
dna_reads = st.number_input(
    "DNA Reads:", min_value=0, max_value=1000000, value=100, step=1
)
dna_wbc = st.selectbox("DNA/WBC (0 or 1):", options=[0, 1])
ccl = st.number_input(
    "CCL (CSF chloride, mmol/L):",
    min_value=0.0, max_value=200.0, value=119.0, step=0.1, format="%.1f",
)
cglu = st.number_input(
    "CGlu (CSF glucose, mmol/L):",
    min_value=0.0, max_value=30.0, value=2.95, step=0.01, format="%.2f",
)

# 将输入的数据转化为模型的输入格式 (顺序与 feature_cols 一致)
feature_values = [co_infection, relative_abundance, dna_reads, dna_wbc, ccl, cglu]
features_df = pd.DataFrame([feature_values], columns=feature_names)

# 当点击按钮时进行预测
if st.button("Predict"):
    # 进行预测
    predicted_proba = model.predict_proba(features_df)[0]
    prob_positive = predicted_proba[1]
    predicted_class = int(prob_positive >= cutoff)

    # 显示预测结果
    st.write(f"**Predicted Class:** {predicted_class} (0: Non-EBV-related, 1: EBV-related)")
    st.write(
        f"**Prediction Probabilities:** [Non-EBV: {predicted_proba[0]:.4f}, "
        f"EBV: {predicted_proba[1]:.4f}]"
    )
    st.write(f"**Decision Cutoff (Youden):** {cutoff:.3f}")

    # 根据预测结果提供建议
    if predicted_class == 1:
        advice = (
            f"According to our model, this case has a high risk of being EBV-related. "
            f"The predicted probability of EBV-related disease is {prob_positive*100:.1f}%. "
            "We recommend further clinical evaluation and EBV-targeted testing."
        )
    else:
        advice = (
            f"According to our model, this case has a low risk of being EBV-related. "
            f"The predicted probability of NOT being EBV-related is {(1-prob_positive)*100:.1f}%. "
            "However, clinical correlation is still recommended."
        )

    st.write(advice)

    # 计算并显示SHAP值 (Pipeline: imputer -> clf, 需要在 imputer 之后对 clf 解释)
    try:
        imputer = model.named_steps["imputer"]
        clf = model.named_steps["clf"]
        X_imputed = pd.DataFrame(imputer.transform(features_df), columns=feature_names)

        explainer = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(X_imputed)

        # 兼容新旧版 shap 输出格式
        if isinstance(shap_values, list):
            sv = shap_values[predicted_class]
            expected_value = explainer.expected_value[predicted_class]
        elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
            sv = shap_values[:, :, predicted_class]
            expected_value = explainer.expected_value[predicted_class]
        else:
            sv = shap_values
            expected_value = explainer.expected_value

        # 瀑布图 (waterfall plot)
        shap.plots.waterfall(
            shap.Explanation(
                values=sv[0],
                base_values=expected_value,
                data=X_imputed.iloc[0],
                feature_names=feature_names,
            ),
            show=False,
        )

        out_path = os.path.join(os.path.dirname(__file__), "shap_waterfall_plot.png")
        svg_path = os.path.join(os.path.dirname(__file__), "shap_waterfall_plot.svg")
        plt.savefig(out_path, bbox_inches="tight", dpi=300)
        plt.savefig(svg_path, bbox_inches="tight", format="svg")
        plt.close()
        st.image(out_path)

        with open(svg_path, "rb") as f:
            st.download_button(
                label="📥 Download SHAP Waterfall Plot (SVG)",
                data=f,
                file_name="shap_waterfall_plot.svg",
                mime="image/svg+xml",
            )
    except Exception as e:
        st.warning(f"SHAP visualization failed: {e}")
