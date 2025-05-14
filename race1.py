import random
from collections import defaultdict

class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.reached = False
    
    def reset(self):
        self.position = 0
        self.reached = False
    
    def roll_dice(self):
        return random.randint(1, 3)
    
    def take_turn(self, position_stacks, players):
        if self.reached:
            return None
        
        # 基础移动
        dice = self.roll_dice()
        steps = dice
        
        # 处理移动
        winner = self.move(steps, position_stacks)
        return winner
    
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
        
        # 计算新位置
        new_pos = min(current_pos + steps, 20)
        
        # 添加到新位置
        position_stacks[new_pos].extend(moving_group)
        for p in moving_group:
            p.position = new_pos
            if new_pos >= 20:
                p.reached = True
        
        # 检查是否到达终点
        if new_pos >= 20:
            return position_stacks[new_pos][-1]
        return None

class JinXi(Player):
    def after_move(self, position_stacks):
        current_pos = self.position
        stack = position_stacks.get(current_pos, [])
        if self in stack and stack.index(self) < len(stack)-1:
            if random.random() < 0.4:
                stack.remove(self)
                stack.append(self)

class KeLaiTa(Player):
    def take_turn(self, position_stacks, players):
        if self.reached:
            return None
        
        if random.random() < 0.28:
            for _ in range(2):
                dice = self.roll_dice()
                winner = self.move(dice, position_stacks)
                if winner:
                    return winner
                if self.reached:
                    break
                # 今汐技能检查
                if isinstance(self, JinXi):
                    self.after_move(position_stacks)
            return None
        else:
            return super().take_turn(position_stacks, players)

class Chun(Player):
    def take_turn(self, position_stacks, players):
        if self.reached:
            return None
        
        if random.random() < 0.5:
            current_pos = self.position
            stack = position_stacks.get(current_pos, [])
            others = len(stack) - 1
            dice = self.roll_dice()
            steps = dice + others
            return self.move(steps, position_stacks, carry_above=False)
        else:
            return super().take_turn(position_stacks, players)

class ShouAnRen(Player):
    def roll_dice(self):
        return random.choice([2, 3])

class KaKaLuo(Player):
    def take_turn(self, position_stacks, players):
        if self.reached:
            return None
        
        # 检查是否最后一名
        active_players = [p for p in players if not p.reached]
        if not active_players:
            return None
        min_pos = min(p.position for p in active_players)
        extra = 3 if self.position == min_pos else 0
        
        dice = self.roll_dice()
        steps = dice + extra
        return self.move(steps, position_stacks)

class ChangLi(Player):
    pass

def determine_order(players, position_stacks):
    active_players = [p for p in players if not p.reached]
    order = active_players.copy()
    random.shuffle(order)
    
    # 处理长离技能
    changli_players = [p for p in order if isinstance(p, ChangLi)]
    for p in changli_players:
        stack = position_stacks.get(p.position, [])
        if p in stack and stack.index(p) > 0:
            if random.random() < 0.65:
                order.remove(p)
                order.append(p)
                break
    
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
            if pos >= 20 and position_stacks[pos]:
                return position_stacks[pos][-1].name
        
        # 获取存活玩家
        active_players = [p for p in players if not p.reached]
        if not active_players:
            break
        
        # 确定行动顺序
        order = determine_order(active_players, position_stacks)
        
        # 执行回合
        for player in order:
            if player.reached:
                continue
            
            # 执行移动
            winner = player.take_turn(position_stacks, players)
            if winner:
                return winner.name
            
            # 今汐技能检查
            if isinstance(player, JinXi):
                player.after_move(position_stacks)
            
            # 再次检查终点
            for pos in list(position_stacks.keys()):
                if pos >= 20 and position_stacks[pos]:
                    return position_stacks[pos][-1].name
    
    return None

# 初始化选手
players = [
    JinXi("今汐"),
    KeLaiTa("珂莱塔"),
    Chun("椿"),
    ShouAnRen("守岸人"),
    KaKaLuo("卡卡罗"),
    ChangLi("长离")
]

# 模拟参数
simulations = 10000
results = {p.name: 0 for p in players}

# 运行模拟
for _ in range(simulations):
    winner = simulate_game(players)
    if winner:
        results[winner] += 1

# 输出结果
print(f"模拟次数：{simulations}次")
print("胜率统计：")
for name, wins in results.items():
    print(f"{name}: {wins}次 ({wins/simulations*100:.2f}%)")