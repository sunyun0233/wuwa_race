import random
from collections import defaultdict

TRACK_LENGTH = 24  # 修改赛道长度为24步

class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.reached = False
        self.reset()
    
    def reset(self):
        self.position = 0
        self.reached = False
        self.delay_next_turn = False  # 用于长离的延迟标记
    
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
        
        # 检查是否到达终点
        if new_pos >= TRACK_LENGTH:
            return position_stacks[new_pos][-1].name
        return None

    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        steps = self.roll_dice()
        return self.move(steps, position_stacks)

# ------------ 新增选手实现 ------------
class JinXi(Player):
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        winner = super().take_turn(position_stacks, players, is_first, is_last)
        self.check_stack(position_stacks)
        return winner
    
    def check_stack(self, position_stacks):
        current_pos = self.position
        stack = position_stacks.get(current_pos, [])
        if len(stack) > 1 and self in stack:
            # 检查是否不在最上层
            if stack[-1] != self and random.random() < 0.4:
                stack.remove(self)
                stack.append(self)

class ShouAnRen(Player):
    def roll_dice(self):
        return random.choice([2, 3])

class KaKaLuo(Player):
    def take_turn(self, position_stacks, players, is_first=False, is_last=False):
        # 检查最后一名状态
        active_players = [p for p in players if not p.reached]
        if active_players:
            min_pos = min(p.position for p in active_players)
            if self.position == min_pos:
                steps = self.roll_dice() + 3
            else:
                steps = self.roll_dice()
        else:
            steps = self.roll_dice()
        
        return self.move(steps, position_stacks)

class ChangLi(Player):
    def post_move(self, position_stacks):
        current_pos = self.position
        stack = position_stacks.get(current_pos, [])
        # 检查是否在堆叠上方
        if stack and self in stack and stack.index(self) > 0:
            self.delay_next_turn = random.random() < 0.65

# ------------ 模拟逻辑 ------------
def determine_order(active_players, position_stacks):
    # 先随机打乱顺序
    order = active_players.copy()
    random.shuffle(order)
    
    # 处理长离的延迟
    for p in order:
        if isinstance(p, ChangLi) and p.delay_next_turn:
            order.remove(p)
            order.append(p)
            p.delay_next_turn = False  # 重置标记
            break  # 每次只处理一个
    
    return order

def simulate_game(players):
    for p in players:
        p.reset()
    
    position_stacks = defaultdict(list)
    position_stacks[0] = random.sample(players, k=len(players))
    
    while True:
        # 检查终点
        for pos, stack in position_stacks.items():
            if pos >= TRACK_LENGTH and stack:
                return stack[-1].name
        
        active_players = [p for p in players if not p.reached]
        if not active_players:
            break
        
        order = determine_order(active_players, position_stacks)
        
        for idx, player in enumerate(order):
            is_first = (idx == 0)
            is_last = (idx == len(order)-1)
            
            # 执行移动
            winner = player.take_turn(
                position_stacks, 
                players,
                is_first, 
                is_last
            )
            
            # 处理长离的回合后检查
            if isinstance(player, ChangLi):
                player.post_move(position_stacks)
            
            if winner:
                return winner
    
    return None

# ------------ 主程序 ------------
if __name__ == "__main__":
    players = [
        JinXi("今汐"),
        ShouAnRen("守岸人"),
        KaKaLuo("卡卡罗"),
        ChangLi("长离")
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