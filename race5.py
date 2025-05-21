import random
from collections import defaultdict

TRACK_LENGTH = 24  # 24步赛道

class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.reached = False
        self.reset()
    
    def reset(self):
        self.position = 0
        self.reached = False
        self.next_turn_extra = 0  # 用于赞妮
    
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
        new_pos = min(current_pos + steps, TRACK_LENGTH)
        
        # 添加到新位置
        position_stacks[new_pos].extend(moving_group)
        for p in moving_group:
            p.position = new_pos
            if new_pos >= TRACK_LENGTH:
                p.reached = True
        
        if new_pos >= TRACK_LENGTH:
            return position_stacks[new_pos][-1].name
        return None

# ========= 选手实现 =========
class ShouAnRen(Player):
    def roll_dice(self):
        return random.choice([2, 3])
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        steps = self.roll_dice()
        return self.move(steps, position_stacks)

class KaKaLuo(Player):
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        active_players = [p for p in players if not p.reached]
        min_pos = min(p.position for p in active_players) if active_players else 0
        
        steps = self.roll_dice()
        if self.position == min_pos:
            steps += 3
        
        return self.move(steps, position_stacks)

class Zanni(Player):
    def roll_dice(self):
        return random.choice([1, 3])
    
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        steps = self.roll_dice() + self.next_turn_extra
        self.next_turn_extra = 0  # 重置
        
        winner = self.move(steps, position_stacks)
        
        # 检查堆叠状态
        if not self.reached:
            stack = position_stacks.get(self.position, [])
            if len(stack) > 1 and self in stack:
                if random.random() < 0.4:
                    self.next_turn_extra = 2
        
        return winner

class BuLanTe(Player):
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        steps = self.roll_dice() + (2 if is_first else 0)
        return self.move(steps, position_stacks)

# ========= 模拟逻辑 =========
def determine_order(active_players):
    order = active_players.copy()
    random.shuffle(order)
    return order

def simulate_game(players):
    for p in players:
        p.reset()
    
    position_stacks = defaultdict(list)
    position_stacks[0] = random.sample(players, len(players))
    
    while True:
        # 检查终点
        for pos, stack in position_stacks.items():
            if pos >= TRACK_LENGTH and stack:
                return stack[-1].name
        
        active_players = [p for p in players if not p.reached]
        if not active_players:
            break
        
        order = determine_order(active_players)
        
        for idx, player in enumerate(order):
            winner = player.take_turn(
                position_stacks,
                players,
                is_first=(idx == 0),
                is_last=(idx == len(order)-1)
            )
            if winner:
                return winner
    
    return None

if __name__ == "__main__":
    players = [
        ShouAnRen("守岸人"),
        KaKaLuo("卡卡罗"),
        Zanni("赞妮"),
        BuLanTe("布兰特")
    ]
    
    simulations = 10000
    results = defaultdict(int)
    
    for _ in range(simulations):
        if winner := simulate_game(players):
            results[winner] += 1
    
    print(f"模拟次数：{simulations}次")
    print("胜率统计：")
    for name, wins in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"{name}: {wins}次 ({wins/simulations*100:.2f}%)")