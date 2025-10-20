from agent.llm_manager import LLMManager
from tools.calendar_tools import CalendarTools
from agent.memory import Memory
from tools.tts_manager import tts  # Import the global TTS instance
import readline  # For better input handling on Unix systems

class TEDCLI:
    def __init__(self):
        self.llm = LLMManager()
        self.calendar = CalendarTools()
        self.memory = Memory()
        self.tts_enabled = True
        
        print("🤖 TED 2.0 MVP - Local LLM + Voice")
        print("Commands: 'voice' to toggle TTS, 'quit' to exit")
        print("🔊 Voice: ON\n")
    
    def process_command(self, command: str) -> str:
        # Handle special commands
        if command.lower() in ['voice', 'tts', 'speak']:
            self.tts_enabled = tts.toggle()
            return f"Voice feedback {'enabled' if self.tts_enabled else 'disabled'}."
        
        if command.lower() in ['quiet', 'mute']:
            self.tts_enabled = False
            tts.stop()
            return "Voice feedback muted."
        
        # Get recent context
        recent_chats = self.memory.get_recent_conversations()
        context = "Recent conversations:\n" + "\n".join(
            [f"User: {chat['user']}\nTED: {chat['ai']}" for chat in recent_chats]
        )
        
        # Get calendar context
        try:
            events = self.calendar.get_events(3)
            events_text = "\n".join([
                f"- {event['summary']} ({event['start'].get('dateTime', event['start'].get('date'))})"
                for event in events
            ])
            context += f"\n\nUpcoming events:\n{events_text}"
        except Exception as e:
            context += f"\n\nCalendar access issue: {str(e)}"
        
        # Get LLM response
        response = self.llm.generate_response(command, context)
        
        # Trigger TTS if enabled
        if self.tts_enabled:
            tts.speak(response)
        
        # Save to memory
        self.memory.save_conversation(command, response)
        
        return response
    
    def run(self):
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    tts.speak("Goodbye!")
                    print("TED: Goodbye! 👋")
                    break
                
                if user_input:
                    response = self.process_command(user_input)
                    print(f"TED: {response}\n")
            
            except KeyboardInterrupt:
                print("\nTED: Session ended.")
                break
            except Exception as e:
                print(f"TED: Error - {str(e)}\n")

if __name__ == "__main__":
    cli = TEDCLI()
    cli.run()
