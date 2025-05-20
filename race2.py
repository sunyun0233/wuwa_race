import random
from collections import defaultdict

class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.reached = False
        self.reset()
    
    def reset(self):
        self.position = 0
        self.reached = False
        self.next_turn_extra = 0  # 用于赞妮的额外步数
        self.has_merged = False   # 用于坎特蕾拉的合并标记
        self.buff_active = False  # 用于卡提希娅的增益状态
        self.has_triggered = False  # 用于卡提希娅的触发标记
    
    def roll_dice(self):
        return random.randint(1, 3)
    
    def move(self, steps, position_stacks, carry_above=True):
        if self.reached:
            return None
        
        current_pos = self.position
        stack = position_stacks.get(current_pos, [])
        if not stack or self not in stack:
            return None
        
        index = stack.index(self)
        moving_group = stack[index:] if carry_above else [self]
        
        # 移除原位置团子
        if carry_above:
            del stack[index:]
        else:
            stack.pop(index)
        if not stack:
            del position_stacks[current_pos]
        
        # 计算新位置
        new_pos = min(current_pos + steps, 24)
        
        # 添加到新位置
        position_stacks[new_pos].extend(moving_group)
        for p in moving_group:
            p.position = new_pos
            if new_pos >= 24:
                p.reached = True
        
        # 检查是否到达终点
        if new_pos >= 24:
            return position_stacks[new_pos][-1].name
        return None

class FeiBi(Player):
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        if self.reached:
            return None
        
        dice = self.roll_dice()
        steps = dice + (1 if random.random() < 0.5 else 0)
        return self.move(steps, position_stacks)

class KaTiXiYa(Player):
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        if self.reached:
            return None
        
        # 基础移动
        dice = self.roll_dice()
        steps = dice + (2 if self.buff_active and random.random() < 0.6 else 0)
        winner = self.move(steps, position_stacks)
        
        # 检查是否触发技能
        if not self.has_triggered and not self.reached:
            active_players = [p for p in players if not p.reached]
            if active_players:
                min_pos = min(p.position for p in active_players)
                if self.position == min_pos:
                    self.buff_active = True
                    self.has_triggered = True
        
        return winner

class Zanni(Player):
    def roll_dice(self):
        return random.choice([1, 3])
    
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        # 应用额外步数
        steps = self.roll_dice() + self.next_turn_extra
        self.next_turn_extra = 0
        
        winner = self.move(steps, position_stacks)
        
        # 检查堆叠状态
        current_pos = self.position
        stack = position_stacks.get(current_pos, [])
        if len(stack) > 1 and self in stack:
            if random.random() < 0.4:
                self.next_turn_extra = 2
        
        return winner

class KanTeLeiLa(Player):
    def move(self, steps, position_stacks, carry_above=True):
        if self.reached or self.has_merged:
            return super().move(steps, position_stacks, carry_above)
        
        current_pos = self.position
        original_stack = position_stacks.get(current_pos, [])
        if not original_stack or self not in original_stack:
            return None
        
        index = original_stack.index(self)
        moving_group = original_stack[index:]
        del original_stack[index:]
        if not original_stack:
            del position_stacks[current_pos]
        
        new_pos = current_pos
        remaining_steps = steps
        merged = False
        
        while remaining_steps > 0 and new_pos < 24:
            new_pos += 1
            remaining_steps -= 1
            if not merged and position_stacks.get(new_pos, []):
                # 合并堆叠
                target_stack = position_stacks[new_pos]
                moving_group.extend(target_stack)
                del position_stacks[new_pos]
                merged = True
                self.has_merged = True
        
        final_pos = min(new_pos, 24)
        position_stacks[final_pos].extend(moving_group)
        for p in moving_group:
            p.position = final_pos
            if final_pos >= 24:
                p.reached = True
        
        if final_pos >= 24:
            return position_stacks[final_pos][-1].name
        return None

    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        if self.reached:
            return None
        dice = self.roll_dice()
        return self.move(dice, position_stacks)

class BuLanTe(Player):
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        if self.reached:
            return None
        
        dice = self.roll_dice()
        steps = dice + (2 if is_first else 0)
        return self.move(steps, position_stacks)

class LuoKeKe(Player):
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        if self.reached:
            return None
        
        dice = self.roll_dice()
        steps = dice + (2 if is_last else 0)
        return self.move(steps, position_stacks)

def determine_order(players, position_stacks):
    active_players = [p for p in players if not p.reached]
    order = active_players.copy()
    random.shuffle(order)
    return order

def simulate_game(players):
    for p in players:
        p.reset()
    
    position_stacks = defaultdict(list)
    position_stacks[0] = players.copy()
    random.shuffle(position_stacks[0])
    
    for p in players:
        p.position = 0
    
    while True:
        # 检查是否有人到达终点
        for pos in list(position_stacks.keys()):
            if pos >= 24 and position_stacks[pos]:
                return position_stacks[pos][-1].name
        
        active_players = [p for p in players if not p.reached]
        if not active_players:
            break
        
        order = determine_order(active_players, position_stacks)
        
        for index, player in enumerate(order):
            is_first = (index == 0)
            is_last = (index == len(order)-1)
            winner = player.take_turn(position_stacks, players, is_first, is_last)
            if winner:
                return winner
    
    return None

# 初始化B组选手
players = [
    FeiBi("菲比"),
    KaTiXiYa("卡提希娅"),
    Zanni("赞妮"),
    KanTeLeiLa("坎特蕾拉"),
    BuLanTe("布兰特"),
    LuoKeKe("洛可可")
]

# 模拟参数
simulations = 100000 # 模拟次数
results = {p.name: 0 for p in players}

# 运行模拟
for _ in range(simulations):
    winner = simulate_game(players)
    if winner:
        results[winner] += 1

# 输出结果
print(f"模拟次数：{simulations}次")
print("胜率统计：")
for name, wins in sorted(results.items(), key=lambda x: x[1], reverse=True):
    print(f"{name}: {wins}次 ({wins/simulations*100:.2f}%)")