/* Runs exactly the project's scikit-learn pipelines in the user's browser via Pyodide.
 * No Python backend, API key, remote inference, or image upload is used.
 * NOTE: the FIRST RUN requires Internet to load the Pyodide scientific stack.
 */
'use strict';
const PYODIDE_VERSION='314.0.7';
const BASE_URL=`https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
let pyodidePromise=null;
let loadedModels=new Set();
function notify(id,title,detail){self.postMessage({type:'status',id,title,detail});}
async function startPython(id){
  if(pyodidePromise) return pyodidePromise;
  pyodidePromise=(async()=>{
    notify(id,'Đang tải môi trường Python...','Nạp WebAssembly từ CDN cho lần chạy đầu tiên.');
    importScripts(BASE_URL+'pyodide.js');
    const py=await self.loadPyodide({indexURL:BASE_URL});
    notify(id,'Đang tải thư viện AI...','Nạp NumPy, SciPy, scikit-learn, scikit-image, Pillow và joblib.');
    await py.loadPackage(['numpy','scipy','scikit-learn','scikit-image','pillow','joblib']);
    notify(id,'Đang đồng bộ tính năng...','Nạp lại chính bộ trích đặc trưng Python của bài thi AI02.');
    const response=await fetch('./python_features.py',{cache:'no-store'});
    if(!response.ok) throw Error('Không đọc được python_features.py từ GitHub Pages.');
    const featuresCode=await response.text();
    py.FS.mkdirTree('/home/pyodide/src');
    py.FS.writeFile('/home/pyodide/src/__init__.py','');
    py.FS.writeFile('/home/pyodide/src/features.py',featuresCode);
    const bridgeResponse=await fetch('./python_bridge.py',{cache:'no-store'});
    if(!bridgeResponse.ok)throw Error('Không đọc được python_bridge.py.');
    const bridgeCode=await bridgeResponse.text();
    await py.runPythonAsync(bridgeCode);
    return py;
  })().catch(error=>{pyodidePromise=null;throw error;});
  return pyodidePromise;
}
async function loadModel(py,slot,modelBytes,id){
  if(loadedModels.has(slot)&&!modelBytes)return;
  const filename=slot==='baseline'?'baseline.joblib':'improved.joblib';
  notify(id,'Đang nạp mô hình...','Đọc trọng số mô hình '+filename+' để bắt đầu dự đoán.');
  let data;
  if(modelBytes) data=new Uint8Array(modelBytes);
  else {
    const response=await fetch('./models/'+filename,{cache:'force-cache'});
    if(!response.ok)throw Error('Thiếu '+filename+'. Hãy chạy export_models_for_web.py rồi đẩy thư mục models lên GitHub.');
    data=new Uint8Array(await response.arrayBuffer());
  }
  if(data.byteLength>200*1024*1024)throw Error('Trọng số mô hình quá lớn (>200 MB).');
  const p='/tmp/ai02_'+slot+'.joblib';py.FS.writeFile(p,data);
  try{
    const ok=py.runPython(`load_model_file(${JSON.stringify(p)}, ${JSON.stringify(slot)})`);
    if(ok!=='ok')throw Error('Không thể khởi tạo mô hình '+slot);
    loadedModels.add(slot);
  }finally{try{py.FS.unlink(p);}catch(_){/* FS cleanup */}}
}
async function infer(message){
  const {id,slot,imageBytes,modelBytes}=message;
  try{
    if(!['baseline','improved'].includes(slot))throw Error('Mô hình không hợp lệ.');
    if(!imageBytes||imageBytes.byteLength>10*1024*1024)throw Error('Ảnh thiếu hoặc vượt giới hạn 10 MB.');
    const py=await startPython(id);
    await loadModel(py,slot,modelBytes,id);
    notify(id,'Đang phân tích hình ảnh...','Tính HOG, histogram màu, LBP và chạy mô hình AI trên trình duyệt.');
    // Python's PIL accepts images based on file magic bytes, no extension required.
    const file='/tmp/ai02_uploaded_image';
    py.FS.writeFile(file,new Uint8Array(imageBytes));
    let result;
    try {
      const raw=py.runPython(`predict_image_path(${JSON.stringify(file)}, ${JSON.stringify(slot)})`);
      result=JSON.parse(raw);
    }finally{try{py.FS.unlink(file);}catch(_){/* FS cleanup */}}
    self.postMessage({type:'result',id,result});
  }catch(err){
    let msg=(err&&err.message)||String(err);
    if(/Failed to fetch|NetworkError|importScripts/i.test(msg)) msg+=' Hãy kiểm tra Internet hoặc trình chặn CDN. Lần đầu trang cần tải Pyodide.';
    if(/InconsistentVersionWarning|ModuleNotFoundError|unsupported pickle|UnpicklingError|AttributeError/i.test(msg)) msg+=' Kiểm tra tương thích phiên bản: bộ huấn luyện và Pyodide nên dùng scikit-learn 1.8.x.';
    self.postMessage({type:'error',id,message:msg.slice(0,1000)});
  }
}
self.onmessage=(event)=>{const d=event.data;if(d&&d.type==='predict')infer(d);};
