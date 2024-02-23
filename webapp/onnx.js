// 獲取video元素
const video = document.querySelector("video");

// 選擇使用前置或後置鏡頭，可以是"user"（前置）或"environment"（後置）
const constraints = {
    video: { facingMode: "environment" } // 使用後置鏡頭
};

// 啟動媒體設備，獲取影片流
if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia(constraints)
        .then(function (stream) {
    video.srcObject = stream;
        })
    .catch(function (error) {
    console.log("發生錯誤：" + error.message);
    });
}

// 創建Web Worker實例，載入worker.js文件
const worker = new Worker("worker.js");
let boxes = [];
let interval;

// 當影片播放時的事件監聽器
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
    }, 5);
});

// 當Worker返回結果時的處理
worker.onmessage = (event) => {
    const output = event.data;
    const canvas = document.querySelector("canvas");
    boxes = process_output(output, canvas.width, canvas.height);
};

// 當影片暫停時清除定時器
video.addEventListener("pause", () => {
    clearInterval(interval);
});

// 播放和暫停按鈕的事件監聽器
const playBtn = document.getElementById("play");
const pauseBtn = document.getElementById("pause");
playBtn.addEventListener("click", () => {
    video.play();
});
pauseBtn.addEventListener("click", () => {
    video.pause();
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

 // 自訂標籤
const custom_labels = [
    '紫花藿香薊','紫花藿香薊_花','紫花藿香薊_葉',
    '刺莧','刺莧_花','刺莧_葉',
    '大花咸豐草','大花咸豐草_花','大花咸豐草_葉','大花咸豐草_種子',
    '巴拉草','巴拉草_種子',
    '落地生根','落地生根_葉',
    '雞冠花','雞冠花_花', '雞冠花_葉',
    '孟仁草', '孟仁草_花',
    '假蓬草', '假蓬草_花', '假蓬草_葉',
    '昭和草','昭和草_花', '昭和草_葉',
    '狗牙根',
    '牛筋草', '牛筋草_花',
    '馬纓丹','馬纓丹_花','馬纓丹_葉',
    '銀合歡','銀合歡_花','銀合歡_葉','銀合歡_種子',
    '大黍','大黍_種子',
    '小花蔓澤蘭', '小花蔓澤蘭_花','小花蔓澤蘭_葉',
    '象草','象草_花',  
    '紅毛草','紅毛草_花',
    '芒草', '芒草_花',
    '合果芋',
    '王爺葵','王爺葵_花', '王爺葵_葉',
];

const yolo_classes = custom_labels;
