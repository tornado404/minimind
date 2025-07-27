from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import httpx
import json

from starlette.websockets import WebSocketDisconnect

model_name = "Qwen/Qwen2.5-3B-Instruct"
model_name = "Qwen/Qwen2.5-0.5B-Instruct"
model_name = "deepseek-r1:1.5b"
# model_name = "llama3.1:8b"
app = FastAPI()

# 简单的聊天界面HTML
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Ollama Chat</title>
    </head>
    <body>
        <h1>Ollama流式聊天（支持上下文）</h1>
        <div id="chat" style="height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;"></div>
        <input type="text" id="message" placeholder="输入消息..." style="width: 80%;" />
        <button onclick="sendMessage()">发送</button>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            const chatDiv = document.getElementById('chat');
            
            ws.onmessage = function(event) {
                const message = document.createElement('div');
                message.textContent = 'AI: ' + event.data;
                chatDiv.appendChild(message);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            };

            function sendMessage() {
                const input = document.getElementById('message');
                const message = input.value;
                if (message) {
                    const messageDiv = document.createElement('div');
                    messageDiv.textContent = '你: ' + message;
                    chatDiv.appendChild(messageDiv);
                    ws.send(message);
                    input.value = '';
                }
            }
            
            document.getElementById('message').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    context = None  # 存储对话上下文

    try:
        while True:
            # 接收用户消息
            user_message = await websocket.receive_text()

            # 构造Ollama API请求
            request_data = {
                "model": model_name,       # 改为你的模型名称
                "prompt": user_message,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 128
                }
            }

            if context:
                request_data["context"] = context

            # 使用异步客户端连接Ollama
            async with httpx.AsyncClient(timeout=60) as client:
                try:
                    async with client.stream(
                            "POST",
                            "http://localhost:11434/api/generate",
                            json=request_data
                    ) as ollama_stream:
                        full_response = ""
                        async for chunk in ollama_stream.aiter_lines():
                            chunk = chunk.strip()
                            if not chunk:
                                continue

                            try:
                                data = json.loads(chunk)
                            except json.JSONDecodeError:
                                continue

                            # 处理流式响应
                            if "response" in data:
                                await websocket.send_text(data["response"])
                                full_response += data["response"]

                            # 更新上下文
                            if "context" in data:
                                context = data["context"]

                            # 结束标志
                            if data.get("done", False):
                                break

                except httpx.ConnectError:
                    await websocket.send_text("[系统] 无法连接到Ollama服务")
                except Exception as e:
                    await websocket.send_text(f"[系统] 发生错误: {str(e)}")

    except WebSocketDisconnect:
        print("客户端断开连接")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)