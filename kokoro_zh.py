# -*- coding: utf-8 -*-
# @Time    : 2025/4/25/周五 23:31
# @Author  : Administrator
# @File    : kokoro_zh.py
# Therefore it may NOT generalize gracefully to other texts
# Refer to Usage in README.md for more general usage patterns
# pip install kokoro>=0.8.1 "misaki[zh]>=0.8.1"
from kokoro import KModel, KPipeline
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
import tqdm

REPO_ID = 'hexgrad/Kokoro-82M-v1.1-zh'
SAMPLE_RATE = 24000

# How much silence to insert between paragraphs: 5000 is about 0.2 seconds
N_ZEROS = 5000

# Whether to join sentences in paragraphs 1 and 3
JOIN_SENTENCES = True

# VOICE = 'zf_001' if True else 'zm_010'

'''
voice 选择支持100个voice
https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh/tree/main/voices
'''
VOICE = 'zf_018' if True else 'zm_010'

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# texts = [(
#     "Kokoro 是一系列体积虽小但功能强大的 TTS 模型。",
# ), (
#     "该模型是经过短期训练的结果，从专业数据集中添加了100名中文使用者。",
#     "中文数据由专业数据集公司「龙猫数据」免费且无偿地提供给我们。感谢你们让这个模型成为可能。",
# ), (
#     "另外，一些众包合成英语数据也进入了训练组合：",
#     "1小时的 Maple，美国女性。",
#     "1小时的 Sol，另一位美国女性。",
#     "和1小时的 Vale，一位年长的英国女性。",
# ), (
#     "由于该模型删除了许多声音，因此它并不是对其前身的严格升级，但它提前发布以收集有关新声音和标记化的反馈。",
#     "除了中文数据集和3小时的英语之外，其余数据都留在本次训练中。",
#     "目标是推动模型系列的发展，并最终恢复一些被遗留的声音。",
# ), (
#     "美国版权局目前的指导表明，合成数据通常不符合版权保护的资格。",
#     "由于这些合成数据是众包的，因此模型训练师不受任何服务条款的约束。",
#     "该 Apache 许可模式也符合 OpenAI 所宣称的广泛传播 AI 优势的使命。",
#     "如果您愿意帮助进一步完成这一使命，请考虑为此贡献许可的音频数据。",
# )]

# texts = [(
#     "本期我们来聊一下TOR的网桥。",
#     "我们先开门见山说最重要的。",
# ), (
#     "网桥是一个可以让用户访问TOR网络的一种方式。",
#     "网桥是用来隐藏我们正在使用TOR的事实。",
# ), (
#     "很多朋友就有疑问了。",
#     "TOR它不是拟明性很强吗。",
#     "为什么还要网桥才能隐藏呢?",
# ), (
#     "这个且听我们一一道来。",
# )]


texts = [(
    "hello my name is lisa 嘿，大家好！今天要给各位安利一个超强的AI图像生成工具--ComfyUI！",
    "不夸张地说，这可能是目前最强大的Stable Diffusion操作界面了！",
), (
    "ComfyUI就像是给AI绘画装上了\"乐高积木\"系统！",
    "它不像其他AI工具那样只能填几个参数就点生成，而是让你通过连接各种功能模块，像搭积木一样自由组合出你想要的任何效果！",
    "想象一下，你可以把提示词、模型、采样器这些\"积木\"随意连接，还能实时看到每一步的变化。",
    "简直就是AI绘画师的\"梦想工作台\"！",
), (
    "为什么专业人士都在用ComfyUI？",
    "完全掌控每个细节：不再是黑盒操作，你能看到图像是怎么一步步生成的。",
    "省显存、跑得快：同样的电脑，ComfyUI能跑更大更复杂的模型。",
    "一次设计，反复使用：设计好的流程可以保存下来，下次直接加载就能用。",
    "想法立刻变现实：有什么新奇想法，立刻就能搭建出来试试看。",
), (
    "实际用起来是什么感觉？",
    "刚开始看到那些节点和连线可能会有点懵。",
    "但别担心！你可以先用现成的工作流，就像用别人分享的\"食谱\"一样，慢慢就能理解每个节点是干嘛的了。",
    "当你调整一个参数，能立刻看到它对最终图像的影响。这种即时反馈真的超级爽！",
    "社区里有超多大神分享的工作流，从人像美化、场景生成到动漫风格转换，应有尽有。",
    "你完全可以站在巨人的肩膀上，快速出图！",
), (
    "谁适合用ComfyUI？",
    "你是设计师，想要完全掌控AI生成的每个细节。",
    "你是内容创作者，需要快速生成高质量的原创图像。",
    "你是技术爱好者，想深入了解AI图像生成的原理。",
    "你是普通用户，但厌倦了其他工具的局限性。",
    "即使你是AI新手，只要愿意花一点时间学习，ComfyUI绝对能让你的创作能力提升好几个档次！",
), (
    "最后的小建议",
    "开始用ComfyUI的最好方式就是下载它，加载一个现成的工作流，然后开始\"玩\"！",
    "别被那些节点吓到，把它们想象成乐高积木，一块一块地了解它们的功能。",
    "相信我，一旦你掌握了ComfyUI，你会惊讶于自己能创造出什么样的图像！",
    "准备好解锁AI创作的新境界了吗？ComfyUI等你来探索！",
)]




if JOIN_SENTENCES:
    for i in (1, 3):
        texts[i] = [''.join(texts[i])]

# en_pipeline = KPipeline(lang_code='z', repo_id=REPO_ID, model=False, )
en_pipeline = KPipeline(lang_code='a', repo_id=REPO_ID, model=False, )


def en_callable(text):
    if text == 'Kokoro':
        return 'kˈOkəɹO'
    elif text == 'Sol':
        return 'sˈOl'
    return next(en_pipeline(text)).phonemes


# HACK: Mitigate rushing caused by lack of training data beyond ~100 tokens
# Simple piecewise linear fn that decreases speed as len_ps increases
def speed_callable(len_ps):
    speed = 0.8
    if len_ps <= 83:
        speed = 1
    elif len_ps < 183:
        speed = 1 - (len_ps - 83) / 500
    return speed * 1.1


model = KModel(repo_id=REPO_ID).to(device).eval()

zh_pipeline = KPipeline(lang_code='z', repo_id=REPO_ID, model=model, en_callable=en_callable)

path = Path(__file__).parent

wavs = []
for paragraph in tqdm.tqdm(texts):
    for i, sentence in enumerate(paragraph):
        generator = zh_pipeline(sentence, voice=VOICE, speed=speed_callable)
        f = path / f'zh{len(wavs):02}.wav'
        result = next(generator)
        wav = result.audio
        sf.write(f, wav, SAMPLE_RATE)
        if i == 0 and wavs and N_ZEROS > 0:
            wav = np.concatenate([np.zeros(N_ZEROS), wav])
        wavs.append(wav)

sf.write(path / f'HEARME_{VOICE}.wav', np.concatenate(wavs), SAMPLE_RATE)

final_wav = np.concatenate(wavs)

# 保证是float32类型的numpy数组
final_wav = final_wav.astype(np.float32)
# 假设 final_wav 是 numpy 数组
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
