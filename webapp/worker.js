// 導入 ONNX Runtime Web 版本的 JavaScript 檔案
importScripts("https://cdn.jsdelivr.net/npm/onnxruntime-web@1.15.1/dist/ort.min.js");

let busy = false;

// 當收到訊息時執行的事件處理器
onmessage = async (event) => {
    
    if (busy) {
        return;
    }
    
    busy = true;
    
    // 從事件中獲取輸入數據
    const input = event.data;
    
    // 使用 run_model 函數執行模型並獲取輸出
    const output = await run_model(input);
    
    // 將模型的輸出傳送回主線程
    postMessage(output);
    
    busy = false;
}

// 執行模型的函數，接收輸入並返回模型的輸出
async function run_model(input) {
    // 使用 ONNX Runtime Web 創建推論會話（Inference Session）
    const model = await ort.InferenceSession.create("./best_1.onnx");
    
    // 將輸入轉換為 Tensor 對象
    input = new ort.Tensor(Float32Array.from(input), [1, 3, 640, 640]);
    
    // 使用模型進行推論，返回輸出結果
    const outputs = await model.run({ images: input });
    
    // 返回模型的特定輸出（這裡假設模型的輸出為 "output0"）
    return outputs["output0"].data;
}
