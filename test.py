# -*- coding: utf-8 -*-
# @Time    : 2025/4/30/周三 20:29
# @Author  : Administrator
# @File    : test.py
class KokoroTTSGenerator:
    """
    KokoroTTS的语音生成和保存节点
    """

    def __init__(self):
        # 设置采样率
        self.sample_rate = 24000
        import os

        # 确保输出目录存在
        try:
            import folder_paths
        except ImportError:
            # Fallback for when running outside of ComfyUI
            print("Warning: 'folder_paths' module not found. Using local output directory instead.")

            class FolderPathsEmulator:
                def get_output_directory(self):
                    # Default to a local 'output' directory
                    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
                    os.makedirs(output_dir, exist_ok=True)
                    return output_dir

            folder_paths = FolderPathsEmulator()

        try:
            # 获取ComfyUI的输出目录
            self.output_dir = folder_paths.get_output_directory()
        except Exception as e:
            # 如果获取失败，使用备用目录
            print(f"无法获取ComfyUI输出目录：{e}，使用备用目录")
            self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")

        os.makedirs(self.output_dir, exist_ok=True)
        print(f"音频将保存到目录: {self.output_dir}")

    @classmethod
    def INPUT_TYPES(cls):
        """
        定义节点的输入参数
        """
        return {
            "required": {
                "model": ("KOKORO_MODEL",),
                "pipeline": ("KOKORO_PIPELINE",),
                "text": ("KOKORO_TEXT",),
                "voice_settings": ("KOKORO_VOICE_SETTINGS",),
                "output_filename": ("STRING", {"default": "kokoro_output.wav", "multiline": False}),
            }
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "filename")
    FUNCTION = "generate_audio"
    CATEGORY = "KokoroTTS"
    OUTPUT_NODE = True

    def speed_callable(self, len_ps):
        """
        根据音素长度动态调整语速的回调函数，避免长文本生成时语速过快

        Args:
            len_ps: 音素长度

        Returns:
            语速调整系数
        """
        speed = 0.8
        if len_ps <= 83:
            speed = 1
        elif len_ps < 183:
            speed = 1 - (len_ps - 83) / 500
        return speed * 1.1

    def generate_audio(self, model, pipeline, text, voice_settings, output_filename):
        """
        生成并保存音频

        Args:
            model: KokoroTTS模型
            pipeline: KokoroTTS管道
            text: 文本内容
            voice_settings: 语音设置
            output_filename: 输出文件名

        Returns:
            (audio_data, file_path): 音频数据和保存的音频文件路径
        """
        import tqdm
        import os

        # 解析设置
        voice = voice_settings["voice"]
        silence = voice_settings["silence"]
        join_sentences = voice_settings["join_sentences"]

        # 获取文本
        texts = text

        # 如果需要连接句子
        if join_sentences:
            for i in range(len(texts)):
                if len(texts[i]) > 1:  # 只有当段落有多个句子时才连接
                    texts[i] = [''.join(texts[i])]

        # 确保输出文件名有正确的扩展名
        if not output_filename.lower().endswith('.wav'):
            output_filename += '.wav'

        output_path = os.path.join(self.output_dir, output_filename)

        print(f"开始生成语音，使用语音：{voice}")
        print(f"将保存到：{output_path}")

        # 生成语音
        wavs = []

        for paragraph_idx, paragraph in enumerate(tqdm.tqdm(texts)):
            for i, sentence in enumerate(paragraph):
                # 生成语音
                generator = pipeline(sentence, voice=voice, speed=self.speed_callable)
                result = next(generator)
                wav = result.audio

                # 段落之间添加静音
                if i == 0 and wavs and silence > 0:
                    wav = np.concatenate([np.zeros(silence), wav])

                wavs.append(wav)

        # 合并所有语音
        final_wav = np.concatenate(wavs)

        # 保存音频文件
        sf.write(output_path, final_wav, self.sample_rate)

        # 创建音频对象，符合PreAudio预期的格式
        audio_obj = {
            "samples": final_wav,
            "sampling_rate": self.sample_rate,
            "path": output_path
        }

        print(f"语音生成完成，已保存到：{output_path}")
        return (audio_obj, output_path)