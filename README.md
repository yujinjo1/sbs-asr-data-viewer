📖 sbs-asr-data-viewer

Automatic Speech Recognition (ASR) 데이터셋을 시각화하고 관리하기 위한 도구입니다.
파인튜닝된 모델과 음성 데이터셋을 탐색/검증하는 데 유용합니다.

🚀 Features

🎧 음성 데이터셋 로드 및 시각화 (sbs_datasets/, sbs_datasets_processed/)

📊 STFT 기반 스펙트로그램 분석 (stft.ipynb)

🤖 파인튜닝된 모델 결과 확인 (fine-tuned_models/)

🔔 간단한 알림/오디오 출력 (bell.mp3, sample.mp3)

📂 Project Structure
sbs-asr-data-viewer/
│── main.py                 # 실행 스크립트
│── pyproject.toml           # 프로젝트 의존성 (uv 기반)
│── uv.lock                  # 의존성 lock 파일
│── stft.ipynb               # 데이터 시각화 노트북
│── README.md                # 프로젝트 설명
│── .gitignore               # 무시 규칙
│── .python-version          # Python 버전 지정
│
├── sbs_datasets/            # (로컬) 원본 데이터셋
├── sbs_datasets_processed/  # (로컬) 전처리된 데이터셋
├── fine-tuned_models/       # (로컬) 모델 체크포인트
└── wandb/                   # (로컬) 학습 로그


⚠️ 주의: 대용량 데이터(sbs_datasets/, fine-tuned_models/, wandb/)는 GitHub에 올라가지 않습니다.
필요하다면 [Google Drive/HuggingFace Hub]에서 받아야 합니다.

🔧 Installation
1. Clone Repository
git clone https://github.com/yujinjo1/sbs-asr-data-viewer.git
cd sbs-asr-data-viewer

2. Install Dependencies (with uv
)
uv sync

3. Activate Virtual Environment
uv venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows (PowerShell)

▶️ Usage
Run main script
uv run python main.py

Jupyter Notebook
uv run jupyter notebook stft.ipynb

📦 Data & Models

데이터셋: sbs_datasets/, sbs_datasets_processed/

모델: fine-tuned_models/

로그: wandb/

이들은 GitHub에 포함되지 않음 → Google Drive or HuggingFace Hub에서 다운로드 필요.
