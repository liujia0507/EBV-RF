# EBV-related Disease Prediction App

基于 Random Forest 6-feature 模型的 EBV 相关疾病预测 Web 应用，使用 Streamlit 构建，可部署至 Streamlit Community Cloud。

## 目录结构

```
EBV-streamlit-app/
├── app.py                     # Streamlit 主程序
├── EBV_RF_model.pkl           # 训练好的模型 bundle (model / feature_cols / cutoff / loocv_auc)
├── requirements.txt           # Python 依赖
├── runtime.txt                # Python 版本 (python-3.11)
├── .streamlit/config.toml     # Streamlit 配置
├── .devcontainer/
│   └── devcontainer.json      # VS Code Dev Container 配置
├── .gitignore
└── README.md
```

## 输入特征 (6 个)

按模型训练时的特征顺序：

1. `Co-infection` (0 / 1)
2. `Relative abundance` (0–1 连续值)
3. `DNA Reads` (整数)
4. `DNA/WBC` (0 / 1)
5. `CCL` — CSF chloride (mmol/L, 连续值, 如 119.0)
6. `CGlu` — CSF glucose (mmol/L, 连续值, 如 2.95)

## 模型

- **算法**: Random Forest (scikit-learn Pipeline: SimpleImputer → RandomForestClassifier)
- **决策阈值**: Youden 指数最优 cutoff (显示在应用标题栏)
- **输出**: 二分类概率 + 预测类别 (0: Non-EBV-related, 1: EBV-related)

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

打开 http://localhost:8501 即可使用。

## 部署到 Streamlit Community Cloud

1. **新建 GitHub 仓库**，将本 `EBV-streamlit-app/` 文件夹下所有内容（包括 `EBV_RF_model.pkl`）推送到该仓库。
   ```bash
   cd EBV-streamlit-app
   git init
   git add .
   git commit -m "Initial commit: EBV prediction app"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
   > 模型文件约 900 KB，远小于 GitHub 单文件 100 MB 限制，无需 Git LFS。

2. **登录** https://share.streamlit.io ，点击 **"New app"**。

3. 选择 GitHub 仓库、分支（`main`）、主文件路径填 `app.py`，点击 **Deploy**。

4. 等待几分钟构建完成后即可获得公共访问 URL。

## 功能说明

- 模型加载使用 `@st.cache_resource`，避免重复反序列化。
- 预测后自动生成 **SHAP 瀑布图 (waterfall plot)**，展示各特征对 EBV 风险的正负贡献（红色 = 正向，蓝色 = 负向）。
- 支持 **下载 SHAP 瀑布图 SVG** 矢量格式，便于投稿和展示。
- 预测结果附带临床建议文本。
- 决策阈值基于 Youden 指数最优 cutoff。

## 备注

- 若需要更新依赖版本，请同步修改 `requirements.txt` 后重新部署。
- 特征输入顺序必须与 `feature_cols` 一致，不可随意调换。
