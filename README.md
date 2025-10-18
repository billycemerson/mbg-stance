# Stance Detection on Indonesia’s “Makan Bergizi Gratis (MBG)” Policy

## Project Description
This project aims to analyze **public stance toward Indonesia’s “Makan Bergizi Gratis (MBG)” policy** — a national free meal initiative introduced by the government.

Using **YouTube comments** as the primary data source, the project classifies public opinions into three stance categories:

- **FAVOR** — Supportive or positive stance toward MBG  
- **AGAINST** — Critical or negative stance toward MBG  
- **NEUTRAL** — Informative or unclear stance  

A fine-tuned **IndoBERT** model will be developed to automatically classify stances and provide insight into how Indonesian citizens respond to the MBG policy online.

---

## Project Progress

| Stage | Description | Status |
|--------|--------------|--------|
| **Data Collection** | Scraping YouTube videos & comments related to MBG using YouTube API v3 | ✅ Completed |
| **Data Labeling** | Labeling comments as FAVOR / AGAINST / NEUTRAL using Label Studio | 🟡 In Progress |
| **Model Fine-Tuning** | Fine-tuning IndoBERT for stance detection | ⬜ Planned |
| **Evaluation & Visualization** | Measuring model accuracy and analyzing stance distribution | ⬜ Planned |
| **Documentation & Deployment** | Preparing README, notebooks, and demo | ⬜ Planned |

---

## Tech Stack
- **Python 3.10+**
- **Transformers (Hugging Face)**
- **Pandas**, **Scikit-learn**, **Matplotlib**
- **Label Studio** (for annotation)
- **YouTube Data API v3** via `googleapiclient`

---