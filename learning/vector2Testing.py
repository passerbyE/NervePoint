class Node:
    """節點類別，用來儲存 A* 演算法中的節點資訊"""
    def __init__(self, parent=None, position=None):
        self.parent = parent  # 父節點
        self.position = position  # 節點在網格中的位置 (x, y)

        self.g = 0  # 從起點到此節點的實際成本
        self.h = 0  # 從此節點到終點的預估成本 (啟發式)
        self.f = 0  # 總評估值 (g + h)

    # 為了方便比較兩個節點的 f-cost
    def __eq__(self, other):
        return self.position == other.position


def astar(grid, start, end):
    """
    A* 尋路演算法主函數
    :param grid: 2D 陣列，代表地圖。0 表示可通行，1 表示障礙物。
    :param start: 起點座標 (row, col)
    :param end: 終點座標 (row, col)
    :return: 包含路徑座標的 list，如果找不到路徑則返回 None
    """

    # 1. 初始化起點和終點節點
    start_node = Node(None, start)
    end_node = Node(None, end)

    # 2. 初始化 Open List 和 Closed List
    open_list = []
    closed_list = []

    # 將起點加入 Open List
    open_list.append(start_node)

    # 3. 開始主迴圈
    while len(open_list) > 0:

        # a. 尋找 F-cost 最低的節點
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # b. 處理當前節點 (移出 Open List，加入 Closed List)
        open_list.pop(current_index)
        closed_list.append(current_node)

        # c. 檢查是否已到達終點
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # 反轉路徑，從起點到終點

        # d. 探索鄰居
        children = []
        # 定義可能的移動方向 (上下左右)
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # 可加入斜向移動 ( diagonals) e.g., (-1, -1)

            # 取得鄰居節點的座標
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # 確保鄰居在網格範圍內
            if node_position[0] > (len(grid) - 1) or node_position[0] < 0 or \
               node_position[1] > (len(grid[len(grid)-1]) - 1) or node_position[1] < 0:
                continue

            # 確保鄰居是可通行的 (不是障礙物)
            if grid[node_position[0]][node_position[1]] != 0:
                continue

            # 建立新的鄰居節點
            new_node = Node(current_node, node_position)
            children.append(new_node)

        # 處理所有有效的鄰居
        for child in children:

            # 如果鄰居已經在 Closed List 中，忽略它
            if child in closed_list:
                continue

            # 計算 g, h, f 值
            # 這裡簡化處理，每走一步 g-cost 加 1
            child.g = current_node.g + 1
            # 使用曼哈頓距離計算 h-cost
            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
            child.f = child.g + child.h

            # 如果鄰居已經在 Open List 中，且新的路徑 g-cost 更高，則不做任何事
            # (注意：這裡的實作是簡化版，一個更優化的版本會去更新已在 open_list 中的節點)
            is_in_open_list = False
            for open_node in open_list:
                if child == open_node and child.g >= open_node.g:
                    is_in_open_list = True
                    break
            
            if is_in_open_list:
                continue

            # 將合格的鄰居加入 Open List
            open_list.append(child)

    return None # 如果 Open List 空了還沒找到，表示無路可走



def main():
    # 定義地圖: 0 是路, 1 是牆
    grid = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 中間留一個小開口
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]]

    start = (0, 0)
    end = (7, 6)

    path = astar(grid, start, end)
    
    if path:
        print("找到路徑：")
        print(path)
        # 視覺化路徑
        for r, row in enumerate(grid):
            for c, col in enumerate(row):
                if (r, c) == start:
                    print("S ", end="")
                elif (r, c) == end:
                    print("E ", end="")
                elif (r, c) in path:
                    print("* ", end="")
                elif col == 1:
                    print("# ", end="")
                else:
                    print(". ", end="")
            print()
    else:
        print("找不到路徑！")

# 執行主函數
if __name__ == '__main__':
    main()