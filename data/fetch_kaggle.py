import os
import requests
import zipfile
import io

KAGGLE_TOKEN = "KGAT_d2a659f9c5fc428a7cfbd46cbd59fe31"
HEADERS = {"Authorization": f"Bearer {KAGGLE_TOKEN}"}
DATASETS = [
    "nudratabbas/global-supply-chain-risk-and-logistics-2024-2026",
    "kuldeepjangra/global-supply-chain-disruption-dataset-20152026"
]

def download_and_extract(dataset_ref, dest_folder):
    print(f"Downloading {dataset_ref}...")
    url = f"https://www.kaggle.com/api/v1/datasets/download/{dataset_ref}"
    response = requests.get(url, headers=HEADERS, stream=True)
    
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(dest_folder)
        print(f"Extracted to {dest_folder}")
    else:
        print(f"Failed to download {dataset_ref}: {response.status_code} {response.text}")

if __name__ == "__main__":
    os.makedirs("data/raw_kaggle", exist_ok=True)
    for ds in DATASETS:
        # Create a safe folder name
        folder_name = ds.split('/')[-1]
        download_and_extract(ds, f"data/raw_kaggle/{folder_name}")
