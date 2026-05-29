import os
import shutil

import kagglehub


def download_superstore():
    print("Descargando dataset...")
    path = kagglehub.dataset_download("vivek468/superstore-dataset-final")
    print(f"Dataset descargado en caché: {path}")

    # Mover a data/raw
    dest = "data/raw"
    os.makedirs(dest, exist_ok=True)

    for file in os.listdir(path):
        src = os.path.join(path, file)
        dst = os.path.join(dest, file)
        shutil.copy2(src, dst)
        print(f"Copiado: {file} → {dest}")

if __name__ == "__main__":
    download_superstore()