import asyncio
import websockets

async def chat():
    uri = "ws://localhost:8000/ws/chat/"
    async with websockets.connect(uri) as websocket:
        while True:
            query = input("You: ")
            await websocket.send(query)

            response = await websocket.recv()
            print(f"Bot: {response}")

            if query.lower() == "quit":
                print("Exiting chat...")
                break

asyncio.run(chat())
