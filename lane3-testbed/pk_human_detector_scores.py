"""Fix for LAYERB-PILOT.md section 5: pool_measurement.py ran the roberta detector over
pk_human texts (as half of an AUC-only sample) but never saved detector_p_machine for them.
This runs the detector over all PK-human texts and appends detector_p_machine to
data/scores/pk_human.json, aligned to the existing "ids" order (same load_pk() order).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loaders.essays_loader import load as load_pk  # noqa: E402
from detector.calibration import run_roberta_scores  # noqa: E402

SCORE_PATH = Path(__file__).resolve().parent / "data" / "scores" / "pk_human.json"


def main():
    pk = list(load_pk())
    pk_ids = [r["author_id"] for r in pk]
    pk_texts = [r["text"] for r in pk]

    existing = json.loads(SCORE_PATH.read_text())
    assert existing["ids"] == pk_ids, "PK id order mismatch vs pk_human.json"

    t0 = time.time()
    print(f"scoring {len(pk_texts)} PK-human texts with roberta detector", file=sys.stderr)
    scores = run_roberta_scores(pk_texts)
    print(f"done in {time.time() - t0:.1f}s, n={len(scores)}", file=sys.stderr)

    assert len(scores) == len(pk_ids)
    existing["detector_p_machine"] = scores
    SCORE_PATH.write_text(json.dumps(existing))
    print(f"wrote {SCORE_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
