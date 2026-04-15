#!/usr/bin/env python3
"""
课表空课查找统计分析引擎

用法:
    python schedule_analyzer.py <all_weeks.txt> <config.json> <output.md>

输入:
    all_weeks.txt  - pipe 分隔的课表数据 (姓名|星期|大节|周次范围)
    config.json    - 配置文件 (分组定义、周数、阈值等)

输出:
    output.md      - Markdown 格式的分析报告
"""

import json
import re
import sys
from dataclasses import dataclass, field


# ============================================================
# 数据类型定义
# ============================================================

@dataclass
class Config:
    groups: dict[str, list[str]]
    total_weeks: int = 17
    focus_periods: list[str] = field(default_factory=lambda: ['第五大节'])
    golden_threshold: float = 0.88
    title: str = '课表分析报告'
    exclude_weekends: bool = True
    significant_change_threshold: int = 10


DAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
WEEKDAYS = ['周一', '周二', '周三', '周四', '周五']
PERIODS = ['第一大节', '第二大节', '第三大节', '第四大节', '第五大节']

# 课表数据: {姓名: {(星期, 大节): set(周次)}}
Schedule = dict[str, dict[tuple[str, str], set[int]]]


# ============================================================
# 核心函数
# ============================================================

def parse_week_range(s: str) -> set[int]:
    """解析周次范围字符串，返回周次集合。

    支持格式:
        "1-16"       → {1,2,...,16}
        "1-15单"     → {1,3,5,...,15}
        "2-16双"     → {2,4,6,...,16}
        "1-8,10-17"  → {1,2,...,8,10,...,17}
        "1-5,7-15单" → {1,2,...,5,7,9,11,13,15}
    """
    s = s.strip()
    odd_only = '单' in s
    even_only = '双' in s
    s = s.replace('单', '').replace('双', '')

    weeks: set[int] = set()
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            try:
                a, b = part.split('-', 1)
                for w in range(int(a), int(b) + 1):
                    if odd_only and w % 2 == 0:
                        continue
                    if even_only and w % 2 == 1:
                        continue
                    weeks.add(w)
            except ValueError:
                pass
        else:
            try:
                w = int(part)
                if odd_only and w % 2 == 0:
                    continue
                if even_only and w % 2 == 1:
                    continue
                weeks.add(w)
            except ValueError:
                pass
    return weeks


def load_config(config_path: str) -> Config:
    """加载 JSON 配置文件。"""
    with open(config_path, encoding='utf-8') as f:
        data = json.load(f)
    return Config(
        groups=data['groups'],
        total_weeks=data.get('total_weeks', 17),
        focus_periods=data.get('focus_periods', ['第五大节']),
        golden_threshold=data.get('golden_threshold', 0.88),
        title=data.get('title', '课表分析报告'),
        exclude_weekends=data.get('exclude_weekends', True),
        significant_change_threshold=data.get('significant_change_threshold', 10),
    )


def load_schedule_data(filepath: str) -> Schedule:
    """加载 all_weeks.txt，返回课表数据字典。"""
    schedule: Schedule = {}
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '|' not in line:
                continue
            parts = line.split('|')
            if len(parts) < 4:
                continue
            name = parts[0].strip()
            day = parts[1].strip()
            period = parts[2].strip()
            week_str = parts[3].strip()

            if day not in DAYS or period not in PERIODS:
                continue

            if name not in schedule:
                schedule[name] = {}
            key = (day, period)
            if key not in schedule[name]:
                schedule[name][key] = set()
            schedule[name][key].update(parse_week_range(week_str))
    return schedule


def resolve_names(schedule: Schedule, all_members: set[str]) -> tuple[Schedule, list[str]]:
    """模糊匹配姓名，返回修正后的 schedule 和警告列表。"""
    warnings: list[str] = []
    resolved: Schedule = {}
    for name, data in schedule.items():
        if name in all_members:
            resolved[name] = data
        else:
            matched = None
            for m in all_members:
                if name in m or m in name:
                    matched = m
                    break
            if matched:
                warnings.append(f'姓名模糊匹配: "{name}" → "{matched}"')
                if matched in resolved:
                    for key, weeks in data.items():
                        if key not in resolved[matched]:
                            resolved[matched][key] = set()
                        resolved[matched][key].update(weeks)
                else:
                    resolved[matched] = data
            else:
                warnings.append(f'未知成员: "{name}"（未找到匹配）')
                resolved[name] = data
    return resolved, warnings


def validate_extraction(schedule: Schedule, all_members: set[str]) -> list[str]:
    """校验提取数据的完整性，返回警告列表。"""
    warnings: list[str] = []
    found = set(schedule.keys()) & all_members
    missing = all_members - found
    if missing:
        warnings.append(f'以下成员未在数据中找到: {", ".join(sorted(missing))}')

    for name in found:
        entry_count = sum(len(weeks) for weeks in schedule[name].values())
        slot_count = len(schedule[name])
        if slot_count < 10:
            warnings.append(f'"{name}" 仅有 {slot_count} 个时段条目（可能遗漏）')
        elif slot_count > 35:
            warnings.append(f'"{name}" 有 {slot_count} 个时段条目（可能重复）')

    return warnings


def get_free_count(schedule: Schedule, members: list[str], day: str, period: str,
                   week: int) -> tuple[int, list[str]]:
    """计算指定周次、星期、大节的无课人数和有课者名单。"""
    busy = []
    for m in members:
        if m in schedule and (day, period) in schedule[m] and week in schedule[m][(day, period)]:
            busy.append(m)
    return len(members) - len(busy), busy


def get_full_semester_free(schedule: Schedule, members: list[str], day: str,
                           period: str) -> tuple[int, list[str]]:
    """计算全学期视图下的无课人数（任意周有课即算有课）。"""
    busy = []
    for m in members:
        if m in schedule and (day, period) in schedule[m] and len(schedule[m][(day, period)]) > 0:
            busy.append(m)
    return len(members) - len(busy), busy


def compute_full_semester(schedule: Schedule, members: list[str]) -> dict[tuple[str, str], set[str]]:
    """计算全学期视图: 每个 (星期, 大节) 有课的成员集合。"""
    result: dict[tuple[str, str], set[str]] = {}
    for day in DAYS:
        for period in PERIODS:
            busy = set()
            for m in members:
                if m in schedule and (day, period) in schedule[m] and len(schedule[m][(day, period)]) > 0:
                    busy.add(m)
            result[(day, period)] = busy
    return result


def find_golden_slots(schedule: Schedule, members: list[str], config: Config,
                      periods: list[str] | None = None) -> list[tuple[int, str, str, int, list[str]]]:
    """查找黄金时段（无课人数 >= 阈值）。

    返回: [(周次, 星期, 大节, 无课人数, 有课者列表)]
    """
    threshold = int(len(members) * config.golden_threshold)
    target_periods = periods or config.focus_periods
    days_to_check = WEEKDAYS if config.exclude_weekends else DAYS
    golden = []
    for week in range(1, config.total_weeks + 1):
        for day in days_to_check:
            for period in target_periods:
                fc, busy = get_free_count(schedule, members, day, period, week)
                if fc >= threshold:
                    golden.append((week, day, period, fc, busy))
    return golden


def find_significant_changes(schedule: Schedule, members: list[str],
                              config: Config) -> list[tuple[int, str, str, int, int, int]]:
    """查找各周全时段中，无课人数变化显著的时段。

    返回: [(周次, 星期, 大节, 全学期无课, 本周无课, 增加)]
    """
    days_to_check = WEEKDAYS if config.exclude_weekends else DAYS
    changes = []
    for week in range(1, config.total_weeks + 1):
        for period in PERIODS:
            for day in days_to_check:
                fc_full, _ = get_full_semester_free(schedule, members, day, period)
                fc_week, _ = get_free_count(schedule, members, day, period, week)
                diff = fc_week - fc_full
                if diff >= config.significant_change_threshold:
                    changes.append((week, day, period, fc_full, fc_week, diff))
    return changes


def find_diff_weeks(schedule: Schedule, members: list[str],
                    config: Config) -> list[tuple[int, list[tuple[str, str, int, int, int, list[str]]]]]:
    """找出与全学期视图有差异的周次及差异详情。

    返回: [(周次, [(星期, 大节, 全学期无课, 本周无课, 总人数, 多出无课者)])]
    """
    total = len(members)
    full_semester = compute_full_semester(schedule, members)
    result = []

    for week in range(1, config.total_weeks + 1):
        diffs = []
        for day in DAYS:
            for period in PERIODS:
                full_busy = full_semester[(day, period)]
                week_busy = set()
                for m in members:
                    if m in schedule and (day, period) in schedule[m] and week in schedule[m][(day, period)]:
                        week_busy.add(m)
                if week_busy != full_busy:
                    freed = full_busy - week_busy
                    if freed:
                        full_free = total - len(full_busy)
                        week_free = total - len(week_busy)
                        diffs.append((day, period, full_free, week_free, total, sorted(freed)))
        if diffs:
            result.append((week, diffs))

    return result


# ============================================================
# 报告生成
# ============================================================

def generate_report(schedule: Schedule, config: Config) -> str:
    """生成完整的 Markdown 分析报告。"""
    lines: list[str] = []
    all_members_set: set[str] = set()
    for g in config.groups.values():
        all_members_set.update(g)
    all_members = sorted(all_members_set)
    total = len(all_members)

    # 标题
    lines.append(f'# {config.title} 课表分析报告')
    lines.append('')
    lines.append(f'> 共 {total} 人 | {len(config.groups)} 个分组 | {config.total_weeks} 教学周')
    lines.append(f'> 分组: {", ".join(f"{k}({len(v)}人)" for k, v in config.groups.items())}')
    lines.append('')

    # ---- 第一部分: 个人课表摘要 ----
    lines.append('## 一、个人课表摘要')
    lines.append('')
    lines.append('| 姓名 | 有课时段数 | 分组 |')
    lines.append('|------|:---------:|------|')

    member_to_group: dict[str, str] = {}
    for gname, members in config.groups.items():
        for m in members:
            member_to_group[m] = gname

    for name in all_members:
        slot_count = len(schedule.get(name, {}))
        group = member_to_group.get(name, '未分组')
        lines.append(f'| {name} | {slot_count} | {group} |')
    lines.append('')

    # ---- 第二部分: 各组 focus_period 每周表 ----
    lines.append('## 二、重点时段每周无课人数')
    lines.append('')

    group_configs = list(config.groups.items()) + [('全体', all_members)]

    for focus in config.focus_periods:
        lines.append(f'### {focus}')
        lines.append('')

        for gname, gmembers in group_configs:
            if isinstance(gmembers, set):
                gmembers = sorted(gmembers)
            gcount = len(gmembers)
            lines.append(f'#### {gname}（{gcount}人）')
            lines.append('')
            lines.append('| 周次 | 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 |')
            lines.append('|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|')

            for week in range(1, config.total_weeks + 1):
                row = [f'第{week}周']
                for day in DAYS:
                    fc, _ = get_free_count(schedule, gmembers, day, focus, week)
                    if fc == gcount:
                        row.append('⬚')
                    elif fc == 0:
                        row.append('✅')
                    else:
                        row.append(str(fc))
                lines.append('| ' + ' | '.join(row) + ' |')

            lines.append('')
            lines.append(f'> ⬚ = 全员无课({gcount}人)，数字 = 无课人数，✅ = 全员有课')
            lines.append('')

            # 黄金时段
            golden = find_golden_slots(schedule, gmembers, config, [focus])
            threshold_pct = int(config.golden_threshold * 100)
            threshold_count = int(gcount * config.golden_threshold)
            lines.append(f'**{gname}{focus}"黄金时段"（无课>={threshold_count}人，即{threshold_pct}%+）：**')
            lines.append('')

            if golden:
                lines.append('| 周次 | 星期 | 无课人数 | 有课者 |')
                lines.append('|:---:|:---:|:---:|------|')
                for week, day, _, fc, busy in golden:
                    busy_names = '、'.join(sorted(busy)) if busy else '—'
                    lines.append(f'| 第{week}周 | {day} | {fc}/{gcount} | {busy_names} |')
            else:
                lines.append('无')
            lines.append('')

        lines.append('---')
        lines.append('')

    # ---- 第三部分: 按周次的差异分析 ----
    lines.append('## 三、按周次的无课差异分析')
    lines.append('')
    lines.append('> 以下仅展示与"全学期"视图有差异的时段。全学期视图按"只要有任何一周有课就标记有课"统计，')
    lines.append('> 实际上很多课程只开设部分周次，因此特定周的空闲时段会比全学期视图更多。')
    lines.append('')

    for gname, gmembers in group_configs:
        if isinstance(gmembers, set):
            gmembers = sorted(gmembers)
        gcount = len(gmembers)

        diff_weeks = find_diff_weeks(schedule, gmembers, config)
        lines.append(f'### {gname}（{gcount}人）')
        lines.append('')

        if not diff_weeks:
            lines.append(f'所有{config.total_weeks}周的课表情况与全学期视图完全一致，无差异周。')
            lines.append('')
            continue

        lines.append(f'有差异的周: {[w for w, _ in diff_weeks]}')
        lines.append('')

        for week, diffs in diff_weeks:
            lines.append(f'**第{week}周:**')
            lines.append('')
            for day, period, full_free, week_free, _, freed in diffs:
                freed_names = '、'.join(freed)
                lines.append(f'- {day} {period}: 全学期{full_free}/{gcount}无课 → '
                             f'第{week}周{week_free}/{gcount}无课 (多出无课: {freed_names})')
            lines.append('')

    lines.append('---')
    lines.append('')

    # ---- 第四部分: 全时段显著变化 ----
    lines.append('## 四、各周全时段无课人数变化概要')
    lines.append('')
    lines.append(f'> 以下仅列出与全学期视图相比，无课人数增加>={config.significant_change_threshold}人的时段')
    lines.append('')

    significant = find_significant_changes(schedule, all_members, config)
    if significant:
        lines.append(f'| 周次 | 星期 | 大节 | 全学期无课 | 本周无课 | 增加 |')
        lines.append('|:---:|:---:|:---:|:---:|:---:|:---:|')
        for week, day, period, fc_full, fc_week, diff in significant:
            lines.append(f'| 第{week}周 | {day} | {period} | {fc_full}/{total} | {fc_week}/{total} | +{diff} |')
    else:
        lines.append('无显著变化。')
    lines.append('')

    # ---- 第五部分: 建议 ----
    lines.append('## 五、活动安排建议')
    lines.append('')

    all_golden = find_golden_slots(schedule, all_members, config)
    if all_golden:
        lines.append(f'以下时段全体{total}人中无课人数达到{int(config.golden_threshold * 100)}%以上，'
                     f'推荐作为活动/培训时间：')
        lines.append('')
        for week, day, period, fc, busy in all_golden:
            busy_str = f'（有课: {"、".join(sorted(busy))}）' if busy else '（全员无课）'
            lines.append(f'- 第{week}周 {day} {period}: {fc}/{total}人无课 {busy_str}')
    else:
        lines.append(f'未找到全体无课率达到{int(config.golden_threshold * 100)}%的时段，'
                     f'建议降低阈值或按分组安排活动。')
    lines.append('')

    return '\n'.join(lines)


# ============================================================
# CLI 入口
# ============================================================

def main():
    if len(sys.argv) < 4:
        print('用法: python schedule_analyzer.py <all_weeks.txt> <config.json> <output.md>')
        print()
        print('参数:')
        print('  all_weeks.txt  - pipe 分隔的课表数据')
        print('  config.json    - 配置文件 (分组/周数/阈值)')
        print('  output.md      - 输出报告路径')
        sys.exit(1)

    data_path = sys.argv[1]
    config_path = sys.argv[2]
    output_path = sys.argv[3]

    # 加载配置
    print(f'加载配置: {config_path}')
    config = load_config(config_path)

    # 收集所有成员
    all_members_set: set[str] = set()
    for g in config.groups.values():
        all_members_set.update(g)
    print(f'成员总数: {len(all_members_set)}')

    # 加载数据
    print(f'加载数据: {data_path}')
    schedule = load_schedule_data(data_path)
    print(f'数据中识别到 {len(schedule)} 个姓名')

    # 姓名匹配
    schedule, name_warnings = resolve_names(schedule, all_members_set)
    for w in name_warnings:
        print(f'  [NAME] {w}')

    # 完整性校验
    validation_warnings = validate_extraction(schedule, all_members_set)
    for w in validation_warnings:
        print(f'  [WARN] {w}')

    # 生成报告
    print('生成报告...')
    report = generate_report(schedule, config)

    # 写入输出
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f'报告已写入: {output_path}')


if __name__ == '__main__':
    main()
