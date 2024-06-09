

def passive_agent_thread(recorder, llm_client, wav_file, current_audio_file):
   

                    # ii = 0
                    # while True:
    
                    #     current_answer = None
                    #     transcription = None
                    #     while True:
                    #         time.sleep(1)

                    #         pcm = recorder.read()
                    #         result = porcupine.process(pcm)
                    #         wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))
                            
                    #         transcription = transcribe_audio_file(llm_client, current_audio_file)
                    #         if current_answer is None:
                    #             current_answer = transcription
                    #         print(ii, current_answer, transcription)
                    #         ii += 1
                    #         if transcription == current_answer:
                    #             print('Transcription is the same:', transcription)
                    #             passive_agent(llm_client, 
                    #                         current_audio_file, 
                    #                         st_memory=dialog_history,
                    #                         current_transcript=transcription)
                    #             if wav_file is not None:
                    #                 wav_file.close()
                    #             os.unlink(current_audio_file)
                    #             wav_file = get_wav_file(current_audio_file)
                    #             break
                    #         current_answer = transcription
                            
                    #     if not transcription:
                    #         print('No transcription')
                    #         break


#     except KeyboardInterrupt:
#         print('Stopping ...')
#     finally:
#         recorder.delete()
#         porcupine.delete()
#         if wav_file is not None:
#             wav_file.close()

