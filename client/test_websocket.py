import asyncio
import websockets
from loguru import logger

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    try:
        logger.info("尝试连接到WebSocket服务器: {}", uri)
        async with websockets.connect(uri) as websocket:
            # 发送测试消息
            test_message = "测试消息，请回复"
            logger.info("发送消息: {}", test_message)
            await websocket.send(test_message)
            
            # 等待并接收响应
            logger.info("等待响应...")
            response = await websocket.recv()
            logger.info("收到响应: {}", response)
            
            # 继续接收更多响应（如果有）
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    logger.info("收到额外响应: {}", response)
            except asyncio.TimeoutError:
                logger.info("没有更多响应")
            except Exception as e:
                logger.error("接收额外响应时出错: {}", e)
                
    except websockets.exceptions.ConnectionClosed as e:
        logger.error("WebSocket连接关闭: {}", e)
    except Exception as e:
        logger.error("发生错误: {}", e)

if __name__ == "__main__":
    logger.info("开始WebSocket测试")
    asyncio.run(test_websocket())
    logger.info("WebSocket测试完成")