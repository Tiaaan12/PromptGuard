# PromptGuard

**A traditional machine-learning application for detecting potential prompt-injection attempts.**

PromptGuard classifies submitted text as **Benign** or **Injection** using a saved scikit-learn pipeline. The application uses Streamlit for the Python app and a React/TypeScript custom component for the chat interface.

> PromptGuard is a lightweight classifier, not a complete prompt-injection security solution. It can miss unfamiliar or context-dependent attacks. Its Linear SVM decision score is a raw model score, not a calibrated probability or confidence percentage. A detection flag does not mean the application has blocked an action.

## Contents

- [Features](#features)
- [Model](#model)
- [Recorded evaluation results](#recorded-evaluation-results)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Run locally](#run-locally)
- [Rebuild the frontend](#rebuild-the-frontend)
- [Deploy to Streamlit Community Cloud](#deploy-to-streamlit-community-cloud)
- [Reproducibility and data notes](#reproducibility-and-data-notes)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)

## Features

- Classifies text prompts as benign or potential prompt injection.
- Displays the predicted label, numeric target, and raw SVM decision score.
- Explains the classifier configuration in an expandable analysis panel.
- Preserves individual detection results in the conversation history.
- Includes exploratory-analysis figures, model-comparison outputs, and error-analysis files.
- Uses a saved preprocessing-and-classification pipeline for inference.

## Model

| Setting | Selected configuration |
|---|---|
| Algorithm | Linear Support Vector Machine (`LinearSVC`) |
| Text representation | Character-level TF-IDF (`char_wb`) |
| Character n-grams | 3–5 |
| Regularization | `C = 1` |
| Class weighting | `balanced` |
| Training version | V3 synthetic augmentation |
| Labels | Benign = `0`; Injection = `1` |
| Saved pipeline | `promptguard/ml/model/promptguard_pipeline.joblib` |
| Metadata | `promptguard/ml/model/model_information.json` |

The saved pipeline contains the feature transformation and classifier. Load this pipeline for predictions; do not separately fit a new vectorizer at inference time. The displayed SVM decision score is not a probability.

## Recorded evaluation results

The following values are from the project's recorded evaluation artifacts. They describe those specific test splits, not a guarantee of performance on future prompts.

| Evaluation | Accuracy | Precision | Recall | F1-score |
|---|---:|---:|---:|---:|
| Internal test, V3 | 99.45% | 97.08% | 90.71% | 93.79% |
| External test, V3 | 81.53% | 99.66% | 72.26% | 83.77% |

The external dataset's characteristics informed the design of the augmentation categories. Therefore, the external results should be interpreted as a robustness/adaptation evaluation, not as a completely untouched independent benchmark. Some manually constructed, document-embedded injection prompts were also missed; these cases are part of the project's known limitations.

## Project structure

The repository currently keeps the application inside the `promptguard/` directory:

```text
repository-root/
├── README.md
├── requirements.txt       # Exported, pinned environment for coursework/manual pip setup
└── promptguard/
    ├── app.py
    ├── pyproject.toml
    ├── uv.lock             # Used by Community Cloud for this app
    ├── ml/
    │   ├── data/
    │   │   ├── raw/
    │   │   ├── processed/
    │   │   ├── external/
    │   │   └── augmented/
    │   ├── model/
    │   │   ├── promptguard_pipeline.joblib
    │   │   └── model_information.json
    │   ├── notebook/
    │   ├── results/
    │   │   ├── metrics/
    │   │   ├── errors/
    │   │   └── visualizations/
    │   └── src/
    └── promptguard/
        ├── __init__.py
        ├── pyproject.toml      # Streamlit component registration
        └── frontend/
            ├── package.json
            ├── package-lock.json
            ├── src/
            └── build/          # Built files served by Streamlit
```

If a file is absent from the actual repository, update this tree to match before submission.

## Requirements

- Python version compatible with the saved scikit-learn pipeline. Use the same Python minor version as local development when deploying.
- Node.js and npm for rebuilding the React component.
- `uv` for the current Python development workflow.
- A GitHub repository for deployment.

The Python project dependencies are managed in `promptguard/pyproject.toml` and `promptguard/uv.lock`. Ensure all direct imports used by the app and ML code are declared there, including the correct versions of Streamlit, scikit-learn, joblib, pandas, NumPy, and Matplotlib if used by the scripts. Because the model is serialized with scikit-learn, pin the scikit-learn version used to create the saved pipeline.

To check the versions in the working environment, run this from `promptguard/`:

```powershell
uv run python -c "import streamlit, sklearn, joblib, pandas, numpy; print('streamlit', streamlit.__version__); print('scikit-learn', sklearn.__version__); print('joblib', joblib.__version__); print('pandas', pandas.__version__); print('numpy', numpy.__version__)"
```

Add any missing direct dependencies to `pyproject.toml` using the versions you verified, then refresh the lock and sync the environment:

```powershell
uv lock
uv sync
```

Export a pinned, pip-compatible dependency list for the course submission from `promptguard/`:

```powershell
uv export --format requirements-txt --no-hashes --no-dev --no-emit-project -o ..\requirements.txt
```

Then add this line as the **first line** of the repository-root `requirements.txt` so a manual pip installation also installs the local custom component package:

```text
-e ./promptguard
```

The repository-root `requirements.txt` is the portable dependency list for the course submission and manual pip setup. The Streamlit app is located at `promptguard/app.py`, so Community Cloud will find `promptguard/uv.lock` beside the entry point and use that lockfile first. Keep `pyproject.toml` and `uv.lock` updated together. Streamlit recommends one active dependency source per app; see the [Streamlit dependency documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).

## Run locally

From the repository root:

```powershell
cd promptguard
uv sync
uv run streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Rebuild the frontend

Rebuild the frontend whenever its React/TypeScript source changes. From the repository root:

```powershell
cd promptguard/promptguard/frontend
npm ci
npm run build
```

If `package-lock.json` is not present, use `npm install` instead of `npm ci` and commit the generated lockfile. The build output must exist at `promptguard/promptguard/frontend/build/` because the component-level `pyproject.toml` registers that directory as `asset_dir`.

Check that the compiled files are tracked by Git. The build output is needed for the Python component package to serve the frontend on deployment; do not accidentally omit it through `.gitignore`.

## Deploy to Streamlit Community Cloud

1. Push the final, tested code and required assets to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and choose **Create app**.
3. Select the repository, deployment branch (usually `main`), and entry point `promptguard/app.py`.
4. Choose the same Python version used locally and deploy the app.
5. Watch the deployment logs. Confirm dependency installation succeeds and the custom component assets are found.
6. Test the deployed URL in a fresh browser session with benign, direct-injection, and document-embedded prompts. Verify that the result cards remain attached to their respective messages after multiple submissions.
7. Add the final public URL to this README and to the project submission.

Official instructions: [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app) and [custom components v2, package-based components](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/package-based).

### Pre-deployment Git checks

Run these commands from the repository root:

```powershell
git status
git diff --check
git diff --cached --stat
```

Stage the intended app, component source, compiled frontend assets, ML source, saved model, required datasets, results, documentation, and dependency files. Do not commit virtual environments, `node_modules`, caches, private credentials, or local machine-specific paths. Check dataset redistribution terms and individual file sizes before pushing.

Example commit workflow:

```powershell
git add README.md requirements.txt
git add promptguard/app.py promptguard/pyproject.toml promptguard/uv.lock
git add promptguard/promptguard/
git add promptguard/ml/src/ promptguard/ml/model/ promptguard/ml/results/
git add promptguard/ml/data/
git status
git diff --cached --stat
git commit -m "Prepare PromptGuard for deployment"
git push origin main
```

Review the staged files carefully. If excluding `promptguard/ml/data/processed/` or other large files, make sure the submission still meets the course's dataset and reproducibility requirements and that any omitted data can be obtained from a documented source.

## Reproducibility and data notes

- The internal dataset has 20,000 prompts: 19,083 benign and 917 injection.
- The standard internal split contains 16,000 training samples and 4,000 test samples.
- The external dataset has 5,441 rows; the reported external evaluation uses its 1,229-row test split.
- V1, V2, and V3 contain 80, 115, and 210 cumulative synthetic training examples, respectively.
- Keep the original data source, license/permission, processing notes, and data dictionary with the submission where permitted.
- The internal test set was examined across multiple augmentation versions. Report this transparently; do not describe it as having been used only once for an untouched final evaluation.

## Known limitations

- The primary dataset is strongly imbalanced toward benign prompts.
- Synthetic examples may not cover the full diversity of real attacks.
- Character n-grams may miss contextual relationships in complex, document-embedded instructions.
- The external dataset informed augmentation design, so the external evaluation is not completely independent of development.
- The SVM decision score is not a calibrated probability.
- The classifier flags potential injection; it does not itself provide a general-purpose conversational answer or guarantee that an attack is blocked.

## Troubleshooting

**The component says it must be declared in `pyproject.toml`.** Confirm that `promptguard/promptguard/pyproject.toml` contains the component registration and that its `asset_dir = "frontend/build"` directory exists. Install/update the Python project from `promptguard/` and restart Streamlit.

**The component loads locally but not in deployment.** Confirm the built `frontend/build/` assets and both relevant `pyproject.toml` files are committed, and check the deployment dependency-install logs.

**The saved model fails to load.** Check that the deployed scikit-learn and Python versions are compatible with the versions used to save `promptguard_pipeline.joblib`.

**The detector misses an injection prompt.** This is a known model limitation. Record the case for error analysis; do not interpret the SVM score as a calibrated confidence percentage.

## Dataset attribution and deployment link

- **Primary dataset source:** Add the exact Kaggle dataset URL and the applicable license/permission before submission.
- **External dataset source:** Add the exact source URL and license/permission before submission.
- **Live application:** Add the deployed Streamlit URL after deployment.
