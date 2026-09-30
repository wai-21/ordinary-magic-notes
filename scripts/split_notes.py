# -*- coding: utf-8 -*-
"""
把《最小努力法则》单文件笔记按标题拆成 18 篇独立单页 + docs/index.md 总目录。

用法：python scripts/split_notes.py
幂等：可 rm -rf docs 后重跑。分篇一律由本脚本从单文件生成，禁止手改 docs/。
"""
import os, re

ROOT = "/Users/semedia_editing/WorkBuddy/2026-09-30-11-36-01/ordinary-magic-notes"
SRC = "最小努力法则-核心精髓与思维演化笔记.md"
OUT = "docs"

BOOK = "最小努力法则读书笔记"

INDEX_TITLE = "《最小努力法则》(Ordinary Magic) 读书笔记 · 总目录（16 主题）"
INDEX_DESC = "把格雷戈里·沃尔顿的《Ordinary Magic》拆进 16 个高压决策场景：向下螺旋、习得性无助、身份重塑、受威胁的自尊、信任重建、归属感、制度设计，以及动态常模、超越性目的、体制隐喻与涟漪效应四大宏观系统章，附 60 条行动算法。"
INDEX_KEYWORDS = ("最小努力法则, Ordinary Magic, 格雷戈里沃尔顿, 明智干预, wise interventions, "
                 "读书笔记, 向下螺旋, 习得性无助, 叙事重构, 身份重塑, 归属感, 制度设计, "
                 "动态常模, 超越性目的, 体制隐喻, 涟漪效应, 递归循环")
INDEX_H1 = "📘 《最小努力法则》(Ordinary Magic) · 读书笔记总目录（16 主题）"

# (输出档名, front matter title, 起始行判定, keywords, description)
SECTIONS = [
    ("00-导览-最小努力法则-30秒读懂.md", f"30 秒看懂这份笔记 · {BOOK}",
     lambda l: l.startswith("## 🚪 先读这里"),
     "最小努力法则, Ordinary Magic, 读书笔记, 明智干预, 沙盘推演, 术语急救包",
     "原书在讲什么、这个沙盘是怎么玩的、三个必补的背景常识、出场人物速查与 28 条术语急救包。"),

    ("roadmap-Ordinary-Magic-16主题演化地图.md", f"学习演化地图：16 个主题对照表 · {BOOK}",
     lambda l: l.startswith("## 🧭 学习演化地图"),
     "学习演化地图, roadmap, Ordinary Magic 章节对照, 核心精髓, 可迁移结论",
     "12 个主题 × 原书核心精髓 × 我的可迁移结论的四列对照表，一页看清全书拆解进度。"),

    ("01-向下螺旋-新人被否定-行为前置.md", f"向下螺旋：为什么一句平淡的否定能毁掉一个新人 · {BOOK}",
     lambda l: l.startswith("### 01."),
     "向下螺旋, spiraling down, 归因, 行为前置, 微小闭环, 新人融入",
     "毁掉一个人的从来不是那件小事，而是他把小事翻译成『我不行』之后开始按『我不行』的方式做事；破解靠允许触底、剥离意义、无威胁的微小闭环。"),

    ("02-习得性无助-归因维度-工单降维.md", f"我能做到吗：把「我们完了」降维成一张工单 · {BOOK}",
     lambda l: l.startswith("### 02."),
     "习得性无助, learned helplessness, 归因维度, 掌控感, 悖论意向, 定量",
     "团队说『我们完了』时不要反驳结论，要拆量词：把『完了』拆成『3 个 bug 和 1 个交互失误』；禁定性词，强制定量。"),

    ("03-身份重塑-名词的力量-撕标签.md", f"我是谁：给他一个名词，再用这个名词锁住他的行为 · {BOOK}",
     lambda l: l.startswith("### 03."),
     "身份重塑, identity reframing, 名词的力量, 自我一致性偏误, 撕标签, 刺头员工",
     "想改一个人的行为别去纠正动作，去改他『是什么人』的定义；提纯负面行为的正面动机，铸成名词化护身符，再给一个能落地的最小动作。"),

    ("04-受威胁的自尊-为什么安慰会适得其反.md", f"你爱/看重我吗：为什么越安慰，对方越觉得被看扁 · {BOOK}",
     lambda l: l.startswith("### 04."),
     "受威胁的自尊, threatened ego, 同情即看扁, 说即是信, 倡导者效应, 认知镜像反弹",
     "对刚被击碎的人，『没关系、大不了不做』不是安慰是宣判；正解是封锁同情、身份翻转向他求助、触发说即是信。"),

    ("05-信任重建-猜忌-终局利益推演.md", f"我能信任你吗：别自证清白，把结局摆到他面前 · {BOOK}",
     lambda l: l.startswith("### 05."),
     "信任重建, 猜忌, 确认偏误, 自证陷阱, 命运共同体, 结构性透明",
     "当一个人认定你要害他，你做的每件好事都会被翻译成阴谋；解法是冻结自证、认领最坏标签、快进到毁灭后 24 小时、用结构捆绑替代道德信任。"),

    ("06-归属感-局外人-功能性互补.md", f"我属于这里吗：不要让他融入，让他变得不可替代 · {BOOK}",
     lambda l: l.startswith("### 06."),
     "归属感, 归属不确定性, do I belong, 局外人, 功能性互补, 超常目标",
     "『你多跟大家聊聊、主动融入』是一句有毒的话；正解是把他的格格不入重新定义成系统的稀缺资产，用共同危机而非团建建立归属。"),

    ("07-制度设计-连坐-移情式纪律.md", f"宏观制度：制度传递的暗语，比制度条文更致命 · {BOOK}",
     lambda l: l.startswith("### 07."),
     "制度设计, 连坐, 责任原子化, 程序正义, 移情式纪律, 恢复性司法, 公地悲剧",
     "一套需要四个人盖章才能报销 50 块的流程，暗语是『我们认定你们全是贼』；制度四查与把违规当系统 bug report 的三步闭环。"),

    ("08-临危受命-横向否决权-非对称激励.md", f"大考一：当三套各自正确的机制互相抵消 · {BOOK}",
     lambda l: l.startswith("### 08."),
     "临危受命, 横向否决权, 双签, 主攻手, 非对称激励, 智慧环境, 制度支架",
     "三枚各自完美的齿轮咬合在同一个系统会互相卡死；先改结构再改叙事——拔横向否决权、锁定主攻手、非对称激励、封装防守方。"),

    ("09-刺头天才-勒索-希望的架构.md", f"大考二：你惩罚过的天才，会反过来敲诈你 · {BOOK}",
     lambda l: l.startswith("### 09."),
     "刺头天才, 勒索, 希望的架构, 合法逃生舱, 动态随机性, 阿蒙",
     "把一个人打到底层又给他一把能锁死队友的钥匙，他一定会开黑市；先截断勒索面，再凿一条极限合法逃生舱。"),

    ("10-吹哨人悖论-抽屉协议-自首式披露.md", f"大考三：抽屉协议是你亲手递出去的刀 · {BOOK}",
     lambda l: l.startswith("### 10."),
     "吹哨人悖论, 抽屉协议, side letter, 自首式披露, 程序正义, IPO 合规",
     "公开羞辱他再私下塞一张不能见光的补偿协议，等于给自己戴上手铐再把钥匙递给他；禁抽屉协议、三层切割、抢在吹哨前自首式披露。"),

    ("11-明智反馈-元信号-天才爆破手.md", f"大考四：你赢了规矩，输了资产负债表 · {BOOK}",
     lambda l: l.startswith("### 11."),
     "明智反馈, wise feedback, 元信号, 双轨叙事, 下台阶梯, 创新沙盒",
     "处罚的杀伤力不取决于多重，而取决于它向全公司广播了一句什么话；四步 Wise Repair 修复清单。"),

    ("12-叙事重构-禀赋效应-冷处理.md", f"叙事重构总纲：整本书的第一性原理 · {BOOK}",
     lambda l: l.startswith("### 12."),
     "叙事重构, 禀赋效应, 过度理由效应, 冷处理, 阿基米德支点, 行为证据",
     "不要改变他手上的任务，只改变他对这个任务的解释；诊断叙事病毒、寻找阿基米德支点、创造行为证据而非口头承诺。"),

    ("13-群体常模-动态常模-私下信念差.md", f"群体常模：为什么「大家都想卷」是个沉默的谎言 · {BOOK}",
     lambda l: l.startswith("### 13."),
     "动态常模, dynamic norms, 多元无知, 谢林点, 信息级联, 默认架构, 破除群体陋习",
     "群体最毒的压迫是「人人都在演、都以为只有自己在演」；先测私下信念差、宣变化率、建特例沙盒、用系统默认值替代说教。"),

    ("14-超越性目的-双重动机-沈博士.md", f"超越性目的：为什么「科技向善」和「就是为钱」都是毒药 · {BOOK}",
     lambda l: l.startswith("### 14."),
     "超越性目的, self-transcendent purpose, 双重动机, dual-motive, 说即是信, 动机毒药",
     "让人忍受极致枯燥痛苦，加钱会疲软、喊口号催生犬儒；唯有双动机构（超越性目的感+个体利益）咬合，把商业定位为神圣目的的装甲。"),

    ("15-体制隐喻-支架型隐喻-洛哥雕塑.md", f"体制隐喻：为什么拆掉格子间比发奖金更管用 · {BOOK}",
     lambda l: l.startswith("### 15."),
     "体制隐喻, institutional messaging, 支架型隐喻, 同化型隐喻, 接口论, 环境线索",
     "人脑解码隐性意图；拆物理同化符号、建低摩擦接口、锁非对称契约边界、把反抗符号征用为系统自省雷达。"),

    ("16-涟漪效应-递归循环-探针重构.md", f"涟漪效应：为什么一场「奇迹」会在半年后打回原形 · {BOOK}",
     lambda l: l.startswith("### 16."),
     "涟漪效应, ripple effects, 递归循环, 可供性, 关键窗口, 世代传承, 探针",
     "干预要形成信念→行为→环境→强化信念的递归自持；锁关键窗口、改环境可供性、探针定性、滚动世代带新、微观测仪表盘。"),

    ("A-附录A-60条行动算法总表.md", f"附录 A：60 条行动算法总表 · {BOOK}",
     lambda l: l.startswith("## 🧾 附录 A"),
     "行动算法, checklist, 检查清单, 归因, 信任, 归属, 制度, 违规修复",
     "16 个沙盘沉淀出的 60 条算法，按 7 组场景归类，每条写成「触发信号 → 动作」，可直接当检查清单用。"),

    ("B-边界-心理干预13条失效条件.md", f"方法论的边界与已知盲区 · {BOOK}",
     lambda l: l.startswith("## ⚠️ 方法论的边界"),
     "方法论边界, 心理学干预失效, 零和博弈, 病态自恋, 实质性违法, 殉道者",
     "这份笔记自身的 5 条来源边界 + 方法论本身的 13 条失效条件 + 我 12 局的思维雷区复盘。"),

    ("C-附录B-书目信息-ISBN-目录核验.md", f"附录 B：书目信息与数据核验 · {BOOK}",
     lambda l: l.startswith("## 📎 附录 B"),
     "书目信息, ISBN, 9780593580899, Ordinary Magic 目录, 置信度, Gregory Walton",
     "已核验的书目信息（ISBN 9780593580899 / 464 页 / 2025-03-25）、11 章真实目录与起始页码、引文与数据的置信度总表。"),

    ("Z-收束-结构与叙事的先后.md", f"收束：这份笔记真正改变的东西 · {BOOK}",
     lambda l: l.startswith("## 🧩 收束"),
     "收束, 总结, 结构与叙事, 元信号, 读书笔记总结",
     "三层判断的顺序被重排：从改行为到改解释，从改解释到改结构，从改结构到改自己下手的本能。"),
]

# 原单文件里的锚点 → 分篇档名
ANCHOR_MAP = {
    "#guide": "00-导览-最小努力法则-30秒读懂.md",
    "#roadmap": "roadmap-Ordinary-Magic-16主题演化地图.md",
    "#appendix-a": "A-附录A-60条行动算法总表.md",
    "#limits": "B-边界-心理干预13条失效条件.md",
    "#appendix-b": "C-附录B-书目信息-ISBN-目录核验.md",
    "#closing": "Z-收束-结构与叙事的先后.md",
}

# 主题编号 → 分篇档名（预建表，不靠 os.listdir 反查）
# 注意：roadmap-*.md 不匹配 ^\d\d-，故不会被误纳入本表
TOPIC_FILE = {int(fn[:2]): fn for fn, *_ in SECTIONS if re.match(r"^\d\d-", fn)}

# 必须是 "./"：Pages → /docs/，GitHub → docs 目录页，两边都通且不依赖 permalink 解析行为
NAV_LABEL = "[📚 总目录](./)"


def rewrite_links(text):
    def rep(m):
        label, url = m.group(1), m.group(2)
        if url in ANCHOR_MAP:
            return f"[{label}]({ANCHOR_MAP[url]})"
        m2 = re.fullmatch(r"#d(\d\d)", url)
        if m2 and int(m2.group(1)) in TOPIC_FILE:
            return f"[{label}]({TOPIC_FILE[int(m2.group(1))]})"
        return m.group(0)
    return re.sub(r"\[([^\]]*)\]\((#[^)]+)\)", rep, text)


def strip_leading_heading(block):
    out = []
    for l in block:
        if re.match(r"^<a id=", l.strip()):
            continue
        m = re.match(r"^### (\d+)\. (.*)$", l)
        if m:
            out.append(f"# {m.group(2)}")
        elif l.startswith("## "):
            out.append("# " + l[3:])
        else:
            out.append(l)
    while out and not out[0].strip(): out.pop(0)
    while out and not out[-1].strip(): out.pop()
    return out


def main():
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    L = open(os.path.join(ROOT, SRC), encoding="utf-8").read().split("\n")
    starts = []
    for _, _, pred, _, _ in SECTIONS:
        starts.append(next(i for i, l in enumerate(L) if pred(l)))
    starts.append(len(L))

    # 首个 section 之前的引言块（一句话核心 / 元信息 / 目录 details）不属于任何一段，
    # 不预置到第 0 篇就会整段丢失。
    head = strip_leading_heading([l for l in L[:starts[0]] if not l.startswith("# ")])

    for i, (fname, title, _, kw, desc) in enumerate(SECTIONS):
        block = L[starts[i]:starts[i + 1]]
        if i == 0 and head:
            block = head + [""] + block
        body = "\n".join(strip_leading_heading(block))
        body = rewrite_links(body)
        prevf = SECTIONS[i - 1][0] if i > 0 else None
        nextf = SECTIONS[i + 1][0] if i < len(SECTIONS) - 1 else None
        nav = NAV_LABEL
        if prevf: nav += f"　·　[⬅️ 上一篇]({prevf})"
        if nextf: nav += f"　·　[下一篇 ➡️]({nextf})"
        content = (
            f"---\ntitle: {title}\ndescription: {desc}\nkeywords: {kw}\n---\n\n"
            f"> {nav}\n\n---\n\n{body}\n\n---\n\n> {nav}\n"
        )
        open(os.path.join(ROOT, OUT, fname), "w", encoding="utf-8").write(content)
        print(f"  ✓ {fname} ({len(content)} 字符)")

    index = f"""---
title: {INDEX_TITLE}
description: {INDEX_DESC}
keywords: {INDEX_KEYWORDS}
---

# {INDEX_H1}

{INDEX_DESC}

| 篇目 | 一句话 |
| :--- | :--- |
""" + "\n".join(
        f"| **[{t.split(' · ')[0]}]({f})** | {SECTIONS[i][4]} |"
        for i, (f, t, *_r) in enumerate(SECTIONS)
    ) + "\n"
    open(os.path.join(ROOT, OUT, "index.md"), "w", encoding="utf-8").write(index)
    print(f"  ✓ index.md ({len(index)} 字符)")


if __name__ == "__main__":
    main()
