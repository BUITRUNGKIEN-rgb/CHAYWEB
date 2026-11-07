"""Export actual AI02 baseline/improved joblib from your Python training folder.

Run this script from any working directory using:
  python export_models_for_web.py --project /path/to/UNETI12_ODD3_AI02
Refuses to package synthetic smoke-test artifacts as genuine AI weights.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description='Copy validated AI02 models into a GitHub Pages site.')
    parser.add_argument('--project',default='.',help='folder with model/, results/, src/features.py')
    parser.add_argument('--allow-small',action='store_true',help='allow nonstandard dataset sizes (still must not be synthetic)')
    args=parser.parse_args()
    project=Path(args.project).resolve()
    result_file=project/'results/metrics.json'
    if not result_file.is_file():
        parser.error('Không tìm thấy results/metrics.json. Hãy huấn luyện trước.')
    result=json.loads(result_file.read_text('utf-8'))
    if result.get('task') != 'AI02': parser.error('Chỉ chấp nhận mã đề AI02.')
    if result.get('experimental_mode')=='SMOKE_SYNTHETIC_DO_NOT_REPORT':
        parser.error('Không được đưa mô hình từ chế độ --fast / ảnh giả lập lên website chính thức.')
    n=int(result.get('dataset',{}).get('n_after_cleanup',0))
    if n<2000 and not args.allow_small:
        parser.error(f'Chỉ có {n} ảnh sau làm sạch; bộ TrashNet chuẩn có khoảng 2527 ảnh. Dùng --allow-small nếu dữ liệu thật có số lượng khác.')
    src_features=project/'src/features.py'
    if not src_features.is_file():parser.error('Không có src/features.py của dự án gốc.')
    models={name:project/'model'/f'{name}.joblib' for name in ('baseline','improved')}
    for name,path in models.items():
        if not path.is_file():parser.error(f'Thiếu {path}.')
    # No unpickling of untrusted model weights in this export script.
    for name,path in models.items():
        shutil.copy2(path,BASE/'models'/path.name)
        print('Export:',name,'%.2f MB'%(path.stat().st_size/(1024*1024)))
    shutil.copy2(src_features,BASE/'python_features.py')
    manifest={
        'trained':True,
        'models':{'baseline':True,'improved':True},
        'dataset':{'total_after_cleanup':n,'name':'TrashNet (người dự thi tự xác minh nguồn)'},
        'macro_f1':{model:result[model].get('macro_f1') for model in ('baseline','improved')},
        'training_provenance':'Đây là kết quả của tệp metrics.json; không chứng nhận nguồn dữ liệu. Người dự thi tự chịu trách nhiệm xác minh.',
        'feature_source':'python_features.py copied from src/features.py',
        'python_packages':'Use compatible scikit-learn, scikit-image, Pillow, numpy, joblib; Pyodide pinned to v314.0.7.'
    }
    (BASE/'models/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Xong. Đưa toàn bộ các tệp trong thư mục web lên thư mục gốc của repository GitHub Pages.')
    print('Macro-F1 theo metrics.json:',manifest['macro_f1'])

if __name__=='__main__': main()
