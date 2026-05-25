# EBV-related Disease Prediction App

基于 Random Forest 4-feature 模型的 EBV 相关疾病预测 Web 应用，使用 Streamlit 构建，可部署至 Streamlit Community Cloud。

## 目录结构

```
EBV-streamlit-app/
├── app.py                     # Streamlit 主程序
├── RF_4feature_final.pkl      # 训练好的模型 bundle (model / feature_cols / cutoff / loocv_auc)
├── requirements.txt           # Python 依赖
├── runtime.txt                # Python 版本 (python-3.11)
├── .streamlit/config.toml     # Streamlit 配置
├── .gitignore
└── README.md
```

## 输入特征 (4 个)

1. `DNA/WBC` (0 / 1)
2. `Co-infection` (0 / 1)
3. `Relative abundance` (0–1 连续值)
4. `DNA Reads` (整数)

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

打开 http://localhost:8501 即可使用。

## 部署到 Streamlit Community Cloud

1. **新建 GitHub 仓库**，将本 `EBV-streamlit-app/` 文件夹下所有内容（包括 `RF_4feature_final.pkl`）推送到该仓库。
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

## 备注

- 模型加载使用 `@st.cache_resource`，避免重复反序列化。
- SHAP 力图会在每次预测时生成并显示。
- 若需要更新依赖版本，请同步修改 `requirements.txt` 后重新部署。
