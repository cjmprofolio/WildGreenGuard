// 選擇上傳檔案的 input 元素
const input = document.getElementById("uploadInput");
// 監聽檔案變動事件
input.addEventListener("change", async (event) => {
    // 呼叫 detect_objects_on_image 函式，獲取偵測到的物體資訊
    const boxes = await detect_objects_on_image(event.target.files[0]);
    // 繪製影像和邊界框
    draw_image_and_boxes(event.target.files[0], boxes);
});

// 繪製影像和邊界框的函式
function draw_image_and_boxes(file, boxes) {
    // 創建圖片物件
    const img = new Image();
    img.src = URL.createObjectURL(file);

    // 圖片載入完成的處理程序
    img.onload = () => {
        // 獲取 canvas 和 context
        const canvas = document.querySelector("canvas");

        // 設定 canvas 的最大寬度和高度
        const maxCanvasWidth = 640;
        const maxCanvasHeight = 640;

        // 計算縮放比例以使圖片在限制範圍內
        const scale = Math.min(maxCanvasWidth / img.width, maxCanvasHeight / img.height);

        // 計算縮放後的寬度和高度
        const drawWidth = img.width * scale;
        const drawHeight = img.height * scale;

        // 設定實際的 canvas 寬度和高度
        canvas.width = drawWidth;
        canvas.height = drawHeight;

        const ctx = canvas.getContext("2d");

        // 在 canvas 上繪製原始圖片，並按比例縮放
        ctx.drawImage(img, 0, 0, drawWidth, drawHeight);

        // 設定邊界框的樣式
        ctx.strokeStyle = "#00FF00";
        ctx.lineWidth = 3;
        ctx.font = "18px serif";

        // 迴圈遍歷邊界框陣列，繪製每個邊界框
        boxes.forEach(([x1, y1, x2, y2, label]) => {
            // 縮放邊界框座標
            x1 *= scale;
            y1 *= scale;
            x2 *= scale;
            y2 *= scale;

            // 繪製邊界框
            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

            // 繪製作為標籤背景的填充矩形
            ctx.fillStyle = "#00ff00";
            const width = ctx.measureText(label).width;
            ctx.fillRect(x1, y1, width + 10, 25);

            // 設定標籤文字的顏色和位置
            ctx.fillStyle = "#000000";
            ctx.fillText(label, x1, y1 + 18);
        });
    };
}

// 在影像上偵測物體的函式
async function detect_objects_on_image(buf) {
    // 準備輸入資料
    const [input, img_width, img_height] = await prepare_input(buf);
    // 執行模型並獲取輸出
    const output = await run_model(input);
    // 處理模型輸出並返回結果
    return process_output(output, img_width, img_height);
}

// 準備模型輸入資料的函式
async function prepare_input(buf) {
    return new Promise(resolve => {
        const img = new Image();
        img.src = URL.createObjectURL(buf);
        img.onload = () => {
            const [img_width, img_height] = [img.width, img.height]
            const canvas = document.createElement("canvas");
            canvas.width = 640;
            canvas.height = 640;
            const context = canvas.getContext("2d");
            context.drawImage(img, 0, 0, 640, 640);
            const imgData = context.getImageData(0, 0, 640, 640);
            const pixels = imgData.data;

            const red = [], green = [], blue = [];
            for (let index = 0; index < pixels.length; index += 4) {
                red.push(pixels[index] / 255.0);
                green.push(pixels[index + 1] / 255.0);
                blue.push(pixels[index + 2] / 255.0);
            }
            const input = [...red, ...green, ...blue];
            resolve([input, img_width, img_height])
        }
    })
}

// 執行模型的函式
async function run_model(input) {
    const model = await ort.InferenceSession.create("best.onnx");
    input = new ort.Tensor(Float32Array.from(input), [1, 3, 640, 640]);
    const outputs = await model.run({ images: input });
    console.log(outputs);
    return outputs["output0"].data;
}

// 處理模型輸出的函式
function process_output(output, img_width, img_height) {
    let boxes = [];
    console.log(boxes);
    for (let index = 0; index < 8400; index++) {
        const [class_id, prob] = [...Array(50).keys()]
            .map(col => [col, output[8400 * (col + 4) + index]])
            .reduce((accum, item) => item[1] > accum[1] ? item : accum, [0, 0]);
        if (prob < 0.1) {
            continue;
        }
        const label = yolo_classes[class_id];
        const xc = output[index];
        const yc = output[8400 + index];
        const w = output[2 * 8400 + index];
        const h = output[3 * 8400 + index];
        const x1 = (xc - w / 2) / 640 * img_width;
        const y1 = (yc - h / 2) / 640 * img_height;
        const x2 = (xc + w / 2) / 640 * img_width;
        const y2 = (yc + h / 2) / 640 * img_height;
        boxes.push([x1, y1, x2, y2, label, prob]);
    }

    // 依概率排序邊界框
    boxes = boxes.sort((box1, box2) => box2[5] - box1[5])
    console.log(boxes);
    const result = [];
    while (boxes.length > 0) {
        result.push(boxes[0]);
        // 過濾掉與當前框 IoU 大於 0.7 的框
        boxes = boxes.filter(box => iou(boxes[0], box) < 0.7);
    }
    console.log(result);
    return result;
}

// 計算 IoU（Intersection-over-Union）的函式
function iou(box1, box2) {
    return intersection(box1, box2) / union(box1, box2);
}

// 計算兩個框的聯集面積的函式
function union(box1, box2) {
    const [box1_x1, box1_y1, box1_x2, box1_y2] = box1;
    const [box2_x1, box2_y1, box2_x2, box2_y2] = box2;
    const box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1)
    const box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1)
    return box1_area + box2_area - intersection(box1, box2)
}

// 計算兩個框的交集面積的函式
function intersection(box1, box2) {
    const [box1_x1, box1_y1, box1_x2, box1_y2] = box1;
    const [box2_x1, box2_y1, box2_x2, box2_y2] = box2;
    const x1 = Math.max(box1_x1, box2_x1);
    const y1 = Math.max(box1_y1, box2_y1);
    const x2 = Math.min(box1_x2, box2_x2);
    const y2 = Math.min(box1_y2, box2_y2);
    return (x2 - x1) * (y2 - y1)
}

// YOLOv8的類別標籤
const yolo_classes = [
    'Ageratum_houstonianum','Ageratum_houstonianum_flower','Ageratum_houstonianum_leaf',
    'Amaranthus_spinosus','Amaranthus_spinosus_flower','Amaranthus_spinosus_leaf',
    'Bidens_pilosa_var_radiata','Bidens_pilosa_var_radiata_flower','Bidens_pilosa_var_radiata_leaf','Bidens_pilosa_var_radiata_seed',
    'Brachiaria_mutica','Brachiaria_mutica_seed',
    'Bryophyllum_pinnatum','Bryophyllum_pinnatum_leaf',
    'Celosia_cristata','Celosia_cristata_flower','Celosia_cristata_leaf',
    'Chloris_barbata','Chloris_barbata_flower',
    'Conyza_species','Conyza_species_flower','Conyza_species_leaf',
    'Crassocephalum_crepidioides','Crassocephalum_crepidioides_flower','Crassocephalum_crepidioides_leaf',
    'Cynodon_dactylon',
    'Eleusine_indica','Eleusine_indica_flower',
    'Lantana_camara','Lantana_camara_flower','Lantana_camara_leaf',
    'Leucaena_leucocephala','Leucaena_leucocephala_flower','Leucaena_leucocephala_leaf','Leucaena_leucocephala_seed',
    'Megathyrsus_maximus','Megathyrsus_maximus_seed',
    'Mikania_micrantha','Mikania_micrantha_flower','Mikania_micrantha_leaf',
    'Pennisetum_purpureum','Pennisetum_purpureum_flower',
    'Rhynchelytrum_repens','Rhynchelytrum_repens_flower',
    'Silvergrass','Silvergrass_flower',
    'Syngonium_podophyllum',
    'Tithonia_diversifolia','Tithonia_diversifolia_flower','Tithonia_diversifolia_leaf'
    ]
