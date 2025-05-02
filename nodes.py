# -*- coding: utf-8 -*-
# @Time    : 2025/4/30/周三 16:08
# @Author  : ruanjianlun
# @File    : nodes.py
# KokoroTTS for ComfyUI
# 将KokoroTTS集成到ComfyUI中的节点

import torch
import numpy as np
import soundfile as sf
from kokoro import KModel, KPipeline
import os


# 模型加载节点
class KokoroModelLoader:
    """
    加载KokoroTTS模型的节点
    """

    @classmethod
    def INPUT_TYPES(cls):
        """
        定义节点的输入参数
        """
        return {
            "required": {
                "repo_id": ("STRING", {"default": "hexgrad/Kokoro-82M-v1.1-zh", "multiline": False}),
            }
        }

    RETURN_TYPES = ("KOKORO_MODEL", "KOKORO_PIPELINE")
    FUNCTION = "load_model"
    CATEGORY = "KokoroTTS"

    def load_model(self, repo_id):
        """
        加载KokoroTTS模型

        Args:
            repo_id: Hugging Face上的模型ID

        Returns:
            加载的模型和管道对象
        """
        print(f"正在加载KokoroTTS模型: {repo_id}")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # 初始化英文语音管道（不加载模型）
        en_pipeline = KPipeline(lang_code='a', repo_id=repo_id, model=False)

        # 定义英文发音回调函数
        def en_callable(text):
            if text == 'Kokoro':
                return 'kˈOkəɹO'
            elif text == 'Sol':
                return 'sˈOl'
            return next(en_pipeline(text)).phonemes

        # 加载模型
        model = KModel(repo_id=repo_id).to(device).eval()

        # 初始化中文语音管道
        zh_pipeline = KPipeline(lang_code='z', repo_id=repo_id, model=model, en_callable=en_callable)

        print(f"KokoroTTS模型加载完成: {repo_id}")
        return (model, zh_pipeline)


# 文本输入节点
class KokoroTextInput:
    """
    KokoroTTS的文本输入节点
    """

    @classmethod
    def INPUT_TYPES(cls):
        """
        定义节点的输入参数
        """
        return {
            "required": {
                "text": ("STRING", {"default": "hello KokoroTTS！", "multiline": True}),
            }
        }

    RETURN_TYPES = ("KOKORO_TEXT",)
    FUNCTION = "process_text"
    CATEGORY = "KokoroTTS"

    def process_text(self, text):
        """
        处理输入文本

        Args:
            text: 要转换为语音的文本

        Returns:
            处理后的文本列表
        """
        # 将输入文本按段落分割（以空行为界）
        paragraphs = []
        current_paragraph = []

        for line in text.split('\n'):
            line = line.strip()
            if line:
                current_paragraph.append(line)
            elif current_paragraph:  # 遇到空行且当前段落非空
                paragraphs.append(current_paragraph)
                current_paragraph = []

        # 添加最后一个段落（如果有）
        if current_paragraph:
            paragraphs.append(current_paragraph)

        # 如果没有文本，添加默认文本
        if not paragraphs:
            paragraphs = [["欢迎使用KokoroTTS！"]]

        print(f"已处理文本，共{len(paragraphs)}个段落")
        return (paragraphs,)


# 语音选择节点
class KokoroVoiceSelector:
    """
    KokoroTTS的语音选择节点
    """

    @classmethod
    def INPUT_TYPES(cls):
        """
        定义节点的输入参数
        """
        # 支持的语音列表，从zf_001到zf_050是女声，zm_001到zm_050是男声
        voices = [f"zf_{i:03d}" for i in range(1, 51)] + [f"zm_{i:03d}" for i in range(1, 51)]

        return {
            "required": {
                "voice": (voices, {"default": "zf_018"}),
                "silence_between_paragraphs": ("INT", {"default": 5000, "min": 0, "max": 20000, "step": 100}),
                "join_sentences": (["False", "True"], {"default": "False"}),
            }
        }

    RETURN_TYPES = ("KOKORO_VOICE_SETTINGS",)
    FUNCTION = "select_voice"
    CATEGORY = "KokoroTTS"

    def select_voice(self, voice, silence_between_paragraphs, join_sentences):
        """
        选择语音和相关设置

        Args:
            voice: 选择的语音ID
            silence_between_paragraphs: 段落之间的静音长度（采样点数）
            join_sentences: 是否连接段落中的句子

        Returns:
            语音设置字典
        """
        join_sentences = join_sentences == "True"

        voice_settings = {
            "voice": voice,
            "silence": silence_between_paragraphs,
            "join_sentences": join_sentences
        }

        print(f"已选择语音: {voice}, 段落间隔: {silence_between_paragraphs}, 连接句子: {join_sentences}")
        return (voice_settings,)


# 语音生成和保存节点
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
                "speed_mode": (["auto", "fixed"], {"default": "auto"}),
                "fixed_speed": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.0, "step": 0.1}),
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

    ##############################

    def generate_audio(self, model, pipeline, text, voice_settings, output_filename, speed_mode, fixed_speed):
        """
        生成并保存音频
        """
        import os
        import tqdm
        import torch

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
        print(f"速度模式：{speed_mode}" + (f"，固定速度：{fixed_speed}" if speed_mode == "fixed" else ""))

        # 选择速度回调函数
        if speed_mode == "auto":
            speed_function = self.speed_callable
        else:
            # 使用固定速度
            def fixed_speed_callable(_):
                return fixed_speed

            speed_function = fixed_speed_callable

        # 生成语音
        wavs = []

        for paragraph_idx, paragraph in enumerate(tqdm.tqdm(texts)):
            for i, sentence in enumerate(paragraph):
                # 生成语音
                generator = pipeline(sentence, voice=voice, speed=speed_function)
                result = next(generator)
                wav = result.audio

                # 段落之间添加静音
                if i == 0 and wavs and silence > 0:
                    wav = np.concatenate([np.zeros(silence), wav])

                wavs.append(wav)

        # 合并所有语音
        final_wav = np.concatenate(wavs)
        # 保证是float32类型的numpy数组
        final_wav = final_wav.astype(np.float32)
        ##################
        waveform_tensor = torch.from_numpy(final_wav.astype(np.float32))
        if waveform_tensor.dim() == 1:
            waveform_tensor = waveform_tensor.unsqueeze(0).unsqueeze(0)  # [1, 1, N]
        elif waveform_tensor.dim() == 2:
            waveform_tensor = waveform_tensor.unsqueeze(0)  # [1, C, N]
        elif waveform_tensor.dim() == 3:
            pass  # 已经是 [B, C, N]
        else:
            raise ValueError("waveform_tensor shape不支持: %s" % (waveform_tensor.shape,))

        print("waveform_tensor.shape:", waveform_tensor)

        #############

        audio_obj = {
            "waveform": waveform_tensor,
            "sample_rate": self.sample_rate
        }
        return audio_obj, output_path


# 节点列表，用于注册到ComfyUI
NODE_CLASS_MAPPINGS = {
    "KokoroModelLoader": KokoroModelLoader,
    "KokoroTextInput": KokoroTextInput,
    "KokoroVoiceSelector": KokoroVoiceSelector,
    "KokoroTTSGenerator": KokoroTTSGenerator,
}

# 节点显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "KokoroModelLoader": "KokoroModelLoader",
    "KokoroTextInput": "KokoroTextInput",
    "KokoroVoiceSelector": "KokoroVoiceSelector",
    "KokoroTTSGenerator": "KokoroTTSGenerator",
}
