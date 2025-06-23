define ai = Character("LING", color="#c8ffc8")
define config.gl2 = True
init python:
    import os
    import subprocess
    import json
    import random
    def MyLive2D(*args, fallback="placeholder_image", **kwargs):
        if renpy.has_live2d():
            return Live2D(*args, **kwargs)
        else:
            return fallback
    # 语音识别状态
    is_listening = False
    recognition_result = ""
    ai_response = ""

    # 路径配置
    python_exe = r"D:\\python3.9\\python.exe"  # 使用原始字符串避免路径中的转义字符
    model_path = os.path.join(renpy.config.gamedir, "models", "vosk-model-small-en-us-0.15")
    asr_script = os.path.join(renpy.config.gamedir, "local_asr.py")
    ai_response_script = os.path.join(renpy.config.gamedir, "get_ai_response.py")
    tts_script = os.path.join(renpy.config.gamedir, "tts_script.py")

    def voice_recognition():
        global recognition_result, is_listening
        try:
            proc = subprocess.run(
                [python_exe, asr_script, "--model", model_path],
                capture_output=True,
                text=True,
                timeout=30  # 增加超时时间到30秒
            )
            print(f"ASR Output (stdout): {proc.stdout}")  # 增加日志输出
            print(f"ASR Output (stderr): {proc.stderr}")  # 增加日志输出
            
            # 过滤掉非 JSON 部分的内容，仅解析 stdout 中的最后一行
            lines = proc.stdout.strip().splitlines()
            last_line = lines[-1] if lines else ""
            
            if last_line.startswith("{") and last_line.endswith("}"):  # 简单判断是否为 JSON 格式
                try:
                    result = json.loads(last_line)
                    recognition_result = result.get("recognized_text", "")
                    print(f"Recognized Text: {recognition_result}")  # 增加日志输出
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error in ASR: {str(e)}")  # 增加日志输出
                    recognition_result = f"JSON Decode Error in ASR: {str(e)}"
            else:
                recognition_result = "No valid JSON output from ASR."
                print(recognition_result)
                
        except subprocess.TimeoutExpired:
            recognition_result = "Recognition timeout, please try again."
            print("Recognition Timeout")  # 增加日志输出
        except Exception as e:
            recognition_result = f"Runtime Error: {str(e)}"
            print(f"Runtime Error: {str(e)}")  # 增加日志输出
        finally:
            is_listening = False

    def get_ai_reply(message):
        try:
            proc = subprocess.run(
                [python_exe, ai_response_script, message],
                capture_output=True,
                text=True,
                timeout=30  # 增加超时时间到30秒
            )
            stdout = proc.stdout.encode('utf-8').decode('utf-8', errors='ignore')  # 处理非UTF-8字符
            stderr = proc.stderr.encode('utf-8').decode('utf-8', errors='ignore')  # 处理非UTF-8字符
            
            print(f"AI Response Output (stdout): {stdout}")  # 增加日志输出
            print(f"AI Response Output (stderr): {stderr}")  # 增加日志输出
            
            if proc.returncode == 0:
                try:
                    result = json.loads(stdout.strip())
                    ai_response = result.get("ai_response", "")
                    # 将可能包含特殊字符的字符串进行清理
                    ai_response = ai_response.replace("[", "\$").replace("]", "\$")
                    return ai_response
                except json.JSONDecodeError as e:
                    return f"JSON Decode Error in AI Response: {str(e)}"
            else:
                error_msg = stderr.strip() or "Unknown Error"
                return f"AI Response failed: {error_msg}"
        except subprocess.TimeoutExpired:
            return "AI Response timeout, please try again."
        except Exception as e:
            return f"Runtime Error: {str(e)}"
    
    def generate_and_save_audio(text, lang='en'):
        audio_dir = os.path.join(renpy.config.gamedir, "audio")
        audio_file = "temp_audio.mp3"
        output_path = os.path.join(audio_dir, audio_file)
        
        proc = subprocess.run(
            [python_exe, tts_script, text, lang, audio_dir, audio_file],
            capture_output=True,
            text=True
        )
        print(f"TTS Output (stdout): {proc.stdout}")  # 增加日志输出
        print(f"TTS Output (stderr): {proc.stderr}")  # 增加日志输出
        
        if proc.returncode == 0:
            return output_path
        else:
            print(f"TTS failed: {proc.stderr}")
            return None

    

# 定义全局变量
default user_message = ""
default ai_response = ""

image haru_greeter = MyLive2D(
    "live2d/haru_greeter_pro_jp/runtime/haru_greeter_t05.model3.json",
    base=0.6,
    loop=True,
    fade=0.5
)

screen listening_ui():
    zorder 100
    fixed:
        xalign 0.5
        yalign 0.8
        vbox:
            text "Click and talk" size 30 color "#FF0000"
            text "Recognized: [recognition_result]" size 25 color "#FFFFFF"

label start:
    scene bg classroom
    show screen listening_ui
    show haru_greeter haru_g_idle
    ai "Hello, what would you like to talk about?"
    
    while True:
        # 开始语音识别
        $ is_listening = True
        $ recognition_result = ""
        $ renpy.invoke_in_thread(voice_recognition)
        
        # 等待识别完成
        while is_listening:
            pause 0.1
        
        # 显示识别结果并获取AI回复
        if recognition_result and "error" not in recognition_result.lower():
            $ user_message = recognition_result
            "you: [user_message]"
            
            # 获取AI回复
            $ ai_response = get_ai_reply(user_message)
            show haru_greeter haru_g_m05

    # 使用动态生成的动作名称显示角色
            # 生成并保存AI回复的音频
            $ audio_file_path = generate_and_save_audio(ai_response)

            # 如果成功生成音频文件，则播放它
            if audio_file_path:
                voice "temp_audio.mp3"
                ai "[ai_response]"
            else:
                ai "Sorry, there was an issue generating the audio response."

            show haru_greeter haru_g_m06

            #ai "[ai_response]"
            #show haru_greeter haru_g_idle
        else:
            ai "I couldn't hear you, could you please speak again?"

    return