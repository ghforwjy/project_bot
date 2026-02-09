/**
 * 测试语音流式识别的Node.js脚本
 * 使用ws库
 * 运行前需要安装ws库: npm install ws
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

// 增加日志输出
console.log('开始测试语音流式识别...');

// WebSocket服务器URL
const url = "ws://localhost:8000/api/v1/voice/stream";
console.log(`WebSocket服务器URL: ${url}`);

// 发送心跳消息，避免连接超时
function sendPing(ws) {
  if (ws.readyState === WebSocket.OPEN) {
    console.log('发送心跳消息');
    ws.ping();
    setTimeout(() => sendPing(ws), 30000);
  }
}

// 创建WebSocket连接
const ws = new WebSocket(url);

// 连接建立
ws.on('open', () => {
  console.log("WebSocket连接已建立");
  
  // 读取测试音频文件
  const wavPath = path.join(__dirname, 'test_audio.wav');
  fs.readFile(wavPath, (err, wavData) => {
    if (err) {
      console.error("读取音频文件失败:", err);
      ws.close();
      return;
    }
    
    console.log(`WAV文件大小: ${wavData.length} bytes`);
    
    // 分块发送音频数据
    const chunkSize = 32000; // 每次发送约1秒的音频数据
    let offset = 0;
    
    const sendChunk = () => {
      if (offset >= wavData.length) {
        // 发送结束信号
        console.log("发送结束信号");
        ws.send(Buffer.from([69, 78, 68])); // 'END' 字符的ASCII码
        return;
      }
      
      const chunk = wavData.slice(offset, offset + chunkSize);
      console.log(`发送音频数据: ${chunk.length} bytes`);
      ws.send(chunk);
      
      offset += chunkSize;
      setTimeout(sendChunk, 200); // 模拟实时录音，添加短暂延迟
    };
    
    // 开始发送音频数据
    sendChunk();
  });
});

// 接收消息
ws.on('message', (message) => {
  try {
    const data = JSON.parse(message);
    if (data.type === "recognition_result") {
      console.log(`识别结果: ${data.text}`);
    } else if (data.type === "error") {
      console.error(`错误: ${data.message}`);
      ws.close();
    }
  } catch (error) {
    console.error("解析消息失败:", error);
  }
});

// 连接关闭
ws.on('close', (code, reason) => {
  console.log(`WebSocket连接已关闭: ${code} ${reason}`);
});

// 连接错误
ws.on('error', (error) => {
  console.error("WebSocket错误:", error);
});
