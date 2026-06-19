from pathlib import Path
import shutil


DATASET_DIR = Path(__file__).resolve().parents[1] / "data" / "facturas_generadas"


def main() -> None:
    originals = sorted(path for path in DATASET_DIR.glob("factura_*.*") if int(path.stem.split("_")[1]) <= 10)
    if len(originals) < 10:
        raise SystemExit("Se requieren las 10 facturas originales extraidas del ZIP.")
    for index in range(11, 21):
        source = originals[(index - 11) % len(originals)]
        target = DATASET_DIR / f"factura_{index:03d}{source.suffix.lower()}"
        if not target.exists():
            shutil.copy2(source, target)
            print(f"creada {target.name} desde {source.name}")


if __name__ == "__main__":
    main()
