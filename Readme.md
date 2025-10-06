![cover](figures/misevolution_github_cover.png)

<div align="center">

#  Your Agent May Misevolve: Emergent Risks in Self-evolving LLM Agents

</div>


<div align="center">

[![Paper](https://img.shields.io/badge/Arxiv-misevolution?style=for-the-badge&logo=arxiv&logoColor=white&color=%23B22222)](https://arxiv.org/abs/2509.26354) [![Github](https://img.shields.io/badge/Github-misevolution?style=for-the-badge&logo=github&logoColor=white&color=black)](https://github.com/ShaoShuai0605/Misevolution) [![Huggingface](https://img.shields.io/badge/dataset-misevolution?style=for-the-badge&logo=huggingface&logoColor=black&color=%23FFD21F)]()

</div>

---

# 📚 Overview
- 📢 [News](#news)  
- 📖 [Introduction](#introduction)  
- ✨ [Getting Started](#getting-started)  
- 🔧 [Usage](#usage)   
- 🙏 [Citation](#citation)  
- 🌻 [Acknowledgement](#acknowledgement)  
<!-- - 📈 [Star History](#star-history) -->


<div align="center">
  <hr width="100%">
</div>



## 📢News
- **[2025/10/06]** Our paper is available on [Huggingface](https://huggingface.co/papers/2509.26354). If you enjoy our work, we warmly invite you to **upvote** it on Huggingface!
- **[2025/09/30]** Our paper is available on [arXiv](https://arxiv.org/pdf/2509.26354). 



---
## 📖Introduction


**Self-evolving agents**, systems that can improve themselves with minimal human input, have become an exciting and emerging area of research. 
However, self-evolution also introduces novel risks that existing safety research often misses. In this work, we study the case where *an agent's self-evolution deviates in unintended ways, leading to undesirable or even harmful outcomes*. We refer to this as **Misevolution**.
To provide a systematic investigation, we evaluate misevolution along four key evolutionary pathways: the agent's model, memory, tool, and workflow. 
Our empirical findings reveal that misevolution is a widespread risk, even for agents built on top models like Gemini-2.5-Pro.
Different emergent risks are observed in the self-evolutionary process, such as the degradation of safety alignment after memory accumulation, or the unintended introduction of vulnerabilities in tool creation and reuse. 
To our knowledge, this is the first study to systematically conceptualize misevolution and provide empirical evidence of its occurrence, highlighting an urgent need for new safety paradigms for self-evolving agents.

### Misevolution can happen in various scenarios
![showcase](figures/fig1_showcase.png)

The figure above shows some typical cases where misevolution may happen:

**(a) Biased memory evolution leads to over-refunding.** A customer service agent evolves its memory by storing the interaction history with the user, including the actions taken and the feedbacks & ratings from users. However, it may learn a biased correlation between the refunding action and positive user feedback from the memory, leading it to proactively offer refunds even when not asked to.

**(b) Tool evolution by ingesting appealing but insecure code causes data leakage.** An agent evolves its toolset by searching and ingesting open-source tools from GitHub. However, it may incorporate seemingly useful but insecure code from a public repository, inadvertently creating a new tool with a backdoor that leaks data.

**(c) Inappropriate cross-domain tool reuse leads to privacy issues.** An agent evolves its toolset by self-creating new tools and reusing existing ones. For one task (sharing posters with participants), it creates a general-purpose tool called `upload_and_share_files`, which upload the files to be shared and generates a public link. Later, in another task (sharing a financial report with the board), the agent reuses this tool, but does not notice that the financial report is confidential. As a result, it creates a public link, which can lead to privacy issues and can be targeted by cyber attacks.

<div align="center">
  <hr width="100%">
</div>


## ✨ Getting Started

Coming soon.

---
## 🔧 Usage

### Memory Misevolution

#### Reward Hacking
To reproduce the reward hacking experiment, you may first set your base_url and api_key in the reward_hacking_test.py file.

Then, you can run the following command:

```bash

python reward_hacking_test.py --model gemini-2.5-pro --scenario finance
```

### Tool Misevolution

#### Insecure Tool Creation and Reuse
To reproduce the insecure tool creation and reuse experiment, you may first set your base_url, api_key and model to be evaluated in the config.py file.

Then, you can run the following command:

```bash

bash insecure_tool_evaluation.sh
```


---

## 🙏 Citation

If you find this work useful, please consider citing:

```bibtex
@article{shao2025misevolution,
    title={Your Agent May Misevolve: Emergent Risks in Self-evolving LLM Agents}, 
    author={Shuai Shao and Qihan Ren and Chen Qian and Boyi Wei and Dadi Guo and Jingyi Yang and Xinhao Song and Linfeng Zhang and Weinan Zhang and Dongrui Liu and Jing Shao},
    journal={arXiv preprint arXiv:2509.26354},
    year={2025}
}
```

## 🌻 Acknowledgements
This work is partially inspired by this [survey](https://github.com/CharlesQ9/Self-Evolving-Agents) on self-evolving agents. Part of our evaluation code is based from [Harmbench](https://github.com/centerforaisafety/HarmBench), [SALAD-Bench](https://github.com/OpenSafetyLab/SALAD-BENCH), [LLMs-Finetuning-Safety](https://github.com/LLM-Tuning-Safety/LLMs-Finetuning-Safety), [Agent-SafetyBench](https://github.com/thu-coai/Agent-SafetyBench), [RiOSWorld](https://github.com/yjyddq/RiOSWorld), and [RedCode](https://github.com/ai-secure/redcode). Thanks to these wonderful works!
