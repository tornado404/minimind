import asyncio
import re  # 用于正则匹配标点符号
import websockets  # 使用 websockets 库连接 WebSocket 服务
from loguru import logger

async def tts_client():
    uri = "ws://localhost:8000/ws"  # 连接第一个服务的 WebSocket 地址
    try:
        async with websockets.connect(uri) as websocket:
            prompt = "你好，有人在家吗。"  # 根据需求设置发送的文本
            await websocket.send(prompt)  # 发送文本到第一个服务
            logger.info("已发送消息: {}", prompt)  # 记录发送的消息

            buffer = ""  # 用于存储接收到的文本片段，便于重组完整句子
            pattern = r'([,，。！？])'  # 定义中文句子结束标点

            # 无限循环接收流式响应的文本片段
            while True:
                message = await websocket.recv()  # 接收文本片段
                logger.info("接收到文本片段: {}", message)  # 打印收到的文本片段
                
                # 跳过特殊标记，如<think>和</think>
                if message.startswith('<') and message.endswith('>'):
                    logger.info("跳过特殊标记: {}", message)
                    continue
                    
                buffer += message  # 将收到的文本追加到缓冲区

                # 使用正则表达式将 buffer 按标点进行分割
                parts = re.split(pattern, buffer)
                # parts 结果示例：['部分文本', '。', '下一部分文本', '！', '剩余未完整句子']
                complete_sentences = []  # 用于存放完整的句子
                new_buffer = ""  # 用于存放未完整的文本片段

                # 每两个元素拼接一次：文本 + 标点 为一完整句子
                for i in range(0, len(parts)-1, 2):
                    if i+1 < len(parts):
                        sentence = parts[i] + parts[i+1]  # 拼接文本与标点
                        complete_sentences.append(sentence)
                # 如果最后一部分不是完整句子，则保留到新的 buffer 中
                if len(parts) % 2 == 1:
                    new_buffer = parts[-1]
                # 对每个完整句子进行打印，同时可在此处调用 TTS 转语音函数
                for sentence in complete_sentences:
                    logger.info("完整句子: {}", sentence)
                    # 在这里可以调用 TTS 转语音函数，例如：
                    # tts = gTTS(text=sentence, lang='zh')  # 使用 gTTS 将文本转换为语音
                    # tts.save("output.mp3")  # 保存音频文件
                    # os.system("mpg123 output.mp3")  # 播放音频文件
                buffer = new_buffer  # 更新 buffer 为未完整的部分

    except websockets.exceptions.ConnectionClosed:
        logger.warning("与服务1的连接已关闭")  # 连接关闭时记录警告日志
    except Exception as e:
        logger.error("发生错误: {}", e)  # 记录其他异常错误

if __name__ == "__main__":
    asyncio.run(tts_client())  # 运行异步客户端
