/**
 * Copyright FunASR (https://github.com/alibaba-damo-academy/FunASR). All Rights
 * Reserved. MIT License  (https://opensource.org/licenses/MIT)
 */
/* 2022-2023 by zhaoming,mali aihealthx.com */


// 连接; 定义socket连接类对象与语音对象
var wsconnecter = new WebSocketConnectMethod({msgHandle:getJsonMessage,stateHandle:getConnState});
var audioBlob;
var sampleBuf=new Int16Array();
var rec_text="";  // for online rec asr result
var isfilemode=false;  // if it is in file mode
var file_ext="";
var file_sample_rate=16000; //for wav file sample rate
var file_data_array;  // array to save file data
var totalsend=0;
var	isRec = false;
var sendBuf = ''
// 录音; 定义录音对象,wav格式
var rec = Recorder({
	type:"pcm",
	bitRate:16,
	sampleRate:16000,
	onProcess:recProcess
});

function start_file_send(){
	sampleBuf=new Uint8Array( file_data_array );
	var chunk_size=960; // for asr chunk_size [5, 10, 5]
	while(sampleBuf.length>=chunk_size){
		
		sendBuf=sampleBuf.slice(0,chunk_size);
		totalsend=totalsend+sampleBuf.length;
		sampleBuf=sampleBuf.slice(chunk_size,sampleBuf.length);
		wsconnecter.wsSend(sendBuf);
	}
	stop();
}
 
// 语音识别结果; 对jsonMsg数据解析,将识别结果附加到编辑框中
function getJsonMessage( jsonMsg ) {
	//console.log(jsonMsg);
	console.log( "message: " + JSON.parse(jsonMsg.data)['text'] );
	var rectxt=""+JSON.parse(jsonMsg.data)['text'];
	var asrmodel=JSON.parse(jsonMsg.data)['mode'];
	if(asrmodel=="2pass"){
		rec_text=rec_text+rectxt; //.replace(/ +/g,"");
	}
	console.log( "rec_text: " + rec_text);
}

// 连接状态响应
function getConnState( connState ) {
	if ( connState === 0 ) { //on open
		console.log('连接成功!请点击开始')
	} else if ( connState === 1 ) {
		//stop();
	} else if ( connState === 2 ) {
		stop();
		console.log("连接地址失败,请检查asr地址和端口。或试试界面上手动授权，再连接。");
	}
}

function record(){
	rec.open( function(){
		rec.start();
		console.log("开始");
	});
}

 

// 识别启动、停止、清空操作
function start() {
	
	// 清除显示
	clear();
	//启动连接
	var ret=wsconnecter.wsStart();
	// 1 is ok, 0 is error
	if(ret==1){
		console.log("正在连接asr服务器，请等待...")
		isRec = true;
        return 1;
	}else{
 		console.log("请点击开始...")
		return 0;
	}
}

 
function stop() {
	var chunk_size = new Array( 5, 10, 5 );
	var request = {
		"chunk_size": chunk_size,
		"wav_name":  "h5",
		"is_speaking":  false,
		"chunk_interval":10,
		"mode":'2pass',
	};
	console.log(request);
	if(sampleBuf.length>0){
	wsconnecter.wsSend(sampleBuf);
	console.log("sampleBuf.length"+sampleBuf.length);
	sampleBuf=new Int16Array();
	}
	wsconnecter.wsSend( JSON.stringify(request) );
	// 控件状态更新
	isRec = false;
    console.log("发送完数据,请等候,正在识别...");
}

function clear() {
    rec_text="";
}

 
function recProcess( buffer, powerLevel, bufferDuration, bufferSampleRate,newBufferIdx,asyncEnd ) {
	if ( isRec === true ) {
		var data_48k = buffer[buffer.length-1];  
 
		var  array_48k = new Array(data_48k);
		var data_16k=Recorder.SampleData(array_48k,bufferSampleRate,16000).data;
 
		sampleBuf = Int16Array.from([...sampleBuf, ...data_16k]);
		var chunk_size=960; // for asr chunk_size [5, 10, 5]
		console.log(""+bufferDuration/1000+"s");
		while(sampleBuf.length>=chunk_size){
		    sendBuf=sampleBuf.slice(0,chunk_size);
			sampleBuf=sampleBuf.slice(chunk_size,sampleBuf.length);
			wsconnecter.wsSend(sendBuf);
			
			
		 
		}
		
 
		
	}
}
