import os
import asyncio
import os
import aioconsole

class TextToSpeech:

    def __init__(self):
        self.current_process = None

    async def speak(self, text, role="Milena"):
        """Asynchronous function to speak text."""
        self.current_process = await asyncio.create_subprocess_shell(
            f"say -v {role} '{text}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await self.current_process.communicate()
            if stderr:
                print(f"Error: {stderr.decode().strip()}")
        except asyncio.CancelledError:
            if self.current_process:
                self.current_process.terminate()
                await self.current_process.wait()
            raise
        finally:
            self.current_process = None

    async def stop_speaking(self):
        """Asynchronous function to stop current speaking."""
        if self.current_process:
            print("Stopping current speaking...")
            self.current_process.terminate()
            await self.current_process.wait()
            self.current_process = None
            print("Stopped.")

    async def listener(self, task_queue, stop_event):
        """Asynchronous listener function waiting for speaking tasks."""
        while not stop_event.is_set():
            try:
                text, role = await asyncio.wait_for(task_queue.get(), timeout=1)
                print(f"Starting to speak: '{text}' with role: {role}")
                await self.speak(text, role)
                print(f"Finished speaking: '{text}'")
                task_queue.task_done()
            except asyncio.TimeoutError:
                continue

def prepare_text(text):
    escaped_text = text.replace('"', '\\"')
    return escaped_text

def say(text):
    text = prepare_text(text)
    command = f'nohup say -v Milena "{text}" > /dev/null 2>&1 &'
    os.system(command)

def do_tts(text):
    say(text)

def interrupt_tts():
    os.system('killall say')

async def main():

    tts = TextToSpeech()
    task_queue = asyncio.Queue(maxsize=10)
    stop_event = asyncio.Event()

    listener_task = asyncio.create_task(tts.listener(task_queue, stop_event))

    try:
        while True:
            command = await aioconsole.ainput("Enter command (speak/stop/exit): ")
            if command == "speak":
                role = None
                text = await aioconsole.ainput("Enter text to speak: ")
                # role = await aioconsole.ainput("Enter role (voice): ")
                await task_queue.put((text, role))
            elif command == "stop":
                await tts.stop_speaking()
            elif command == "exit":
                stop_event.set()
                break
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        await listener_task
        await asyncio.gather(listener_task)

# # Ensure proper event loop handling on Windows
# if __name__ == "__main__":
#     if os.name == 'nt':  # For Windows
#         asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
#     asyncio.run(main())