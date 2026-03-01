// questions.jsが正しく読み込まれているか確認
if (typeof questions === 'undefined') {
    alert('問題データ(questions.js)が読み込まれていません。\nHTMLファイルで、quizApp.jsよりも先にquestions.jsを読み込んでいるか確認してください。');
    throw new Error("questions array is not defined. Make sure questions.js is loaded before this script.");
}

let index = 0;
let C_AnsCnt = 0; //correct answer count
const amount = document.getElementById('amount');
let MaxNum = parseInt(amount.value, 10);

const qElem = document.getElementById('question');
const resElem = document.getElementById('result');
const TranslatedElem = document.getElementById('Translated');
const trueBtn = document.getElementById('trueBtn');
const falseBtn = document.getElementById('falseBtn');
const qNumElem = document.getElementById('qnum');
const startBtnArea = document.getElementById('start_btn_group');
const startBtn = document.getElementById('start_btn');
const backBtnArea = document.getElementById('backBtn_group');
const backBtn = document.getElementById('backBtn');
const selectBtnArea = document.getElementById('button-group');
const intro = document.getElementById('intro');
const nextBtnArea = document.getElementById('next_btn_group');
const nextBtn = document.getElementById('next_btn');
const quitBtnArea = document.getElementById('quit_btn_group');
const quitBtn = document.getElementById('quit_btn');
const img = document.querySelector('#image img');
const exp_Translated = document.getElementById('exp_Translated');
const exp = document.getElementById('exp');
let Sequence = [];

function shuffle_Num(num) {
    const arr = Array.from({ length: num }, (_, i) => i);
    for(let i = arr.length-1;i>0;i--){
        let j = Math.floor(Math.random()*(i+1));
        [arr[i],arr[j]] = [arr[j],arr[i]];
    }
    return arr;
}

function start(){
    // 問題数を取得し、数値に変換
    MaxNum = parseInt(amount.value, 10);
    // 選択された問題数が、実際に利用可能な問題数を超えている場合は全問題数に設定
    if (MaxNum > questions.length) {
        MaxNum = questions.length;
    }

    qElem.style.display = 'block';
    TranslatedElem.style.display = 'block';
    startBtnArea.style.display = "none";
    selectBtnArea.style.display = "flex";
    quitBtnArea.style.display = "block"; // 中止ボタンを表示
    intro.style.display = 'none'; 
    // 全問題のインデックスをシャッフルし、選択された数だけ取得
    Sequence = shuffle_Num(questions.length).slice(0, MaxNum);
    console.log(Sequence);
    
    showQuestion();
}

function showQuestion() {
    let q = questions[Sequence[index]];

    // idが数字型ではない、または91以上の場合はスキップ
    if (typeof q.id !== 'number' || q.id >= 91) {
        nextQuestion();
        return;
    }

    resElem.style.display = 'none';
    exp_Translated.style.display = 'none';
    exp.style.display = 'none';
    trueBtn.disabled = false;
    falseBtn.disabled = false;
    qElem.textContent = q.state;
    TranslatedElem.textContent = q.state_Translated;
    qNumElem.textContent = index + 1 + "/" + MaxNum;
    if(q.image && !Number.isNaN(q.image)){
        img.src = q.image;
        img.style.display = '';
    }else{
        img.src = '';
        img.style.display = 'none';
    }
}

function checkAnswer(userAns) {
    nextBtnArea.style.display = 'block';
    trueBtn.disabled = true;
    falseBtn.disabled = true;

    if(questions[Sequence[index]].exp_Translated){
        exp_Translated.style.display = 'block';
        exp.style.display = 'block';
        exp_Translated.textContent =  questions[Sequence[index]].exp_Translated;
        exp.textContent = questions[Sequence[index]].exp;
    }

    let correct = (questions[Sequence[index]].answer === '○') === userAns;
    selectBtnArea.style.display = 'none';

    resElem.style.display = 'block';
    resElem.textContent = correct ? "Correct!" : "Incorrect...";
    resElem.className = correct ? "correct" : "incorrect";
    C_AnsCnt += correct ? 1:0;
}

function nextQuestion(){
    index++;
    nextBtnArea.style.display = 'none';

    if (index < MaxNum) {
        selectBtnArea.style.display = 'flex';
        showQuestion();
    } else {
        qElem.textContent = "You've done all questions!";
        TranslatedElem.textContent = "คุณตอบคำถามทั้งหมดแล้ว!";
        resElem.textContent = "Score : " + C_AnsCnt + "/" + MaxNum;
        selectBtnArea.style.display = 'none';
        quitBtnArea.style.display = 'none'; // クイズ終了時は中止ボタンを隠す
        backBtnArea.style.display = 'block';
    }
}

// トップ画面に戻る処理を関数化
function resetToTitle() {
    backBtnArea.style.display = 'none';
    startBtnArea.style.display = 'block';
    selectBtnArea.style.display = 'none';
    nextBtnArea.style.display = 'none';
    quitBtnArea.style.display = 'none';

    qElem.style.display = 'none';
    TranslatedElem.style.display = 'none';
    resElem.style.display = 'none';
    resElem.textContent = '';
    
    intro.style.display = 'block';
    img.style.display = 'none';
    exp_Translated.style.display = 'none';
    exp.style.display = 'none';
    qNumElem.textContent = '';

    index = 0;
    C_AnsCnt = 0;
}

// イベントリスナー
startBtn.addEventListener('click', start);
trueBtn.addEventListener('click', () => checkAnswer(true));
falseBtn.addEventListener('click', () => checkAnswer(false));
nextBtn.addEventListener('click', nextQuestion);
quitBtn.addEventListener('click', () => {
    if(confirm("Are you sure you want to quit? \n本当に終了しますか？")){
        resetToTitle();
    }
});
amount.addEventListener('change', () => {
  // ユーザーが問題数を変更したことをコンソールにログ出力（デバッグ用）
  console.log('選択値が変更されました:', amount.value);
});
backBtn.addEventListener('click', resetToTitle);