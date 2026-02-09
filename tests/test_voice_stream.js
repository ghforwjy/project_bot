/**
 * 测试语音流式识别的JavaScript脚本
 * 在浏览器中运行
 */

// WebSocket服务器URL
const url = "ws://localhost:8000/api/v1/voice/stream";

// 创建WebSocket连接
const ws = new WebSocket(url);

// 连接建立
ws.onopen = () => {
  console.log("WebSocket连接已建立");
  
  // 读取测试音频文件
  fetch("tests/test_audio.wav")
    .then(response => response.arrayBuffer())
    .then(arrayBuffer => {
      const wavData = new Uint8Array(arrayBuffer);
      console.log(`WAV文件大小: ${wavData.length} bytes`);
      
      // 分块发送音频数据
      const chunkSize = 32000; // 每次发送约1秒的音频数据
      let offset = 0;
      
      const sendChunk = () => {
        if (offset >= wavData.length) {
          // 发送结束信号
          console.log("发送结束信号");
          ws.send(new Uint8Array([69, 78, 68])); // 'END' 字符的ASCII码
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
    })
    .catch(error => {
      console.error("读取音频文件失败:", error);
      ws.close();
    });
};

// 接收消息
ws.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    if (data.type === "recognition_result") {
      console.log(`识别结果: ${data.text}`);
    } else if (data.type === "error") {
      console.error(`错误: ${data.message}`);
      ws.close();
    }
  } catch (error) {
    console.error("解析消息失败:", error);
  }
};

// 连接关闭
ws.onclose = (event) => {
  console.log(`WebSocket连接已关闭: ${event.code} ${event.reason}`);
};

// 连接错误
ws.onerror = (error) => {
  console.error("WebSocket错误:", error);
};
