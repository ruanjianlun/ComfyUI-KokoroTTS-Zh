# ComfyUI-KokoroTTS-Zh

A custom node extension for ComfyUI that integrates KokoroTTS for high-quality Chinese text-to-speech synthesis.

## 简介 (Introduction)

ComfyUI-KokoroTTS-Zh 是一个 ComfyUI 的扩展节点集合，将 KokoroTTS 语音合成引擎集成到 ComfyUI 工作流中。它提供了高质量的中文语音合成功能，支持多种声音和语速调整。

## 特性 (Features)

- 加载 KokoroTTS 模型
- 处理多段落文本输入
- 支持近 100 种不同的中文声音（50 种女声和 50 种男声）
- 段落间静音控制
- 句子连接选项
- 支持自动和固定语速模式
- 生成高质量 24kHz 采样率的 WAV 音频
- 与 ComfyUI 音频节点兼容

## 安装 (Installation)

### 要求 (Requirements)

- Python 3.8+
- ComfyUI
- PyTorch
- 其他依赖包：
  - kokoro
  - soundfile
  - tqdm

### 安装步骤 (Installation Steps)

1. 确保已安装 ComfyUI 并正常运行

2. 克隆此仓库到 ComfyUI 的 `custom_nodes` 目录：

   ```bash
   cd /path/to/ComfyUI/custom_nodes
   git clone https://github.com/ruanjianlun/ComfyUI-KokoroTTS-Zh.git
    pathto\python_embeded\python.exe -m pip install "kokoro>=0.8.1" "misaki[zh]>=0.8.1"  "soundfile>=0.10.0" 