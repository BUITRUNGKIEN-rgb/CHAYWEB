"""Inference-only Python bridge loaded inside the browser via Pyodide.

Replicates the original Streamlit app's inference exactly:
  src.features.image_features(image_path, 'baseline'|'improved')
  -> pipeline.predict / predict_proba
Only trusted joblib models may be loaded. Never load third-party arbitrary joblib.
"""
import json
from pathlib import Path
import joblib
import numpy as np
from PIL import Image
from src.features import LABELS, image_features

MODELS = {}


def load_model_file(path, slot):
    if slot not in ('baseline', 'improved'):
        raise ValueError('Loại mô hình không hợp lệ')
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or not {'pipeline', 'feature_kind'} <= set(bundle):
        raise ValueError('Tệp joblib không đúng cấu trúc của bài AI02')
    if bundle['feature_kind'] != slot:
        raise ValueError(f'Model {slot} cần feature_kind={slot!r}')
    model = bundle['pipeline']
    if not hasattr(model, 'predict') or not hasattr(model, 'predict_proba'):
        raise ValueError('Model phải hỗ trợ predict và predict_proba')
    if set(map(str, model.classes_)) != set(LABELS):
        raise ValueError('Mô hình không đủ 6 lớp TrashNet')
    MODELS[slot] = bundle
    return 'ok'


def predict_image_path(path, slot):
    if slot not in MODELS:
        raise RuntimeError('Bạn chưa nạp mô hình: '+slot)
    if Path(path).stat().st_size > 10*1024*1024:
        raise ValueError('Ảnh quá lớn (>10 MB)')
    with Image.open(path) as image:
        if image.width*image.height>22_000_000:
            raise ValueError('Độ phân giải ảnh quá lớn (hơn 22 triệu pixel)')
        image.verify()
    bundle=MODELS[slot]
    vec=image_features(path,bundle['feature_kind']).reshape(1,-1)
    model=bundle['pipeline']
    pred=str(model.predict(vec)[0])
    probs=model.predict_proba(vec)[0]
    scores={str(k):float(v) for k,v in zip(model.classes_,probs)}
    if pred not in scores:
        raise ValueError('Thiếu nhãn dự đoán trong xác suất mô hình')
    if not np.all(np.isfinite(probs)):
        raise ValueError('Mô hình sinh ra xác suất không hợp lệ')
    return json.dumps({'label':pred,'confidence':float(scores[pred]),
                       'probabilities':scores,'feature_kind':slot},ensure_ascii=False)
