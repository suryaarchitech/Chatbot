import json
import os
from langchain_openai import ChatOpenAI # type: ignore
from langchain_core.prompts import ChatPromptTemplate # type: ignore
from langchain_core.output_parsers import StrOutputParser # type: ignore
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from langchain.memory import ConversationBufferMemory # type:ignore
from channels.layers import get_channel_layer # type:ignore
from dotenv import load_dotenv # type:ignore

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY



llm = ChatOpenAI(model="gpt-4")
output_parser = StrOutputParser()
memory = ConversationBufferMemory(memory_key="history")

class ChatConsumer(AsyncWebsocketConsumer):
    """Chat Consumer for handling WebSocket connections"""
    
    async def connect(self):
        """Handle new WebSocket connection"""
        self.room_name = "chat"
        self.room_group_name = "chat"
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        pass

    async def receive(self, text_data):
        """Handle messages from the WebSocket"""
        query = text_data
        print(f"Server received: {query}")

        if query.lower() == 'quit':
            await self.send(text_data=json.dumps({
                "message": "Goodbye!"
            }))
            await self.close()
            return

       
        memory.save_context({"input": query}, {"output": ""})  

        conversation_context = memory.load_memory_variables({})
        print(f"Conversation context from memory: {conversation_context}")


        prompt_with_context = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Please respond to the user's queries."),
            ("user", f"Question:{query}\n\n{conversation_context.get('history', '')}")
        ])

        chain = prompt_with_context | llm | output_parser
        response = chain.invoke({'question': query})
        print(f"Response generated: {response}")
        
        memory.save_context({"input": query}, {"output": response})

        await self.send(text_data=json.dumps({
            "message": response
        }))

    async def chat_message(self, event):
        """Handles the messages received from the channel layer"""
        message = event['message']
        print(f"Received message from channel layer: {message}")

        await self.send(text_data=json.dumps({
            "message": message
        }))














# class ChatConsumer(AsyncWebsocketConsumer):
#     """Chat Consumer for handling WebSocket connections"""
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Initialize a list to store the conversation history
#         self.conversation_history = []

#     async def connect(self):
#         """Handle new WebSocket connection"""
#         self.room_name = "chat"
#         self.room_group_name = "chat"
#         await self.accept()

#     async def disconnect(self, close_code):
#         """Handle WebSocket disconnection"""
#         pass

#     async def receive(self, text_data):
#         """Handle messages from the WebSocket"""
#         query = text_data
#         print(f"Server received: {query}")

#         # If the user wants to quit, close the connection
#         if query.lower() == 'quit':
#             await self.send(text_data=json.dumps({
#                 "message": "Goodbye!"
#             }))
#             await self.close()
#             return

#         # Add the current query to the conversation history
#         self.conversation_history.append({'user': query})

#         # Build the full conversation context
#         conversation_context = ""
#         for message in self.conversation_history:
#             conversation_context += f"User: {message['user']}\n"
#             if 'bot' in message:
#                 conversation_context += f"Bot: {message['bot']}\n"

#         # Update the prompt to include the full conversation history
#         prompt_with_context = ChatPromptTemplate.from_messages([
#             ("system", "You are a helpful assistant. Please respond to the user's queries."),
#             ("user", f"Question:{query}\n\n{conversation_context}")
#         ])

#         # Use Langchain to get a response from the model
#         try:
#             print("Generating response using Langchain...")
#             chain = prompt_with_context | llm | output_parser
#             response = chain.invoke({'question': query})
#             print(f"Response generated: {response}")
#         except Exception as e:
#             response = f"Error: {str(e)}"
#             print(f"Error while generating response: {response}")

#         # Store the response in the conversation history
#         self.conversation_history[-1]['bot'] = response

#         # Print the current conversation history
#         print(f"Conversation History: {self.conversation_history}")

#         # Send the response to the WebSocket client
#         await self.send(text_data=json.dumps({
#             "message": response
#         }))

#         # --- Store conversation history in InMemoryChannelLayer ---
#         # Get the channel layer instance
#         channel_layer = get_channel_layer()

#         # Here, we'll store the conversation history in the channel layer for this room.
#         # Use the `group_send` to send the full history.
#         await channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': json.dumps(self.conversation_history)  # Store the full history
#             }
#         )

#     async def chat_message(self, event):
#         """Handles the messages received from the channel layer"""
#         message = event['message']
#         print(f"Received message from channel layer: {message}")

#         # Send the received message to the WebSocket
#         await self.send(text_data=json.dumps({
#             "message": message
#         }))