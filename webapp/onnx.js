const video = document.querySelector("video");

// 選擇使用前置或後置鏡頭，可以是"user"（前置）或"environment"（後置）
const constraints = {
    video: { facingMode: "environment" } // 使用後置鏡頭
};

if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia(constraints)
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (error) {
            console.log("發生錯誤：" + error.message);
        });
}

const worker = new Worker("worker.js");
let boxes = [];
let interval;

video.addEventListener("play", () => {
    const canvas = document.querySelector("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");

    // 定期執行的定時器
    interval = setInterval(() => {
        context.drawImage(video, 0, 0);
        draw_boxes(canvas, boxes);
        const input = prepare_input(canvas);
        worker.postMessage(input);
    }, 30);
});

// 當 worker 返回結果時的處理
worker.onmessage = (event) => {
    const output = event.data;
    const canvas = document.querySelector("canvas");
    boxes = process_output(output, canvas.width, canvas.height);
};


// 當影片停止時清除定時器
video.addEventListener("stop", () => {
    clearInterval(interval);
});

// 開始和停止按鈕的事件監聽器
const playBtn = document.getElementById("play");
const stopBtn = document.getElementById("stop");
playBtn.addEventListener("click", () => {
    video.play();
});
stopBtn.addEventListener("click", () => {
    video.stop();
});

// 將圖像準備為神經網絡輸入的函數
function prepare_input(img) {
    const canvas = document.createElement("canvas");
    canvas.width = 640;
    canvas.height = 640;
    const context = canvas.getContext("2d");
    context.drawImage(img, 0, 0, 640, 640);
    
    // 取得圖像數據
    const data = context.getImageData(0, 0, 640, 640).data;
    const red = [], green = [], blue = [];
    
    // 正規化像素值
    for (let index = 0; index < data.length; index += 4) {
        red.push(data[index] / 255);
        green.push(data[index + 1] / 255);
        blue.push(data[index + 2] / 255);
    }

    return [...red, ...green, ...blue];
}

// 處理神經網絡輸出的函數
function process_output(output, img_width, img_height) {
    let boxes = [];
    for (let index = 0; index < 8400; index++) {
        const [class_id, prob] = [...Array(50).keys()]
            .map(col => [col, output[8400 * (col + 4) + index]])
            .reduce((accum, item) => item[1] > accum[1] ? item : accum, [0, 0]);

        // 如果概率低於閾值，跳過
        if (prob < 0.5) {
            continue;
        }

        const label = yolo_classes[class_id];
        const xc = output[index];
        const yc = output[8400 + index];
        const w = output[2 * 8400 + index];
        const h = output[3 * 8400 + index];

        // 計算邊界框座標
        const x1 = (xc - w / 2) / 640 * img_width;
        const y1 = (yc - h / 2) / 640 * img_height;
        const x2 = (xc + w / 2) / 640 * img_width;
        const y2 = (yc + h / 2) / 640 * img_height;

        boxes.push([x1, y1, x2, y2, label, prob]);
    }

    // 根據概率排序邊界框
    boxes = boxes.sort((box1, box2) => box2[5] - box1[5])

    // 過濾重疊的邊界框
    const result = [];
    while (boxes.length > 0) {
        result.push(boxes[0]);
        boxes = boxes.filter(box => iou(boxes[0], box) < 0.7 || boxes[0][4] !== box[4]);
    }

    return result;
}

// 計算交集-聯集比率的函數
function iou(box1, box2) {
    return intersection(box1, box2) / union(box1, box2);
}

// 計算兩個框的聯集區域的函數
function union(box1, box2) {
    const [box1_x1, box1_y1, box1_x2, box1_y2] = box1;
    const [box2_x1, box2_y1, box2_x2, box2_y2] = box2;
    const box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1)
    const box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1)
    return box1_area + box2_area - intersection(box1, box2)
}

// 計算兩個框的交集區域的函數
function intersection(box1, box2) {
    const [box1_x1, box1_y1, box1_x2, box1_y2] = box1;
    const [box2_x1, box2_y1, box2_x2, box2_y2] = box2;
    const x1 = Math.max(box1_x1, box2_x1);
    const y1 = Math.max(box1_y1, box2_y1);
    const x2 = Math.min(box1_x2, box2_x2);
    const y2 = Math.min(box1_y2, box2_y2);
    return (x2 - x1) * (y2 - y1)
}

// 繪製邊界框的函數
function draw_boxes(canvas, boxes) {
    const ctx = canvas.getContext("2d");
    ctx.strokeStyle = "#00FF00";
    ctx.lineWidth = 3;
    ctx.font = "18px serif";
    boxes.forEach(([x1, y1, x2, y2, label]) => {
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        ctx.fillStyle = "#00ff00";
        const width = ctx.measureText(label).width;
        ctx.fillRect(x1, y1, width + 10, 25);
        ctx.fillStyle = "#000000";
        ctx.fillText(label, x1, y1 + 18);
    });
}

const yolo_classes = [
    'Ageratum_houstonianum','Ageratum_houstonianum_flower','Ageratum_houstonianum_leaf',
    'Amaranthus_spinosus','Amaranthus_spinosus_flower','Amaranthus_spinosus_leaf','Bidens_pilosa_var',
    'Bidens_pilosa_var._radiata','Bidens_pilosa_var_radiata_flower','Bidens_pilosa_var_radiata_leaf','Bidens_pilosa_var_radiata_seed',
    'Brachiaria_mutica','Brachiaria_mutica_seed','Bryophyllum_pinnatum','Bryophyllum_pinnatum_leaf',
    'Celosia_cristata','Celosia_cristata_flower','Celosia_cristata_leaf',
    'Chloris_barbata','Chloris_barbata_flower',
    'Conyza_species','Conyza_species_flower','Conyza_species_leaf',
    'Crassocephalum_crepidioides','Crassocephalum_crepidioides_flower','Crassocephalum_crepidioides_leaf',
    'Cynodon_dactylon',
    'Eleusine_indica','Eleusine_indica_flower',
    'Lantana_camara','Lantana_camara_flower','Lantana_camara_leaf',
    'Leucaena_leucocephala','Leucaena_leucocephala_flower','Leucaena_leucocephala_leaf','Leucaena_leucocephala_seed',
    'Megathyrsus_maximus','Megathyrsus_maximus_seed',
    'Mikania_micrantha','Mikania_micrantha_flower',
    'Pennisetum_purpureum','Pennisetum_purpureum_flower',
    'Rhynchelytrum_repens','Rhynchelytrum_repens_flower',
    'Silvergrass','Silvergrass_flower','Syngonium_podophyllum',
    'Tithonia_diversifolia','Tithonia_diversifolia_flower','Tithonia_diversifolia_leaf'
    
  ];